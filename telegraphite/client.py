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
from telethon.errors import RPCError
from telethon.errors.rpcerrorlist import BotTokenInvalidError

from telegraphite.errors import AuthenticationError

logger = logging.getLogger(__name__)


class TelegramClientManager:
    """Manages the Telegram client connection and authentication."""

    _SESSION = "telegraphite_bot"
    _API_ID = 6
    _API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

    def __init__(self, env_path: Optional[str] = None):
        """Initialize the Telegram client manager.

        Args:
            env_path: Path to the .env file. If None, looks in the current directory.
            
        Raises:
            AuthenticationError: If the bot token is missing.
        """
        env_path = env_path or Path(".env")
        load_dotenv(env_path)
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token:
            logger.error("BOT_TOKEN must be set in the .env file")
            raise AuthenticationError(
                "BOT_TOKEN must be set in the .env file. "
                "Create a bot via @BotFather and copy the token."
            )

        logger.debug(f"Initialized TelegramClientManager with env file: {env_path}")
        self.client = None

    async def start(self):
        """Start the Telegram client session.
        
        Returns:
            The Telegram client instance.
            
        Raises:
            AuthenticationError: If there is an error with Telegram authentication.
        """
        try:
            logger.info("Starting Telegram bot session")
            self.client = TelegramClient(self._SESSION, self._API_ID, self._API_HASH)
            await self.client.start(bot_token=self.bot_token)
            logger.info("Telegram bot session started successfully")
            return self.client
        except BotTokenInvalidError as e:
            logger.error(f"Invalid bot token: {e}")
            raise AuthenticationError(f"Invalid bot token: {e}") from e
        except RPCError as e:
            logger.error(f"Telegram RPC error: {e}")
            raise AuthenticationError(f"Telegram RPC error: {e}") from e
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            raise AuthenticationError(f"Failed to start Telegram bot: {e}") from e

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