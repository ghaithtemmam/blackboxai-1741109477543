import time
from typing import Optional, Dict, List
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
from config import settings
from models import InstagramAccount
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramClient:
    def __init__(self):
        self.clients: Dict[str, Client] = {}  # Store multiple client instances
        self.login_attempts: Dict[str, int] = {}  # Track login attempts

    def _create_client(self, username: str) -> Client:
        """Create a new Instagram client instance with device settings."""
        client = Client()
        client.set_device_settings(settings.IG_DEVICE_SETTINGS)
        self.clients[username] = client
        return client

    async def login(self, account: InstagramAccount) -> tuple[bool, Optional[str]]:
        """Login to Instagram account with retry mechanism."""
        if account.username in self.login_attempts and self.login_attempts[account.username] >= settings.MAX_RETRIES:
            return False, "Maximum login attempts exceeded"

        try:
            client = self._create_client(account.username)
            client.login(account.username, account.password)
            self.login_attempts[account.username] = 0  # Reset attempts on successful login
            logger.info(f"Successfully logged in as {account.username}")
            return True, None

        except Exception as e:
            self.login_attempts[account.username] = self.login_attempts.get(account.username, 0) + 1
            error_msg = f"Login failed for {account.username}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def send_dm(self, username: str, target_username: str, message: str) -> tuple[bool, Optional[str]]:
        """Send a DM to a target user."""
        if username not in self.clients:
            return False, "Client not logged in"

        client = self.clients[username]
        try:
            # Get user ID from username
            user_id = client.user_id_from_username(target_username)
            
            # Send message
            client.direct_send(message, [user_id])
            
            # Add delay to avoid rate limiting
            time.sleep(settings.DM_DELAY_SECONDS)
            
            logger.info(f"Successfully sent DM to {target_username}")
            return True, None

        except LoginRequired:
            logger.error(f"Login required for {username}")
            return False, "Login required"
        except Exception as e:
            error_msg = f"Failed to send DM to {target_username}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def check_new_messages(self, username: str) -> List[Dict]:
        """Check for new direct messages."""
        if username not in self.clients:
            logger.error(f"Client not logged in for {username}")
            return []

        client = self.clients[username]
        try:
            # Get recent messages from direct inbox
            inbox = client.direct_threads(selected_filter="unread")
            
            messages = []
            for thread in inbox:
                thread_id = thread.id
                thread_messages = client.direct_messages(thread_id, amount=5)  # Get last 5 messages
                
                for msg in thread_messages:
                    if not msg.seen_at:  # If message hasn't been seen
                        messages.append({
                            "thread_id": thread_id,
                            "sender_id": msg.user_id,
                            "text": msg.text,
                            "timestamp": msg.timestamp
                        })
            
            return messages

        except LoginRequired:
            logger.error(f"Login required for {username}")
            return []
        except Exception as e:
            logger.error(f"Error checking messages for {username}: {str(e)}")
            return []

    async def send_auto_reply(self, username: str, thread_id: str, message: str) -> tuple[bool, Optional[str]]:
        """Send an auto-reply message to a specific thread."""
        if username not in self.clients:
            return False, "Client not logged in"

        client = self.clients[username]
        try:
            # Send auto-reply
            client.direct_answer(thread_id, message)
            
            # Add delay to avoid rate limiting
            time.sleep(settings.DM_DELAY_SECONDS)
            
            logger.info(f"Successfully sent auto-reply in thread {thread_id}")
            return True, None

        except LoginRequired:
            logger.error(f"Login required for {username}")
            return False, "Login required"
        except Exception as e:
            error_msg = f"Failed to send auto-reply: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def logout(self, username: str):
        """Logout from Instagram account."""
        if username in self.clients:
            try:
                self.clients[username].logout()
                del self.clients[username]
                logger.info(f"Successfully logged out {username}")
            except Exception as e:
                logger.error(f"Error logging out {username}: {str(e)}")

# Initialize Instagram client instance
instagram_client = InstagramClient()
