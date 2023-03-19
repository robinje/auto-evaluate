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
    contents = repo.get_contents(path)

    for content in contents:
        if content.type == "dir":
            get_files_recursive(repo, content.path)
        else:
            files.append(content)


get_files_recursive(repo, "")


def analyze_code(code):
    max_prompt_tokens = 7000
    max_tokens = 200

    engine = "code-davinci-002"

    def num_tokens_from_string(string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("p50k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens

    num_tokens = num_tokens_from_string(code)

    if num_tokens < max_prompt_tokens:

        response = openai.Completion.create(
            engine=engine,
            prompt=f"Analyze the following Python code snippet for efficiency, potential improvements, code defects, and security vulnerabilities. Please provide specific and actionable details, referencing function names, class names, or line numbers:\n\n{code}\n\nAnalysis:",
            max_tokens=max_tokens,
            n=1,
            temperature=0.5,
        )

        print(response["choices"])

        analysis = response.choices[0].text
        return analysis.strip()
    return ""


def create_issue_summary(analysis):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI language model trained to help users with code analysis and creating GitHub issues.",
            },
            {
                "role": "user",
                "content": f"Based on the following code analysis, provide a summary to create a GitHub issue with an 'Issue Title' and a 'Description':\n\n{analysis}\n\n",
            },
        ],
        max_tokens=250,
        n=1,
        temperature=0.5,
    )

    print(response["choices"])

    message_content = response["choices"][0]["message"]["content"].encode("utf-8").decode("utf-8")
    title_search = re.search(r"Issue Title: (.+)", message_content)
    description_search = re.search(r"Description: (.+)", message_content)

    title = title_search.group(1) if title_search else ""
    description = description_search.group(1) if description_search else ""

    return title, description


def create_github_issue(repo, title, body):
    repo.create_issue(title=title, body=body)


# Analyze each file and create GitHub issues
for file in files:

    # Skip files that are not Python source code
    if not file.name.endswith(".py"):
        continue

    print(file.name)

    code = file.decoded_content.decode("utf-8")
    analysis = analyze_code(code)

    if "defect" in analysis.lower() or "improvement" in analysis.lower():
        issue_title, issue_description = create_issue_summary(analysis)

        print(f"Issue title: {issue_title}")
        print(f"Issue description: {issue_description}")

        create_github_issue(repo, issue_title, f"File: {file.path}\n\n{issue_description}\n\nAnalysis details:\n{analysis}")
    else:
        print("No defects found. No issue created.")
