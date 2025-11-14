# tools/github_tool.py
import requests

def github_tool(owner, repo):
    """
    Fetch last 5 commits from a GitHub repository.
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        response = requests.get(url, timeout=5)
        commits = response.json()
        if not commits or "message" in commits:
            return f"No commits found or error: {commits.get('message', '')}"
        recent = [f"{c['commit']['author']['name']}: {c['commit']['message']}" for c in commits[:5]]
        return "\n".join(recent)
    except Exception as e:
        return f"Error fetching GitHub commits: {e}"
