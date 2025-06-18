import numpy as np
import requests
from django.conf import settings
from .call_llm_clients import call_llm
from math_agent.models import Problem

EMBEDDING_MODEL = 'text-embedding-3-small'  # or make configurable
SIMILARITY_THRESHOLD = 0.82


def fetch_embedding(text, provider='openai', model=EMBEDDING_MODEL):
    """
    Fetch embedding for the given text using the specified provider/model.
    Updated for openai>=1.0.0
    """
    if provider == 'openai':
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    # Add other providers if needed
    raise NotImplementedError(f"Embedding provider {provider} not implemented.")


def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def find_similar_problems(problem_text, exclude_ids=None, threshold=SIMILARITY_THRESHOLD):
    """
    Given a problem text, fetch its embedding and compare to all existing problems.
    Returns a dict: {problem_id: similarity_score, ...} for all above threshold.
    """
    if exclude_ids is None:
        exclude_ids = []
    embedding = fetch_embedding(problem_text)
    similars = {}
    for prob in Problem.objects.exclude(id__in=exclude_ids).exclude(problem_embedding=None):
        sim = cosine_similarity(embedding, prob.problem_embedding)
        if sim >= threshold:
            similars[prob.id] = sim
    return similars, embedding 