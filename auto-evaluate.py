import re

import openai # type: ignore
from github import Github # type: ignore

from api.constants import SMALL_GPT_MODEL, GITHUB_TOKEN, REPO_NAME, OPEN_AI_API_KEY
from api.evaluate import evaluate_module


# Set up your OpenAI API key
openai.api_key = OPEN_AI_API_KEY


# Authenticate and get the repository
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Read the contents of the repository
files = []


def get_files_recursive(repo, path):
    """Get all files in a repository recursively."""
    files = []
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            files.extend(get_files_recursive(repo, content.path))
        else:
            files.append(content)
    return files


def create_issue_summary(analysis):
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


def create_github_issue(repo, title, body):
    """Create a GitHub issue with the given title and body."""
    repo.create_issue(title=title, body=body)


# Analyze each file and create GitHub issues
files = get_files_recursive(repo, "")

for file in files:
    try:
        print(file.name)
        code: str = file.decoded_content.decode("utf-8")
        analysis = evaluate_module(code, OPEN_AI_API_KEY)

        if "defect" in analysis.lower() or "improvement" in analysis.lower():
            issue_title, issue_description = create_issue_summary(analysis)

            print(f"Issue title: {issue_title}")
            print(f"Issue description: {issue_description}")

            create_github_issue(repo, issue_title, f"File: {file.path}\n\n{issue_description}\n\nAnalysis details:\n{analysis}")
        else:
            print("No defects found. No issue created.")
    except Exception as err:
        print(f"An error occurred while processing the file {file.name}: {err}")
        continue
