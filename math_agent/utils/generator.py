import json
from django.conf import settings
from .system_messages import GENERATOR_MESSAGE
from .call_llm_clients import call_llm

def generate_problem(pipeline_config, taxonomy=None):
    """
    Generate a math problem using the specified model.
    
    Args:
        pipeline_config (dict): Configuration containing provider and model information
            Example: {"provider": "openai", "model": "o3-mini"}
        taxonomy (dict, optional): Dictionary containing subject and topic
        
    Returns:
        tuple: (question, answer)
    """
    try:
        # Prepare the prompt based on taxonomy
        user_prompt = "Generate a new problem as instructed."
        if taxonomy:
            subject = taxonomy.get('subject', '')
            topic = taxonomy.get('topic', '')
            user_prompt = f"Generate a math problem in {subject} under the topic '{topic}'."
        
        messages = [
            {"role": "system", "content": GENERATOR_MESSAGE},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the model using our centralized client
        data = call_llm(pipeline_config, messages)
        
        # Extract question and answer
        question = data.get('problem', '')
        answer = data.get('answer', '')
        
        if not question or not answer:
            raise ValueError("Invalid response: missing problem or answer")
        
        return question, answer
        
    except Exception as e:
        raise Exception(f"Error generating problem: {str(e)}") 