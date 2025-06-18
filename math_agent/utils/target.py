import json
from django.conf import settings
from .system_messages import TARGET_MESSAGE
from .call_llm_clients import call_llm

def test_with_target(question, pipeline_config):
    """
    Test a math problem with the target model.
    
    Args:
        question (str): The math problem
        pipeline_config (dict): Configuration containing provider and model information
            Example: {"provider": "openai", "model": "o3-mini"}
        
    Returns:
        str: The model's solution attempt
    """
    try:
        # Prepare the input for the model
        input_data = {
            "problem": question
        }
        
        messages = [
            {"role": "system", "content": TARGET_MESSAGE},
            {"role": "user", "content": json.dumps(input_data)}
        ]
        
        data = call_llm(pipeline_config, messages)
        
        # Extract the answer from the JSON response
        answer = data.get('answer', '')
        
        if not answer:
            raise ValueError("Invalid response: missing answer field")
        
        return answer.strip()
        
    except Exception as e:
        raise Exception(f"Error testing with target model: {str(e)}") 