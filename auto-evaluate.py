import os
import re
import time  # Add this import

import openai
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
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=f"Analyze the following code snippet for inefficient code, code defects, and security vulnerabilities:\n\n{code}\n\nAnalysis:",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    )

    print(response['choices'])  # Updated

    return response.choices[0].text.strip()


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
                "content": f"Based on the following code analysis, provide a summary to create a GitHub issue:\n\n{analysis}\n\n",
            },
        ],
        max_tokens=150,
        n=1,
        temperature=0.5,
    )

    print(response["choices"])

    title = ""
    description = ""
    for message in response['choices'][0]['message']['content'].split("\n"):
        if message.startswith("Title:"):
            title = message.replace("Title:", "").strip()
        elif message.startswith("Description:"):
            description = message.replace("Description:", "").strip()

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

    if analysis:
        issue_title, issue_description = create_issue_summary(analysis)
        create_github_issue(repo, issue_title, f"File: {file.path}\n\n{issue_description}\n\nAnalysis details:\n{analysis}")