import requests
import json
from datetime import datetime

class GitHubClient:
    
    # vrati json vypis z githubu, ak user alebo repo existuje (tzn. request je uspesny)
    # r = request response, je definovana v jednotlivych volaniach (user info, repos, commits)
    def _handle_response(self, r):
        
        if r.status_code == 200:
            return r.json()
        
        elif r.status_code == 403:
            remaining = r.headers.get('X-RateLimit-Remaining')
            limit = r.headers.get('X-RateLimit-Limit')
            reset_time = int(r.headers.get('X-RateLimit-Reset')) # UNIX timestamp
            
            reset_time_datetime = datetime.fromtimestamp(reset_time) # human-readable time

            print(f"Error: {r.status_code} - Rate limit exceeded")
            print(f"Total limit: {limit}")
            print(f"Remaining requests: {remaining}")
            print(f"Limit resets at: {reset_time_datetime}")
            return None
        
        else:
            print(f"Error: {r.status_code} - {r.json().get('message')}")
            return None

    # vrati user data
    def get_user_info(self, username):
        r = requests.get(f"https://api.github.com/users/{username}")
        return self._handle_response(r)

    # list repozitarov
    def get_repos(self, username):
        r = requests.get(f"https://api.github.com/users/{username}/repos")
        return self._handle_response(r)
    
    # pocet commitov
    def get_repo_commits(self, username, repo):
        r = requests.get(f"https://api.github.com/repos/{username}/{repo}/commits?per_page=100")
        return self._handle_response(r)


# MAIN
if __name__ == "__main__":
    client = GitHubClient()
    
    username = "renekuda38"
    
    user_data = client.get_user_info(username)
    
    if user_data is None:
        print("User does not exists")
        exit()    

    repos = client.get_repos(username)
    
    
    print("=================================")
    print(f"GitHub User: {user_data['login']}")
    print("=================================")
    
    print(f"Name: {user_data['name']}")
    print(f"Followers: {user_data['followers']}")
    print(f"Public repos: {user_data['public_repos']}")
    print()

    
    sorted_repos = sorted(repos, key=lambda repo: repo["stargazers_count"], reverse=True)

    top_5 = sorted_repos[:5]

    for repo in top_5:
        print("Name:", repo["name"])
        print("Stars:", repo["stargazers_count"])
        
        if repo["description"] is not None:
            print("Description:", repo["description"])
        
        commits = client.get_repo_commits(username, repo["name"])
        if commits is not None:
            print(f"Number of commits: {len(commits)} (Commit count is approximate due to pagination limits - Max 100, can be higher)")
        else:
            print("Number of commits: N/A (could not fetch commits)")

        print() # prazdny riadok medzi jednotlivymi repozitarmi
