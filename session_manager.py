import streamlit as st
from tornado.websocket import WebSocketClosedError
from tornado.iostream import StreamClosedError
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_websocket_errors(func):
    """Decorator to handle WebSocket errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (WebSocketClosedError, StreamClosedError) as e:
            logger.warning(f"WebSocket connection closed: {e}")
            # No need to show error to user as it happens during normal navigation
            return None
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            st.error("An error occurred. Please try again.")
            return None
    return wrapper

