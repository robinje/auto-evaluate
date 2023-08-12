import re

import tiktoken  # type: ignore
import openai  # type: ignore

from api.constants import SMALL_GPT_MODEL, SMALL_TOKENS, LARGE_GPT_MODEL, LARGE_TOKENS, PERSONALITY, OPEN_AI_API_KEY

# Set up your OpenAI API key
openai.api_key = OPEN_AI_API_KEY


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def evaluate_module(code: str):
    """Analyze the module using GPT-3.5-turbo and return an analysis."""
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
                {
                    "role": "user",
                    "content": f"Review the following code: \n{code}",
                },
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


def evaluate_function(code: str):
    """Analyze the function using GPT-4 and return an analysis."""
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
                {
                    "role": "user",
                    "content": f"Review the following code: {code}",
                },
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


def evaluate_summary(analysis):
    """Create a summary for the GitHub issue based on the analysis."""
    try:
        response = openai.ChatCompletion.create(
            model=SMALL_GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an advanced AI language model with specialized knowledge in source code analysis and assisting developers in creating meaningful GitHub issues. Your expertise covers various aspects of software development, including code optimization, identifying potential improvements, detecting defects, and uncovering security vulnerabilities in source code. As an AI assistant, you are capable of understanding code analysis results and summarizing them into concise and informative GitHub issues. Your goal is to help developers address code-related concerns efficiently and effectively.",
                },
                {
                    "role": "user",
                    "content": f"Based on the following code analysis, provide a summary to create a GitHub issue with an 'Issue Title' and a 'Description':\n\n{analysis}\n\n Please specify if the issue is a 'defect' or an 'improvement'. Do not provide any other information.",
                },
            ],
            max_tokens=2000,
            n=1,
            temperature=0.4,
        )
    except openai.error.APIConnectionError as err:
        print(f"OpenAI Connection Error: {err}")
        return "", "OpenAI Connection Problem"

    except openai.error.Timeout as err:
        print(f"OpenAI Timeout Error: {err}")
        return "", "OpenAI Timeout Problem"

    except openai.error.APIError as err:
        print(f"OpenAI API Error: {err}")
        return "", "OpenAI API Problem"

    message_content = response["choices"][0]["message"]["content"].encode("utf-8").decode("utf-8")
    title_search = re.search(r"Issue Title: (.+)", message_content)
    description_search = re.search(r"Description: (.+)", message_content)

    title = title_search.group(1) if title_search else ""
    description = description_search.group(1) if description_search else ""

    return title, description  # Simply return the title and description
