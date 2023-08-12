from github import Github  # type: ignore

from api.constants import GITHUB_TOKEN, REPO_NAME

# Authenticate and get the repository
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)


def repo_get_files(path=""):
    """Get all files in a repository recursively."""
    files = []
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            files.extend(repo_get_files(content.path))
        else:
            files.append(content)
    return files


def repor_create_issue(title, body):
    """Create a GitHub issue with the given title and body."""

    print(f"Creating issue: {title}")

    try:
        repo.create_issue(title=title, body=body)
    except Exception as err:
        print(f"An error occurred while creating the issue: {err}")
