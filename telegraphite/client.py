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
from telethon.errors import ApiIdInvalidError, AuthKeyError, BotTokenInvalidError

from telegraphite.errors import AuthenticationError

logger = logging.getLogger(__name__)


APP_ID = 2040
APP_HASH = "b18441a1ff607e10a989891a5462e627"


class TelegramClientManager:
    """Manages the Telegram client connection and authentication."""

    def __init__(self, env_path: Optional[str] = None):
        env_path = env_path or Path(".env")
        load_dotenv(env_path)
        self.bot_token = os.getenv("BOT_TOKEN")

        if not self.bot_token:
            logger.error("BOT_TOKEN must be set in the .env file")
            raise AuthenticationError("BOT_TOKEN must be set in the .env file via @BotFather.")

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
            logger.info("Starting Telegram client session")
            self.client = TelegramClient("telegraphite_bot_session", APP_ID, APP_HASH)
            await self.client.start(bot_token=self.bot_token)
            logger.info("Telegram client session started successfully")
            return self.client
        except BotTokenInvalidError as e:
            logger.error(f"Invalid bot token: {e}")
            raise AuthenticationError(f"Invalid bot token: {e}") from e
        except ApiIdInvalidError as e:
            logger.error(f"Telegram API rejected default credentials: {e}")
            raise AuthenticationError(f"Telegram API rejected default credentials: {e}") from e
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