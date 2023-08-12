import tiktoken # type: ignore
import openai # type: ignore

from api.constants import SMALL_GPT_MODEL, SMALL_TOKENS, LARGE_GPT_MODEL, LARGE_TOKENS, PERSONALITY





def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def evaluate_module(code: str, open_ai_key: str):
    """Analyze the module using GPT-3.5-turbo and return an analysis."""
    openai.api_key = open_ai_key

    max_prompt_tokens = LARGE_TOKENS
    max_tokens = SMALL_TOKENS

    num_tokens = num_tokens_from_string(code)

    if num_tokens >= max_prompt_tokens:
        return "The code is too long to analyze."

    try:
        response = openai.ChatCompletion.create(
            model=LARGE_GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": PERSONALITY,
                },
                {"role": "user", "content": f"Review the following code: {code}",}
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.4,
        )
    except openai.error.APIConnectionError as err:
        print(f"OpenAI Connection Error: {err}")
        return "OpenAI Connection Error"
    
    except openai.error.Timeout as err:
        print(f"OpenAI Timeout Error: {err}")
        return "OpenAI Timeout Error"

    except openai.error.APIError as err:
        print(f"OpenAI API Error: {err}")
        return "OpenAI API Error"

    analysis = response.choices[0].message["content"].strip()
    return analysis

def evaluate_function(code: str, open_ai_key: str):
    """Analyze the function using GPT-4 and return an analysis."""
    openai.api_key = open_ai_key

    max_prompt_tokens = SMALL_TOKENS
    max_tokens = SMALL_TOKENS

    num_tokens = num_tokens_from_string(code)

    if num_tokens >= max_prompt_tokens:
        return "The code is too long to analyze."

    try:
        response = openai.ChatCompletion.create(
            model=SMALL_GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": PERSONALITY,
                },
                {"role": "user", "content": f"Review the following code: {code}",}
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.4,
        )
    except openai.error.APIConnectionError as err:
        print(f"OpenAI Connection Error: {err}")
        return "OpenAI Connection Error"
    
    except openai.error.Timeout as err:
        print(f"OpenAI Timeout Error: {err}")
        return "OpenAI Timeout Error"

    except openai.error.APIError as err:
        print(f"OpenAI API Error: {err}")
        return "OpenAI API Error"

    analysis = response.choices[0].message["content"].strip()
    return analysis