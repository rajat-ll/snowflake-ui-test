import os
from dotenv import load_dotenv
import requests
import json
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from collections import OrderedDict

class HistoryCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        history = session.history.get_strings()
        unique_matches = OrderedDict()  # To preserve order and uniqueness

        for entry in reversed(history):
            if entry.startswith(text):
                unique_matches[entry] = None  # Using None as the value

        for match in unique_matches:
            yield Completion(match, start_position=-len(text))

# Create a PromptSession with file history
session = PromptSession(history=FileHistory('commit_message_history.txt'),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=HistoryCompleter())

def push_first():
    commit_message = session.prompt("Enter commit message: ")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Git push successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Git commands: {e}")
        exit(1)

def get_workflow_id(repo_owner, repo_name, workflow_name, headers):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        workflows = response.json()["workflows"]
        for workflow in workflows:
            if workflow["name"] == workflow_name:
                return workflow["id"]
    return None

def trigger_workflow():
    # Load environment variables from .env file
    load_dotenv()

    # Get environment variables
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
    SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
    SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
    SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    # Ensure the environment variables are set
    if not all([SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, GITHUB_TOKEN]):
        print("Please set your credentials in the .env file.")
        exit(1)

    # GitHub repository details
    REPO_OWNER = "rajat-ll"
    REPO_NAME = "snowflake-ui-test"
    WORKFLOW_NAME = "Deploy App via snowcli"

    # Get workflow ID
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    workflow_id = get_workflow_id(REPO_OWNER, REPO_NAME, WORKFLOW_NAME, headers)
    if not workflow_id:
        print("Workflow not found. Please check the workflow name and its existence in the repository.")
        exit(1)

    # Trigger the GitHub Actions workflow dispatch event
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_id}/dispatches"
    data = {
        "ref": "main",
        "inputs": {
            "snowflake_account": SNOWFLAKE_ACCOUNT,
            "snowflake_user": SNOWFLAKE_USER,
            "snowflake_password": SNOWFLAKE_PASSWORD,
            "snowflake_role": SNOWFLAKE_ROLE
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 204:
        print("Workflow triggered successfully.")
    else:
        print(f"Failed to trigger workflow: {response.status_code}")
        print(response.text)

def main():
    push_first()
    trigger_workflow()

if __name__ == "__main__":
    main()
