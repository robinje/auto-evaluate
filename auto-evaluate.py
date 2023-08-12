import ast

from api.constants import SUPPORTED_EXTENSIONS
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

    print(f"Found {len(files)} files in the repository.")

    for file in files:
        try:
            # Extract the file extension and check if it's supported
            file_extension = file.name.split('.')[-1]
            if file_extension not in SUPPORTED_EXTENSIONS:
                print(f"Skipping {file.name}: Unsupported extension.")
                continue

            print(file.name)
            code: str = file.decoded_content.decode("utf-8")
            analysis = evaluate_module(code)
            print(analysis)

            if "defect" in analysis.lower() or "improvement" in analysis.lower():
                # Evaluate individual functions or classes using the small model
                for element_code in extract_functions_and_classes(code):
                    element_analysis = evaluate_function(element_code)
                    print(element_analysis)

                    if "defect" in element_analysis.lower() or "improvement" in element_analysis.lower():
                        issue_title, issue_description = evaluate_summary(element_analysis)
                        repor_create_issue(
                            issue_title,
                            f"Function/Class: {element_code}\n\n{issue_description}\n\nAnalysis details:\n{element_analysis}",
                        )
            else:
                print(analysis)
                print("No defects found. No issue created.")

        except Exception as err:
            print(f"An error occurred while processing the file {file.name}: {err}")
            continue

if __name__ == "__main__":
    auto_evaluate()