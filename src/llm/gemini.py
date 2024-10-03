from src.llm.prompts import system_prompt
from src.llm.models import LLMResponse

def makeLLMRequest(prompt: str, client, response_model=LLMResponse) -> LLMResponse:
    """
    Makes an LLM request using the provided prompt and expects a response of type LLMResponse.
    """
    messages = [{
        'role': 'system',
        'content': system_prompt
    }]
    
    messages.append({
        'role': 'user',
        'content': prompt
    })
    
    # Send request to the LLM
    resp = client.chat.completions.create(
        messages=messages,
        response_model=response_model
    )
    return resp
