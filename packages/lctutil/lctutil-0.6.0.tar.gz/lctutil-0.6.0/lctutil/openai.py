
from typing import List
import os, openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

proxy = "socks5://127.0.0.1:1080"
openai.proxy = {"http": proxy, "https": proxy}

_apikeystr = os.getenv("API_KEYS")  or ""
apikeys = _apikeystr.split(";")
api_k_index = 0
openai.api_key = apikeys[api_k_index]
api_k_num = len(apikeys)

def set_api_key_inturn():
    if api_k_num < 2: return
    global api_k_index
    api_k_index = api_k_index % api_k_num
    openai.api_key = apikeys[api_k_index] 
    api_k_index = api_k_index + 1


@retry(wait=wait_random_exponential(min=9, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    set_api_key_inturn()
    if type(texts) == "str": texts = [texts]
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    data = response["data"]  # type: ignore
    return [result["embedding"] for result in data]


@retry(wait=wait_random_exponential(min=9, max=20), stop=stop_after_attempt(3))
def get_chat_completion(
    messages,
    model="gpt-3.5-turbo"  # use "gpt-4" for better results
):
    set_api_key_inturn()
    # call the OpenAI chat completion API with the given messages
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    print(f"Completion: \n{completion}")
    return completion
