import requests
import json
from datetime import datetime

# komunikacia s github api
# trieda obsahuje metody na ziskanie info o pouzivatelovi, jeho repos a commitoch
class GitHubClient:
    
    # vrati json vypis z githubu (slovnik), ak user alebo repo existuje (tzn. request je uspesny)
    # r = request response, je definovana v jednotlivych volaniach metod (get_user_info, get_repos, get_repo_commits)
    def _handle_response(self, r):
        
        # ak je request uspesny
        if r.status_code == 200:
            return r.json() # .json() prevedie JSON string na Python slovnik(dictionary)/list
        
        # ak sa presiahne limit requestov, github vrati status code 403 (forbidden)
        # bez autentifikácie: 60 requestov/hodinu
        # s autentifikáciou: 5000 requestov/hodinu
        elif r.status_code == 403:

            # r.headers = slovník s hlavičkami odpovede (metadata o requeste)
            remaining = r.headers.get('X-RateLimit-Remaining') # kolko requestov ostava
            limit = r.headers.get('X-RateLimit-Limit') # kolko requestov je mozne vykonat za hodinu
            reset_time = int(r.headers.get('X-RateLimit-Reset')) # UNIX timestamp, kedy sa limit resetuje
            
            reset_time_datetime = datetime.fromtimestamp(reset_time) # UNIX to human-readable time

            print(f"Error: {r.status_code} - Rate limit exceeded")
            print(f"Total limit: {limit}")
            print(f"Remaining requests: {remaining}")
            print(f"Limit resets at: {reset_time_datetime}")

            return None
        
        else:
            # r.json().get('message') - ziska error srpavu z JSON odpovede
            print(f"Error: {r.status_code} - {r.json().get('message')}")
            return None

    ### metody - vratia slovnik s udajmi (vykonane v internej metode _handle_response)

        # username - pouzivatelske meno na githube, definovane v maine programu
        # repo - jeden z najdenych repozitarov (slovnik z listu), 
            # kazdy slovnik = 1 repo (name, stars, description, ...)

        # requests.get() = posle HTTP GET request na zadanu URL
        # vrati Response objekt (r), ktory obsahuje napr.:
        #   - r.status_code: ciselny kod odpovede (200, 404, 403, ...)
        #   - r.headers: slovnik s hlavickami (metadata)
        #   - r.json(): metoda na ziskanie JSON dat ako Python slovnika
        #   - r.text: raw text odpovede

        # self = client (client = GitHubClient())
        # self._handle_response(r) - zavolaj _handle_response(r) na konkretnej isntancii (client)

        #?per_page=100 - url param, aby github api vratilo max 100 poloziek (default 30, max 100)
    
    # vrati informacie o pouzivatelovi
    def get_user_info(self, username):
        r = requests.get(f"https://api.github.com/users/{username}")
        return self._handle_response(r)

    # list verejnych repozitarov
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
    
    # vrati slovnik s pouzivatelskymi udajmi
    user_data = client.get_user_info(username)
    
    # ak user neexistuje, status code nebude 200 (uspech)
    if user_data is None:
        print("User does not exists")
        exit()    
    
    print("=================================")
    print(f"GitHub User: {user_data['login']}") # vypise pouzivatelske meno github uctu (maju ho vsetci)
    print("=================================")
    
    print(f"Name: {user_data['name']}") # cele meno uzivatela (nemusi byt definovane)
    print(f"Followers: {user_data['followers']}")
    print(f"Public repos: {user_data['public_repos']}")
    print()

    # vrati list slovnikov (1 slovnik = 1 repo)
    repos = client.get_repos(username)

    # zoradenie repozitarov podla hodnotenia (stars)
        # repos - list, ktory chceme zoradit
        # key - podla coho chceme zoradit
        # repo - ako parameter funkcie
        # repo["stargazers_count"] - co chceme vratit (return)
    sorted_repos = sorted(repos, key=lambda repo: repo["stargazers_count"], reverse=True)

    # list s top 5 hodnotenymi repos
    top_5 = sorted_repos[:5]

    # pre kazdy repo vypiseme info
    for repo in top_5:

        print("Name:", repo["name"])
        print("Stars:", repo["stargazers_count"])
        
        # ak repo nema description, tak ostane prazdne, nevypise sa nic
        if repo["description"] is not None:
            print("Description:", repo["description"])
        
        # vrati commity jednotlivych repozitarov
        # do metody posielame pouzivatelske meno a nazov aktualneho repozitara 
        commits = client.get_repo_commits(username, repo["name"])

        # ak commity existuju, vypise sa ich pocet
        # ak neexistuju, spusti sa vetva else
        if commits is not None:
            print(f"Number of commits: {len(commits)} (Commit count is approximate due to pagination limits - Max 100, can be higher)")
        else:
            print("Number of commits: N/A (could not fetch commits)")

        print() # prazdny riadok medzi jednotlivymi repozitarmi
