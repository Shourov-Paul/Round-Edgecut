from .plugin_action import RoundedRectOutlinePlugin

try:
    RoundedRectOutlinePlugin().register()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to register RoundedRectOutlinePlugin: {e}")
