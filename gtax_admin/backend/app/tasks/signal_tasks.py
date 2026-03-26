"""
Signal generation background tasks.
"""
from app.celery_app import celery_app
from loguru import logger


@celery_app.task(name="app.tasks.signal_tasks.generate_signals")
def generate_signals(symbols: list):
    """Generate trading signals for a list of symbols."""
    import asyncio
    from app.services.ai.decision_engine import ai_decision_engine
    
    logger.info(f"Generating signals for {len(symbols)} symbols...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        signals = loop.run_until_complete(
            ai_decision_engine.generate_bulk_signals(symbols)
        )
        logger.info(f"Generated {len(signals)} signals.")
        return {
            "status": "success",
            "signals": [s.to_dict() for s in signals]
        }
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        loop.close()


@celery_app.task(name="app.tasks.signal_tasks.update_positions")
def update_positions():
    """Update portfolio positions and check stop loss/take profit."""
    import asyncio
    from app.services.trading.trade_executor import trade_executor
    
    logger.info("Updating positions...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            trade_executor.update_and_check_orders()
        )
        logger.info(f"Positions updated. Executed {result['orders_executed']} orders.")
        return result
    except Exception as e:
        logger.error(f"Position update failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        loop.close()
