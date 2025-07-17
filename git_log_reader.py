import subprocess
from datetime import datetime

def get_todays_git_logs(repo_path: str = ".") -> list:
    """
    Reads git commit messages from today's logs in the given repo.
    Returns a list of commit messages.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cmd = [
        "git", "--no-pager", "log", f'--since={today} 00:00', f'--until={today} 23:59', "--pretty=%s"
    ]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.strip().split("\n") if line]

if __name__ == "__main__":
    logs = get_todays_git_logs()
    print("Today's git commit messages:")
    for log in logs:
        print("-", log)
