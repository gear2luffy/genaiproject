"""
File upload and download endpoints.

Demonstrates:
- File upload handling
- File streaming/download
- Background file processing
- File validation
"""

import os
import uuid
from pathlib import Path
from typing import Annotated, List

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    BackgroundTasks,
    status,
)
from fastapi.responses import FileResponse, StreamingResponse

from app.models.user import User
from app.dependencies.auth import get_current_active_user
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.common import MessageResponse

logger = get_logger(__name__)

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".doc", ".docx"}
MAX_FILE_SIZE = settings.max_upload_size


def get_upload_dir() -> Path:
    """Get and ensure upload directory exists."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension."""
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    return f"{unique_id}{ext}"


@router.post(
    "/upload",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload File",
    description="Upload a single file. Supported formats: txt, pdf, png, jpg, jpeg, gif, doc, docx."
)
async def upload_file(
    file: Annotated[UploadFile, File(description="File to upload")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks
) -> MessageResponse:
    """
    Upload a single file.
    
    Args:
        file: The file to upload
        current_user: Authenticated user
        background_tasks: Background task queue
        
    Returns:
        MessageResponse: Upload result with file info
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Generate unique filename and save
    unique_filename = generate_unique_filename(file.filename)
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)
    
    # Add background task for file processing (e.g., thumbnail generation)
    background_tasks.add_task(
        process_uploaded_file,
        str(file_path),
        current_user.id
    )
    
    logger.info(
        "File uploaded",
        filename=unique_filename,
        original_name=file.filename,
        size=len(file_content),
        user_id=current_user.id
    )
    
    return MessageResponse(
        message="File uploaded successfully",
        success=True,
        data={
            "filename": unique_filename,
            "original_name": file.filename,
            "size": len(file_content),
            "content_type": file.content_type
        }
    )


@router.post(
    "/upload/multiple",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Multiple Files",
    description="Upload multiple files at once (up to 10 files)."
)
async def upload_multiple_files(
    files: Annotated[List[UploadFile], File(description="Files to upload")],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> MessageResponse:
    """
    Upload multiple files.
    
    Args:
        files: List of files to upload
        current_user: Authenticated user
        
    Returns:
        MessageResponse: Upload results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )
    
    upload_dir = get_upload_dir()
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate
            if not validate_file_extension(file.filename):
                errors.append({"filename": file.filename, "error": "Invalid file type"})
                continue
            
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                errors.append({"filename": file.filename, "error": "File too large"})
                continue
            
            # Save
            unique_filename = generate_unique_filename(file.filename)
            file_path = upload_dir / unique_filename
            
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_name": file.filename,
                "size": len(content)
            })
            
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    logger.info(
        "Multiple files uploaded",
        success_count=len(uploaded_files),
        error_count=len(errors),
        user_id=current_user.id
    )
    
    return MessageResponse(
        message=f"Uploaded {len(uploaded_files)} of {len(files)} files",
        success=len(errors) == 0,
        data={
            "uploaded": uploaded_files,
            "errors": errors
        }
    )


@router.get(
    "/download/{filename}",
    summary="Download File",
    description="Download a file by filename."
)
async def download_file(
    filename: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> FileResponse:
    """
    Download a file.
    
    Args:
        filename: The filename to download
        current_user: Authenticated user
        
    Returns:
        FileResponse: The file download response
    """
    upload_dir = get_upload_dir()
    file_path = upload_dir / filename
    
    # Security check: ensure path is within upload directory
    try:
        file_path = file_path.resolve()
        if upload_dir.resolve() not in file_path.parents and file_path != upload_dir.resolve():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    logger.info(
        "File downloaded",
        filename=filename,
        user_id=current_user.id
    )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get(
    "/stream/{filename}",
    summary="Stream File",
    description="Stream a file (useful for large files or media)."
)
async def stream_file(
    filename: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> StreamingResponse:
    """
    Stream a file for large files or media content.
    
    Args:
        filename: The filename to stream
        current_user: Authenticated user
        
    Returns:
        StreamingResponse: Streaming file response
    """
    upload_dir = get_upload_dir()
    file_path = upload_dir / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    async def file_iterator():
        """Async generator for file streaming."""
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(65536):  # 64KB chunks
                yield chunk
    
    # Determine media type from extension
    ext = Path(filename).suffix.lower()
    media_types = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    
    return StreamingResponse(
        file_iterator(),
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@router.delete(
    "/{filename}",
    response_model=MessageResponse,
    summary="Delete File",
    description="Delete an uploaded file."
)
async def delete_file(
    filename: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> MessageResponse:
    """
    Delete a file.
    
    Args:
        filename: The filename to delete
        current_user: Authenticated user
        
    Returns:
        MessageResponse: Deletion confirmation
    """
    upload_dir = get_upload_dir()
    file_path = upload_dir / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete the file
    os.remove(file_path)
    
    logger.info(
        "File deleted",
        filename=filename,
        user_id=current_user.id
    )
    
    return MessageResponse(
        message=f"File '{filename}' deleted successfully",
        success=True
    )


# Background task functions
async def process_uploaded_file(file_path: str, user_id: int) -> None:
    """
    Process uploaded file in background.
    
    This could include:
    - Generating thumbnails
    - Scanning for viruses
    - Extracting metadata
    - Converting formats
    
    Args:
        file_path: Path to the uploaded file
        user_id: ID of the user who uploaded
    """
    logger.info(
        "Processing uploaded file",
        file_path=file_path,
        user_id=user_id
    )
    # File processing logic would go here
