import json
from django.conf import settings
from .system_messages import HINT_ONLY_MESSAGE
from .call_llm_clients import call_llm

def dictify_hints(hints):
    """Convert list of hints to dictionary if needed."""
    if isinstance(hints, list):
        return {str(i): h for i, h in enumerate(hints)}
    return hints

def generate_hints(question, answer, pipeline_config):
    """
    Generate hints for a math problem using the specified model.
    
    Args:
        question (str): The math problem
        answer (str): The correct answer
        pipeline_config (dict): Configuration containing provider and model information
            Example: {"provider": "openai", "model": "o3-mini"}
        
    Returns:
        dict: Dictionary of hints
    """
    try:
        # Prepare the input for the model
        input_data = {
            "problem": question,
            "answer": answer
        }
        
        messages = [
            {"role": "system", "content": HINT_ONLY_MESSAGE},
            {"role": "user", "content": json.dumps(input_data)}
        ]
        
        retries = 0
        while True:
            retries += 1
            try:
                result = call_llm(pipeline_config, messages)
                hints = result.get("hints", {})

                if isinstance(hints, list):  # sanitize if needed
                    hints = dictify_hints(hints)

                print(f"\n🧾 Model response (attempt {retries}):", hints)
                if isinstance(hints, dict) and any(h.strip() for h in hints.values()):
                    print(f"✅ Non-empty hint dict received on attempt {retries}")
                    return hints
                else:
                    print(f"❌ Empty or malformed hints on attempt {retries}. Retrying...")
            except Exception as e:
                print(f"⚠️ Hint parsing failed (attempt {retries}): {e}")
                if retries >= 3:  # Limit retries
                    raise Exception(f"Failed to generate valid hints after {retries} attempts: {str(e)}")
        
    except Exception as e:
        raise Exception(f"Error generating hints: {str(e)}") 