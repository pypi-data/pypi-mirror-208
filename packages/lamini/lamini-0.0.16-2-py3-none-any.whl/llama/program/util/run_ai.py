import requests
import os
from llama.program.util.config import get_config, edit_config
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import llama


def query_run_program(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/llama/run_program")
    return resp


def query_submit_program_to_batch(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/llama/submit_program")
    return resp


def query_submit_finetune_job(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/lamini/train")
    return resp


def query_check_llama_program_status(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/llama/check_program_status")
    return resp


def query_get_llama_program_result(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/llama/get_program_result")
    return resp


def query_cancel_llama_program(params):
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/llama/cancel_program")
    return resp


def query_run_embedding(prompt, config={}):
    params = {"prompt": prompt}
    edit_config(config)
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/inference/embedding")
    return np.reshape(resp.json()["embedding"], (1, -1))


def query_get_models(params, config={}):
    edit_config(config)
    key, url = get_url_and_key()
    resp = powerml_send_query_to_url(params, url, key, "/v1/training/get_models")
    return resp.json()["models"]


def fuzzy_is_duplicate(embedding, reference_embeddings, threshold=0.99):
    if embedding is None:
        return True
    if not reference_embeddings:
        return False
    similarities = [
        cosine_similarity(embedding, reference_embedding)
        for reference_embedding in reference_embeddings
    ]

    most_similar_index = np.argmax(similarities)

    return similarities[most_similar_index] > threshold


def powerml_send_query_to_url(params, url, key, route):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    }
    response = requests.post(url=url + route, headers=headers, json=params)
    if response.status_code == 429:
        raise llama.error.RateLimitError(f"Rate limit error")
    if response.status_code == 401:
        raise llama.error.AuthenticationError(f"Check your api key")
    if response.status_code != 200:
        try:
            description = response.json()
        except BaseException:
            description = response.status_code
        finally:
            raise llama.error.APIError(f"API error {description}")
    return response


def get_url_and_key():
    cfg = get_config()
    environment = os.environ.get("LLAMA_ENVIRONMENT")
    if environment == "LOCAL":
        key = "test_token"
        if "local.key" in cfg:
            key = cfg["local.key"]
        url = "http://localhost:5001"
        if "local.url" in cfg:
            url = cfg["local.url"]
    elif environment == "STAGING":
        key = cfg["staging.key"]
        url = "https://api.staging.powerml.co"
        if "staging.url" in cfg:
            url = cfg["staging.url"]
    else:
        key = cfg["production.key"]
        url = "https://api.powerml.co"
        if "production.url" in cfg:
            url = cfg["production.url"]
    return (key, url)
