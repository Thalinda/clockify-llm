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
    return response.json()

def get_projects(workspace_id: str):
    response = requests.get(f"{base_url}/workspaces/{workspace_id}/projects", headers=getHeader())
    return response.json()

def interactive_add_time_entry():
 
    workspaces = get_workspaces()
    workspace_choices = [{"name": ws["name"], "value": ws["id"]} for ws in workspaces]
    selected_workspace = inquirer.select(
        message="Select your workspace:",
        choices=workspace_choices
    ).execute()

  
    projects = get_projects(selected_workspace)
    project_choices = [{"name": proj["name"], "value": proj["id"]} for proj in projects]
    selected_project = inquirer.fuzzy(
        message="Select your project:",
        choices=project_choices
    ).execute()


   
    use_git = inquirer.confirm(message="Use today's git commit messages for description?", default=False).execute()
    if use_git:
        git_logs = get_todays_git_logs()
        info = "\n".join(git_logs) if git_logs else "No commits today."
        print("Using git commit messages:", info)
    else:
        info = inquirer.text(message="Enter brief info for description:").execute()

    
    description = generate_description(info)
    print("Generated description:", description)

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    date = inquirer.text(
        message=f"Enter date (YYYY-MM-DD) [default: {today_str}]:",
        default=today_str
    ).execute().strip()

    start_time_input = inquirer.text(message="Start time (24h format, e.g., 13:30):").execute().strip()
    end_time_input = inquirer.text(message="End time (24h format, e.g., 14:45):").execute().strip()

    # Timezone conversion: Sri Lanka → UTC
    sri_lanka_tz = pytz.timezone("Asia/Colombo")
    try:
        start_local = sri_lanka_tz.localize(
            datetime.strptime(f"{date} {start_time_input}", "%Y-%m-%d %H:%M")
        )
        end_local = sri_lanka_tz.localize(
            datetime.strptime(f"{date} {end_time_input}", "%Y-%m-%d %H:%M")
        )
    except ValueError:
        print("Invalid time format. Please use HH:MM format like 13:30.")
        return

    if end_local <= start_local:
        print("End time must be after start time.")
        return

    
    start_time_utc = start_local.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_utc = end_local.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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


    url = f"{base_url}/workspaces/{selected_workspace}/time-entries"
    response = requests.post(url, headers=getHeader(), json=payload)


    if response.status_code == 201:
        print("✅ Time entry created successfully!")
    else:
        print("Failed to create time entry")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    interactive_add_time_entry()
