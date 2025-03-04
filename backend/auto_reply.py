import asyncio
from typing import Dict, Optional
import logging
from datetime import datetime
from utils.instagram_client import instagram_client
from utils.groq_client import groq_client
from database import db
from models import AutoReplyConfig, Template
from config import settings

logger = logging.getLogger(__name__)

class AutoReplyManager:
    def __init__(self):
        self.is_running: bool = False
        self.active_configs: Dict[str, AutoReplyConfig] = {}
        self.last_check_times: Dict[str, datetime] = {}

    async def start(self):
        """Start the auto-reply background task."""
        self.is_running = True
        logger.info("Starting auto-reply manager")
        while self.is_running:
            try:
                await self._check_new_messages()
                await asyncio.sleep(settings.AUTO_REPLY_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Error in auto-reply loop: {str(e)}")
                await asyncio.sleep(settings.AUTO_REPLY_CHECK_INTERVAL)

    async def stop(self):
        """Stop the auto-reply background task."""
        self.is_running = False
        logger.info("Stopping auto-reply manager")

    async def update_config(self, username: str, config: AutoReplyConfig):
        """Update auto-reply configuration for an account."""
        if config.is_enabled:
            self.active_configs[username] = config
            logger.info(f"Updated auto-reply config for {username}")
        else:
            self.active_configs.pop(username, None)
            logger.info(f"Disabled auto-reply for {username}")

    async def _check_new_messages(self):
        """Check for new messages across all configured accounts."""
        for username, config in self.active_configs.items():
            try:
                # Skip if we checked recently
                now = datetime.now()
                if username in self.last_check_times:
                    time_diff = (now - self.last_check_times[username]).total_seconds()
                    if time_diff < settings.AUTO_REPLY_CHECK_INTERVAL:
                        continue

                # Get new messages
                messages = await instagram_client.check_new_messages(username)
                self.last_check_times[username] = now

                for message in messages:
                    await self._process_message(username, message, config)

            except Exception as e:
                logger.error(f"Error checking messages for {username}: {str(e)}")

    async def _process_message(self, username: str, message: Dict, config: AutoReplyConfig):
        """Process a single message and send auto-reply if needed."""
        try:
            # Check if message matches conditions
            if not self._should_reply(message, config):
                return

            # Get reply template
            template = await self._get_reply_template(config.template_id, message)
            if not template:
                return

            # Send auto-reply
            success, error = await instagram_client.send_auto_reply(
                username,
                message['thread_id'],
                template
            )

            if success:
                logger.info(f"Auto-reply sent successfully in thread {message['thread_id']}")
            else:
                logger.error(f"Failed to send auto-reply: {error}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def _should_reply(self, message: Dict, config: AutoReplyConfig) -> bool:
        """Check if a message should receive an auto-reply based on conditions."""
        try:
            message_text = message.get('text', '').lower()
            
            # Check each condition
            for condition_type, condition_value in config.conditions.items():
                if condition_type == 'contains':
                    if condition_value.lower() not in message_text:
                        return False
                elif condition_type == 'starts_with':
                    if not message_text.startswith(condition_value.lower()):
                        return False
                elif condition_type == 'ends_with':
                    if not message_text.endswith(condition_value.lower()):
                        return False

            return True

        except Exception as e:
            logger.error(f"Error checking reply conditions: {str(e)}")
            return False

    async def _get_reply_template(self, template_id: str, message: Dict) -> Optional[str]:
        """Get and process the reply template."""
        try:
            # Get template from database
            template = db.get_template(template_id)
            if not template:
                logger.error(f"Template {template_id} not found")
                return None

            # If template content starts with "AI:", generate response using Groq
            if template.content.startswith("AI:"):
                # Analyze message intent
                intent_analysis = await groq_client.analyze_message_intent(message.get('text', ''))
                
                # Generate AI response
                response = await groq_client.generate_dm_response(
                    message.get('text', ''),
                    context={
                        'intent_analysis': intent_analysis,
                        'template_guide': template.content[3:]  # Remove "AI:" prefix
                    }
                )
                return response if response else template.content

            # Otherwise return the template content directly
            return template.content

        except Exception as e:
            logger.error(f"Error getting reply template: {str(e)}")
            return None

# Initialize auto-reply manager
auto_reply_manager = AutoReplyManager()
