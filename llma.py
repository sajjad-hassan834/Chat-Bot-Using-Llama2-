import ollama # type: ignore
def llama2_local_response(message: str) -> str:
    """
    Send a message to the LLaMA 2 model and get the response.
    Args:
        message (str): The input message to send to the model.
    Returns:
        str: The response from the model.
    """
    try:
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": message}])
        print(response)
        return response["message"]["content"]
    except Exception as e:
        return f"An error occurred: {e}"
