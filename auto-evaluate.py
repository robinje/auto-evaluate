import re

import openai
import tiktoken
from github import Github

# Set up your GitHub token
github_token = ""
# Set up your OpenAI API key
openai.api_key = ""

REPO_NAME = ""

# Authenticate and get the repository
g = Github(github_token)
repo = g.get_repo(REPO_NAME)

# Read the contents of the repository
files = []


def get_files_recursive(repo, path):
    """Get all files in a repository recursively."""
    contents = repo.get_contents(path)

    for content in contents:
        if content.type == "dir":
            get_files_recursive(repo, content.path)
        else:
            files.append(content)


get_files_recursive(repo, "")


def analyze_code(code):
    """Analyze the code using GPT-3.5-turbo and return the analysis."""
    max_prompt_tokens = 3000
    max_tokens = 1000

    def num_tokens_from_string(string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens

    num_tokens = num_tokens_from_string(code)

    if num_tokens >= max_prompt_tokens:
        return "The code is too long to analyze."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly skilled AI language model, specifically trained to analyze and review source code. Your expertise includes code optimization, identifying potential improvements, detecting defects, and uncovering security vulnerabilities. Please examine the following source code thoroughly and provide specific, actionable feedback. When possible, include references to function names, class names, variable names, or line numbers to make your suggestions more concrete and easier to follow:",
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


def create_issue_summary(analysis):
    """Create a summary for the GitHub issue based on the analysis."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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

    return title, description


def create_github_issue(repo, title, body):
    """Create a GitHub issue with the given title and body."""
    repo.create_issue(title=title, body=body)


# Analyze each file and create GitHub issues
for file in files:

    print(file.name)

    try:
        code = file.decoded_content.decode("utf-8")
    except AssertionError as err:
        print(f"Assertion Error: {err}")
        continue

    except UnicodeDecodeError as err:
        print(f"Unicode Decode Error: {err}")
        continue

    analysis = analyze_code(code)

    if "defect" in analysis.lower() or "improvement" in analysis.lower():
        issue_title, issue_description = create_issue_summary(analysis)

        print(f"Issue title: {issue_title}")
        print(f"Issue description: {issue_description}")

        create_github_issue(repo, issue_title, f"File: {file.path}\n\n{issue_description}\n\nAnalysis details:\n{analysis}")
    else:
        print("No defects found. No issue created.")
