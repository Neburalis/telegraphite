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


class TelegramClientManager:
    """Manages the Telegram client connection and authentication."""

    def __init__(self, env_path: Optional[str] = None):
        """Initialize the Telegram client manager.

        Args:
            env_path: Path to the .env file. If None, looks in the current directory.
            
        Raises:
            AuthenticationError: If credentials are missing or invalid.
        """
        env_path = env_path or Path(".env")
        load_dotenv(env_path)

        self.bot_token = os.getenv("BOT_TOKEN")
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")

        if self.bot_token:
            logger.info("Using bot token authentication")
            self.api_id = self.api_id or "0"
            self.api_hash = self.api_hash or "0"
        elif not self.api_id or not self.api_hash:
            raise AuthenticationError(
                "Either BOT_TOKEN or (API_ID and API_HASH) must be set in .env file"
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
        logger.info("Starting Telegram client session")
        self.client = TelegramClient("telegraphite_session", self.api_id, self.api_hash)
        if self.bot_token:
            await self.client.start(bot_token=self.bot_token)
        else:
            await self.client.start()
        logger.info("Telegram client session started successfully")
        return self.client

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