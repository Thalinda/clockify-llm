import requests
import os
from dotenv import load_dotenv
from InquirerPy import inquirer
from datetime import datetime
import pytz
from description_generator import generate_description
from git_log_reader import get_todays_git_logs

load_dotenv()

api_key = os.getenv("CLOCKIFY_API_TOKEN")
base_url = os.getenv("API")

def getHeader() -> dict:
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

def get_workspaces():
    response = requests.get(f"{base_url}/workspaces", headers=getHeader())
    response.raise_for_status()
    return response.json()

def get_projects(workspace_id: str):
    response = requests.get(f"{base_url}/workspaces/{workspace_id}/projects", headers=getHeader())
    response.raise_for_status()
    return response.json()

def interactive_add_time_entry():
    # --- Select Workspace ---
    workspaces = get_workspaces()
    if not workspaces:
        print("No workspaces found. Please check your Clockify account or API key.")
        return

    workspace_choices = [{"name": ws["name"], "value": ws["id"]} for ws in workspaces]
    selected_workspace = inquirer.select(
        message="Select your workspace:",
        choices=workspace_choices
    ).execute()

    # --- Select Project ---
    projects = get_projects(selected_workspace)
    if not projects:
        print(f"No projects found in workspace {selected_workspace}.")
        return

    project_choices = [{"name": proj["name"], "value": proj["id"]} for proj in projects]
    selected_project = inquirer.fuzzy(
        message="Select your project:",
        choices=project_choices
    ).execute()

    # --- Description Generation ---
    use_git = inquirer.confirm(message="Use today's git commit messages for description?", default=False).execute()
    if use_git:
        git_logs = get_todays_git_logs()
        info = "\n".join(git_logs) if git_logs else "No commits today."
        print("\nUsing git commit messages:\n", info)
    else:
        info = inquirer.text(message="Enter brief info for description:").execute()

    description = generate_description(info).strip()
    print("\nGenerated description:", description)

    # --- Date Input ---
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    date = inquirer.text(
        message=f"Enter date (YYYY-MM-DD) [default: {today_str}]:",
        default=today_str
    ).execute().strip() or today_str

    # --- Default Time Input (Press Enter for Default) ---
    default_start = "09:00"
    default_end = "17:00"
    start_time_input = inquirer.text(
        message=f"Start time (24h format, default {default_start}):",
        default=default_start
    ).execute().strip() or default_start
    end_time_input = inquirer.text(
        message=f"End time (24h format, default {default_end}):",
        default=default_end
    ).execute().strip() or default_end

    # --- Time Validation ---
    sri_lanka_tz = pytz.timezone("Asia/Colombo")
    try:
        start_local = sri_lanka_tz.localize(
            datetime.strptime(f"{date} {start_time_input}", "%Y-%m-%d %H:%M")
        )
        end_local = sri_lanka_tz.localize(
            datetime.strptime(f"{date} {end_time_input}", "%Y-%m-%d %H:%M")
        )
    except ValueError:
        print("Invalid date/time format. Please use YYYY-MM-DD and HH:MM.")
        return

    if end_local <= start_local:
        print("End time must be after start time.")
        return

    # --- Convert to UTC ---
    start_time_utc = start_local.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_utc = end_local.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Payload ---
    payload = {
        "billable": True,
        "customAttributes": [],
        "customFields": [],
        "description": description,
        "start": start_time_utc,
        "end": end_time_utc,
        "projectId": selected_project,
        "type": "REGULAR"
    }

    # --- API Call ---
    url = f"{base_url}/workspaces/{selected_workspace}/time-entries"
    try:
        response = requests.post(url, headers=getHeader(), json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"❌ Failed to create time entry: {err}")
        print("Response:", response.text)
        return

    print("✅ Time entry created successfully!")

if __name__ == "__main__":
    interactive_add_time_entry()
