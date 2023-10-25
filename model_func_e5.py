import tiktoken
import openai
import os
import torch
from transformers import AutoTokenizer, AutoModel

openai.api_key = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

tokenizer = AutoTokenizer.from_pretrained('models/E5/multilingual-e5-base')
model = AutoModel.from_pretrained('models/E5/multilingual-e5-base')


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(query: str, strings: list[str], model: str, token_budget: int) -> str:
    introduction = 'Используй заданную базу данных для поиска ответа'
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
        {"role": "system", "content": "Ты отвечаешь на вопрос по заданной базе данных"},
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


def model_d(sent):
    with torch.no_grad():
        encoded_input = tokenizer(sent, padding=True, truncation=True, max_length=24, return_tensors='pt')
        model_output = model(**encoded_input)
    return mean_pooling(model_output, encoded_input['attention_mask'])[0].tolist()
