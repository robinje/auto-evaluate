import ast

from api.evaluate import evaluate_module, evaluate_summary, evaluate_function
from api.repo import repo_get_files, repor_create_issue

# Analyze each file and create GitHub issues


def extract_functions_and_classes(code: str):
    """Extracts functions and classes from the given code."""
    tree = ast.parse(code)
    extracted_elements = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = start_line + len(node.body)
            element_code = "\n".join(code.splitlines()[start_line:end_line])
            extracted_elements.append(element_code)

    return extracted_elements


def auto_evaluate() -> None:
    files: list = repo_get_files()

    for file in files:
        try:
            print(file.name)
            code: str = file.decoded_content.decode("utf-8")
            analysis = evaluate_module(code)

            if "defect" in analysis.lower() or "improvement" in analysis.lower():
                # Evaluate individual functions or classes using the small model
                for element_code in extract_functions_and_classes(code):
                    element_analysis = evaluate_function(element_code)

                    if "defect" in element_analysis.lower() or "improvement" in element_analysis.lower():
                        issue_title, issue_description = evaluate_summary(element_analysis)
                        repor_create_issue(
                            issue_title,
                            f"Function/Class: {element_code}\n\n{issue_description}\n\nAnalysis details:\n{element_analysis}",
                        )
            else:
                print("No defects found. No issue created.")
        except Exception as err:
            print(f"An error occurred while processing the file {file.name}: {err}")
            continue


if __name__ == "__main__":
    auto_evaluate()
