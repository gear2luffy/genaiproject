"""
Scanner background tasks.
"""
from app.celery_app import celery_app
from loguru import logger


@celery_app.task(name="app.tasks.scanner_tasks.scan_markets")
def scan_markets():
    """Periodic task to scan markets."""
    import asyncio
    from app.services.scanner.market_scanner import market_scanner
    
    logger.info("Running scheduled market scan...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(market_scanner.scan_all())
        logger.info(f"Market scan complete. Found {len(results)} opportunities.")
        return {"status": "success", "count": len(results)}
    except Exception as e:
        logger.error(f"Market scan failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        loop.close()
