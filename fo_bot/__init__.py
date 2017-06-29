import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    #filename='bot_log'
                    )
logger = logging.getLogger(__name__)


__all__ = ['settings', 'freeze', 'bot_states', 'bot_utils', 'logger']
