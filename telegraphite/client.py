"""Client module for TeleGraphite.

This module handles authentication and connection to Telegram using Telethon.
It provides a context manager for managing the Telegram client session.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, AuthKeyError

from telegraphite.errors import AuthenticationError

logger = logging.getLogger(__name__)

# Default API credentials for bot authentication (public values, not tied to user account)
DEFAULT_API_ID = 17349
DEFAULT_API_HASH = "344583e45741c457fe1862106095a5eb"


class TelegramClientManager:
    """Manages the Telegram client connection and authentication."""

    def __init__(self, env_path: Optional[str] = None):
        """Initialize the Telegram client manager.

        Args:
            env_path: Path to the .env file. If None, looks in the current directory.
            
        Raises:
            AuthenticationError: If bot token is missing or invalid.
        """
        # Load environment variables from .env file
        env_path = env_path or Path(".env")
        load_dotenv(env_path)

        # Get bot token (required for bot authentication)
        self.bot_token = os.getenv("BOT_TOKEN")
        
        if not self.bot_token:
            logger.error("BOT_TOKEN must be set in the .env file")
            raise AuthenticationError(
                "BOT_TOKEN must be set in the .env file. "
                "Get it from @BotFather on Telegram"
            )

        # Use default API credentials for bots (not tied to user account)
        api_id_str = os.getenv("API_ID")
        self.api_id = int(api_id_str) if api_id_str else DEFAULT_API_ID
        self.api_hash = os.getenv("API_HASH", DEFAULT_API_HASH)

        logger.debug(f"Initialized TelegramClientManager with bot token (env file: {env_path})")
        self.client = None

    async def start(self):
        """Start the Telegram client session.
        
        Returns:
            The Telegram client instance.
            
        Raises:
            AuthenticationError: If there is an error with Telegram authentication.
        """
        try:
            logger.info("Starting Telegram client session with bot token")
            self.client = TelegramClient("telegraphite_session", self.api_id, self.api_hash)
            await self.client.start(bot_token=self.bot_token)
            logger.info("Telegram client session started successfully")
            return self.client
        except ApiIdInvalidError as e:
            logger.error(f"Invalid API credentials: {e}")
            raise AuthenticationError(f"Invalid API credentials: {e}") from e
        except AuthKeyError as e:
            logger.error(f"Authentication key error: {e}")
            raise AuthenticationError(f"Authentication key error: {e}") from e
        except Exception as e:
            logger.error(f"Error starting Telegram client: {e}")
            raise AuthenticationError(f"Failed to start Telegram client: {e}") from e

    async def stop(self):
        """Stop the Telegram client session."""
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def __aenter__(self):
        """Context manager entry point."""
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        await self.stop()