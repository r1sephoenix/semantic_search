import yaml
import tiktoken
import openai
import torch
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import numpy as np
from pgvector.psycopg2 import register_vector
from postgres_db.connection import create_db_connection

config_dir = Path(__file__).parent.parent.resolve() / 'config'

with open(config_dir / 'config.yml', 'r') as f:
    config_yaml = yaml.safe_load(f)

openai_api_key = config_yaml['openai_api_key']
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

tokenizer = AutoTokenizer.from_pretrained('models/E5/')
model = AutoModel.from_pretrained('models/E5/')


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(query: str, strings: list[str], model: str, token_budget: int) -> str:
    introduction = 'Используй заданные тексты для поиска ответа'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_text = f'\n\ntext:\n"""\n{string}\n"""'
        if (
                num_tokens(message + next_text + question, model=model)
                > token_budget
        ):
            break
        else:
            message += next_text
    return message + question


def ask(query: str, strings: list[str], model: str = GPT_MODEL, token_budget: int = 4096 - 500,
        print_message: bool = False) -> str:
    message = query_message(query, strings, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "Ты отвечаешь на вопрос по данным текстам"},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def e5_embedding(query):
    with torch.no_grad():
        encoded_input = tokenizer(query, padding=True, truncation=True, max_length=24, return_tensors='pt')
        model_output = model(**encoded_input)
    return mean_pooling(model_output, encoded_input['attention_mask'])[0].tolist()


def ada_embedding(query):
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query)
    return query_embedding_response['data'][0]['embedding']


def get_top_similar_texts(query_embedding):
    conn = create_db_connection
    embedding_array = np.array(query_embedding)
    register_vector(conn)
    cur = conn.cursor()
    cur.execute("SELECT content FROM embeddings ORDER BY embedding <=> %s LIMIT 5", (embedding_array,))
    top_docs = cur.fetchall()
    return top_docs
