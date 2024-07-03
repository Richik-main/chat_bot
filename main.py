import requests
from taipy.gui import Gui, State, notify

# make the LLM understand what to do
context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by Google. How can I help you today? "
conversation = {
    "Conversation": ["Who are you?", "Hi! I am FLAN-T5 XXL. How can I help you today?"]
} # this will store the conversation history
current_user_message = ""

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

api_key = "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"
headers = {"Authorization": f"Bearer {api_key}"}

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

def request(state: State, prompt: str) -> str:
    """
    Send a prompt to the HuggingFace API and return the response.

    Args:
        - state: The current state of the app.
        - prompt: The prompt to send to the API.

    Returns:
        The response from the API.
    """
    
    print("Sending payload:", {"inputs": prompt})  # Debugging line to print the payload
    output = query({"inputs": prompt})
    print("API response:", output)  # Debugging line to print the response
    if output:
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output[0]:
            return output[0]["generated_text"]
        else:
            print("Missing 'generated_text' in response")
    return "Sorry, I couldn't generate a response."

def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the conversation.

    Args:
        - state: The current state of the app.
    """
    # Add the user's message to the context
    state.context += f"Human: {state.current_user_message}\n\nAI: "
    # Send the user's message to the API and get the response
    answer = request(state, state.current_user_message).replace("\n", "")
    # Add the response to the context for future messages
    state.context += answer + "\n"
    # Update the conversation
    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message, answer]
    state.conversation = conv
    # Clear the input field
    state.current_user_message = ""
    print("Yo ", state.conv)

page = """
<|{conversation}|table|show_all|width=100%|>
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|>
"""

if __name__ == "__main__":
    Gui(page).run(dark_mode=True, title="Taipy Chat", port=6901)
