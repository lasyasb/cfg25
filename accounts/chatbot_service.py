import google.generativeai as genai
from django.conf import settings
import json

class ChatbotService:
    def __init__(self):
        # Configure the API key
        genai.configure(api_key=settings.GOOGLE_GENERATIVE_AI_API_KEY)
        
        # Initialize the model - using gemini-1.5-flash which is more widely available
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            # Fallback to gemini-1.5-pro if flash is not available
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception:
                # Final fallback to gemini-pro
                self.model = genai.GenerativeModel('gemini-pro')
        
        # System prompt for educational context
        self.system_prompt = """
        You are an educational assistant chatbot designed to help students with their studies. 
        You should:
        1. Provide helpful, accurate, and educational responses
        2. Be encouraging and supportive
        3. Help with homework, study tips, and academic questions
        4. Maintain a friendly and professional tone
        5. If you don't know something, admit it and suggest where to find the information
        6. Focus on educational topics and avoid inappropriate content
        
        You can help with:
        - Math problems and explanations
        - Science concepts
        - Language and grammar
        - Study techniques
        - General academic advice
        - Homework help
        """
    
    def get_response(self, user_message, conversation_history=None):
        """
        Get a response from the AI chatbot
        
        Args:
            user_message (str): The user's message
            conversation_history (list): Previous messages in the conversation
            
        Returns:
            str: The AI's response
        """
        try:
            # Prepare the conversation context
            if conversation_history and len(conversation_history) > 0:
                # Format conversation history for the model
                formatted_history = []
                for msg in conversation_history:
                    role = "user" if msg.message_type == "user" else "assistant"
                    formatted_history.append({
                        "role": role,
                        "parts": [msg.content]
                    })
                
                # Create a chat session with history
                chat = self.model.start_chat(history=formatted_history)
                response = chat.send_message(user_message)
            else:
                # For new conversations, include system prompt
                prompt = f"{self.system_prompt}\n\nStudent: {user_message}\nAssistant:"
                response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"
    
    def validate_message(self, message):
        """
        Validate if the message is appropriate for an educational context
        
        Args:
            message (str): The message to validate
            
        Returns:
            bool: True if appropriate, False otherwise
        """
        # Basic validation - check for inappropriate content
        inappropriate_keywords = [
            'inappropriate', 'offensive', 'harmful', 'dangerous'
        ]
        
        message_lower = message.lower()
        for keyword in inappropriate_keywords:
            if keyword in message_lower:
                return False
        
        return True 