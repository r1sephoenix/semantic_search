import tiktoken
import openai
import os
import multiprocessing

openai.api_key = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


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


def create_emb(query: str, model: str=EMBEDDING_MODEL) -> str:
    return openai.Embedding.create(input=query, engine=model)['data'][0]['embedding']


def cr_emb(search_string, r_dict, run):
    while run.is_set():
        try:
            vec = create_emb(search_string)
            r_dict['vec'] = vec
            run.clear()  # Stop running.
            break
        except:
            pass


