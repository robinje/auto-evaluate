from api.evaluate import evaluate_module, evaluate_summary
from api.repo import repo_get_files, repor_create_issue

# Analyze each file and create GitHub issues

def auto_evaluate() -> None:
    """Analyze each file and create GitHub issues."""
    files: list = repo_get_files()

    for file in files:
        try:
            print(file.name)
            code: str = file.decoded_content.decode("utf-8")
            analysis = evaluate_module(code)

            if "defect" in analysis.lower() or "improvement" in analysis.lower():
                issue_title, issue_description = evaluate_summary(analysis)

                print(f"Issue title: {issue_title}")
                print(f"Issue description: {issue_description}")

                repor_create_issue(issue_title, f"File: {file.path}\n\n{issue_description}\n\nAnalysis details:\n{analysis}")
            else:
                print("No defects found. No issue created.")
        except Exception as err:
            print(f"An error occurred while processing the file {file.name}: {err}")
            continue


if __name__ == "__main__":
    auto_evaluate()
