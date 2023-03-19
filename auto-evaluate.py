import os
import openai
import re
from github import Github

# Set up your GitHub token
github_token = os.environ["GITHUB_TOKEN"]

# Authenticate and get the repository
g = Github(github_token)
repo = g.get_repo("owner/repo_name")

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

# Set up your OpenAI API key
openai.api_key = "YOUR_API_KEY"

def analyze_code(code):
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=f"Analyze the following code snippet for inefficient code, code defects, and security vulnerabilities:\n\n{code}\n\nAnalysis:",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

def create_issue_summary(analysis):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Based on the following code analysis, provide a summary to create a GitHub issue:\n\n{analysis}\n\nIssue summary:",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

def create_github_issue(repo, title, body):
    repo.create_issue(title=title, body=body)

# Analyze each file and create GitHub issues
for file in files:
    # Skip files that are not Python source code
    if not file.name.endswith(".py"):
        continue

    code = file.decoded_content.decode("utf-8")
    analysis = analyze_code(code)

    if analysis:
        issue_summary = create_issue_summary(analysis)
        create_github_issue(repo, issue_summary, f"File: {file.path}\n\n{analysis}")
