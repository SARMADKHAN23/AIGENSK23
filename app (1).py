import gradio as gr
import requests
import os
from urllib.parse import urlparse

class N8NChatbot:
    def __init__(self):
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
        self.history = []
    
    def validate_url(self, url):
        """Validate the webhook URL"""
        if not url:
            return False, "Webhook URL is not configured"
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format"
            return True, "URL is valid"
        except:
            return False, "Invalid URL"
    
    def send_message(self, message):
        """Send message to n8n and get response"""
        # Validate URL first
        is_valid, error_msg = self.validate_url(self.webhook_url)
        if not is_valid:
            return f"Configuration error: {error_msg}. Please check your N8N_WEBHOOK_URL environment variable."
        
        try:
            payload = {
                "message": message,
                "history": self.history[-10:]  # Last 10 messages for context
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                bot_response = response.json().get("response", "No response received")
                self.history.append({"user": message, "bot": bot_response})
                return bot_response
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

# Initialize chatbot
chatbot = N8NChatbot()

def chat_interface(message, history):
    """Gradio chat function"""
    response = chatbot.send_message(message)
    return response

# Create configuration UI
def create_config_ui():
    with gr.Blocks() as config_ui:
        gr.Markdown("## n8n Chatbot Configuration")
        
        with gr.Row():
            webhook_url = gr.Textbox(
                label="n8n Webhook URL",
                value=os.getenv("N8N_WEBHOOK_URL", ""),
                placeholder="https://your-n8n-instance.com/webhook/chatbot",
                lines=1
            )
            test_btn = gr.Button("Test Connection")
        
        test_output = gr.Textbox(label="Connection Test Result", interactive=False)
        
        def test_connection(url):
            if not url:
                return "Please enter a webhook URL"
            
            # Validate URL format
            try:
                result = urlparse(url)
                if not all([result.scheme, result.netloc]):
                    return "❌ Invalid URL format. Please include http:// or https://"
            except:
                return "❌ Invalid URL format"
            
            # Test connection
            try:
                response = requests.post(
                    url,
                    json={"message": "test", "history": []},
                    timeout=10
                )
                if response.status_code == 200:
                    return "✅ Connection successful!"
                else:
                    return f"❌ Connection failed: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ Connection failed: {str(e)}"
        
        test_btn.click(test_connection, inputs=webhook_url, outputs=test_output)
    
    return config_ui

# Main application
with gr.Blocks(title="n8n Agentic AI Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 n8n Agentic AI Chatbot")
    gr.Markdown("Powered by n8n workflow automation and AI integration")
    
    # Check if webhook URL is configured
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    is_valid_url = False
    
    if webhook_url:
        try:
            result = urlparse(webhook_url)
            is_valid_url = all([result.scheme, result.netloc])
        except:
            is_valid_url = False
    
    if not is_valid_url:
        gr.Markdown("""
        ## ⚠️ Configuration Required
        
        Before using the chatbot, you need to:
        
        1. Set up an n8n instance with a webhook workflow
        2. Configure the `N8N_WEBHOOK_URL` environment variable
        3. Or enter your webhook URL below to test the connection
        """)
        
        config_ui = create_config_ui()
        
        gr.Markdown("""
        ### How to get started:
        
        1. **Deploy n8n**: Use [Railway](https://railway.app/template/n8n), [Heroku](https://elements.heroku.com/buttons/n8n-io/n8n), or any cloud provider
        2. **Create a webhook workflow** in n8n
        3. **Get your webhook URL** from the n8n workflow
        4. **Set the environment variable** in Hugging Face Space settings
        """)
    else:
        gr.Markdown("### ✅ Configuration detected! You can start chatting below.")
    
    # Chat interface (only show if configured)
    if is_valid_url:
        chatbot_interface = gr.ChatInterface(
            fn=chat_interface,
            examples=[
                "Hello, how are you?",
                "What can you help me with?",
                "Tell me about n8n",
                "How does this chatbot work?"
            ]
        )
    else:
        gr.Markdown("""
        ---
        *Chat interface will appear here once configured*
        """)

if __name__ == "__main__":
    demo.launch()