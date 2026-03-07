"""
Rate Limiter
Adds human-like delays to avoid bot detection
"""
import random
import asyncio
from datetime import datetime, timedelta
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """Rate limiter with human-like delays"""
    
    def __init__(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """
        Initialize rate limiter
        
        Args:
            min_delay: Minimum delay between actions (seconds)
            max_delay: Maximum delay between actions (seconds)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_action_time = None
        self.action_count = 0
    
    async def wait(self):
        """Wait with human-like random delay"""
        if self.last_action_time:
            # Calculate time since last action
            elapsed = (datetime.now() - self.last_action_time).total_seconds()
            
            # Random delay between min and max
            delay = random.uniform(self.min_delay, self.max_delay)
            
            # Subtract elapsed time
            remaining_delay = max(0, delay - elapsed)
            
            if remaining_delay > 0:
                await asyncio.sleep(remaining_delay)
        
        self.last_action_time = datetime.now()
        self.action_count += 1
        
        # Every 10 actions, take a longer break (simulates human browsing)
        if self.action_count % 10 == 0:
            break_time = random.uniform(3, 7)
            logger.debug(f"💤 Taking human-like break: {break_time:.1f}s")
            await asyncio.sleep(break_time)
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        return {
            'total_actions': self.action_count,
            'last_action': self.last_action_time.isoformat() if self.last_action_time else None
        }
