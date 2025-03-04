import groq
from typing import Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.model = "mixtral-8x7b-32768"  # Default model

    async def generate_dm_response(self, message_content: str, context: Dict = None) -> Optional[str]:
        """
        Generate a response for a DM using Groq's AI model.
        
        Args:
            message_content: The content of the received DM
            context: Additional context for response generation (optional)
        
        Returns:
            Generated response text or None if generation fails
        """
        try:
            # Prepare the prompt with context
            prompt = self._prepare_prompt(message_content, context)
            
            # Generate response
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful Instagram DM assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract and return the generated response
            if chat_completion.choices and len(chat_completion.choices) > 0:
                return chat_completion.choices[0].message.content.strip()
            return None

        except Exception as e:
            logger.error(f"Error generating response with Groq: {str(e)}")
            return None

    async def analyze_message_intent(self, message_content: str) -> Optional[Dict]:
        """
        Analyze the intent of a received message using Groq's AI model.
        
        Args:
            message_content: The content of the received DM
        
        Returns:
            Dictionary containing intent analysis or None if analysis fails
        """
        try:
            prompt = f"""
            Analyze the following message and determine:
            1. Primary intent (question, complaint, inquiry, etc.)
            2. Sentiment (positive, negative, neutral)
            3. Key topics mentioned
            4. Priority level (high, medium, low)

            Message: {message_content}

            Provide the analysis in JSON format.
            """

            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a message analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            if chat_completion.choices and len(chat_completion.choices) > 0:
                return eval(chat_completion.choices[0].message.content.strip())
            return None

        except Exception as e:
            logger.error(f"Error analyzing message intent with Groq: {str(e)}")
            return None

    async def generate_template_suggestions(self, business_type: str, purpose: str) -> Optional[Dict]:
        """
        Generate DM template suggestions based on business type and purpose.
        
        Args:
            business_type: Type of business (e.g., "ecommerce", "service", "influencer")
            purpose: Purpose of the template (e.g., "welcome", "follow-up", "promotion")
        
        Returns:
            Dictionary containing template suggestions or None if generation fails
        """
        try:
            prompt = f"""
            Generate 3 professional Instagram DM templates for a {business_type} business.
            Purpose: {purpose}
            
            Include variables like {{name}}, {{username}}, etc. where appropriate.
            Provide templates in JSON format with 'casual', 'professional', and 'friendly' variations.
            """

            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional copywriting assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            if chat_completion.choices and len(chat_completion.choices) > 0:
                return eval(chat_completion.choices[0].message.content.strip())
            return None

        except Exception as e:
            logger.error(f"Error generating template suggestions with Groq: {str(e)}")
            return None

    def _prepare_prompt(self, message_content: str, context: Dict = None) -> str:
        """
        Prepare a prompt for the AI model with appropriate context.
        """
        base_prompt = f"Message: {message_content}\n\n"
        
        if context:
            if 'previous_messages' in context:
                base_prompt += f"Previous conversation: {context['previous_messages']}\n"
            if 'customer_info' in context:
                base_prompt += f"Customer info: {context['customer_info']}\n"
            if 'business_context' in context:
                base_prompt += f"Business context: {context['business_context']}\n"
        
        base_prompt += "\nGenerate a professional and engaging response:"
        return base_prompt

# Initialize Groq client
groq_client = GroqClient()
