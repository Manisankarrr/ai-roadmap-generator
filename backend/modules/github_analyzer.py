import os
import requests
from dotenv import load_dotenv

# Load environment variables to get access to the new GITHUB_TOKEN
load_dotenv()

def analyze_github_profile(github_url: str) -> str:
    """
    Fetches and summarizes public repository data from a GitHub user's profile
    using an authenticated API request to increase the rate limit.
    """
    try:
        username = github_url.strip().rstrip('/').split('/')[-1]
        if not username:
            raise ValueError("Could not extract a valid username from the provided URL.")
        
        api_url = f"https://api.github.com/users/{username}/repos"
        params = {'sort': 'pushed', 'per_page': 7}
        
        # --- THIS IS THE KEY UPGRADE ---
        # We now create an authentication header to send our token.
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {
            'Authorization': f'token {github_token}'
        } if github_token else {}
        
        # We pass the headers with our request.
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        
        repos = response.json()
        
        if not repos:
            return "No public repositories found for this user."

        languages = {repo["language"] for repo in repos if repo.get("language")}
        
        summary = f"Key Languages Used:\n- {', '.join(languages) if languages else 'N/A'}\n\n"
        
        summary += "Recent Projects Summary:\n"
        for repo in repos:
            summary += (f"- Project: {repo.get('name', 'N/A')} "
                        f"(Language: {repo.get('language', 'N/A')})\n  "
                        f"Description: {repo.get('description', 'No description.')}\n")
            
        return summary

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"GitHub user '{username}' not found. Please check the URL.")
        else:
            raise ConnectionError(f"GitHub API error: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

