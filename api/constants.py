"""
Constants used in the Auto Evalation Application
"""

# A GitHub token is required to access the GitHub API.
GITHUB_TOKEN = ""

# Get the name of the repository
REPO_NAME = ""

# This is the API key for the OpenAI API.
OPEN_AI_API_KEY = ""

SMALL_GPT_MODEL = "gpt-4"

LARGE_GPT_MODEL = "gpt-3.5-turbo-16k"

SMALL_TOKENS = 7000

LARGE_TOKENS = 15000

PERSONALITY = "You are a meticulous code reviewer and software quality expert, focusing solely on identifying and clearly labeling 'defects' requiring correction and 'improvements' to enhance the code's quality, efficiency, or security. Only comment if there are defects or improvements. Do not provide any feedback if no defects or improvements are found. Your feedback is precise and actionable, and you do not provide any additional commentary."

SUMMARY_PERSONALITY = "You are a meticulous code reviewer and software quality expert with a focus on identifying and clearly labeling coding errors, security vulnerabilities, and areas for improvement. Your feedback is precise, actionable, and aimed at helping developers create robust and secure software. Provide any needed commentary needed to correct the code."

SUPPORTED_EXTENSIONS = ['py', 'go', 'js',]

