import os
import string
import sys
import requests
from bs4 import BeautifulSoup

INDEX_URL = "https://hackropole.fr/fr/index.json"

def find_challenge(url: string) -> dict:
    data = requests.get(INDEX_URL).json()
    
    for chall in data:
        uri = chall.get("uri", "")
        if url == uri or url == f"https://hackropole.fr/fr/{uri}":
            return chall
    return {}

def get_docker_compose_url(challenge_url: string) -> string:
    try:
        response = requests.get(challenge_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        link = soup.find('a', href=lambda x: x and 'docker-compose' in x)
        if link and link.get('href'):
            docker_url = link['href']
            if docker_url.startswith('/'):
                docker_url = 'https://hackropole.fr' + docker_url
            return docker_url
    except Exception as e:
        print(f"Error scraping docker-compose URL: {e}")
    
    return None

def get_challenge_details(challenge_url: string) -> tuple:
    try:
        response = requests.get(challenge_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        author = "Inconnu"
        author_link = None
        
        author_div = soup.find('div', class_='font-monospace') 
        if author_div:
            author = author_div.get_text(strip=True)
            parent_link = author_div.find_parent('a')
            if parent_link and parent_link.get('href'):
                author_link = parent_link['href']
        
        difficulty = "Inconnue"
        stars = soup.find_all('use', href=lambda x: x and 'star-fill' in x)
        if stars:
            difficulty = len(stars)
        else:
            difficulty = "intro"
        
        return {"name": author, "link": author_link}, difficulty
    except Exception as e:
        print(f"Error scraping challenge details: {e}")
    
    return {"name": "Inconnu", "link": None}, "Inconnue"

def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py <url> <directory> (optional) --overwrite (optional)")
        sys.exit(1)

    url = sys.argv[1]
    overwrite = '--overwrite' in sys.argv
    
    directory = None
    for arg in sys.argv[2:]:
        if not arg.startswith('--'):
            directory = arg
            break
    
    if directory:
        print(f"Preparing to download from {url} into directory {directory}")
    else:
        print(f"Preparing to download from {url}")
        print("No directory specified, using first tag of the challenge.")

    challenge = find_challenge(url)
    author, difficulty = get_challenge_details(url)
    
    if not challenge:
        print("Challenge not found in index.")
        print("Please check the URL or add the challenge manually.")
        sys.exit(1)

    print(f"Found challenge: {challenge['title']}, by {author['name']}, difficulty: {difficulty}")

    

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    tag = challenge.get("tags", ["misc"])[0] if challenge.get("tags") else "misc"
    challenge_name = challenge.get("uri", "").rstrip("/").split("/")[-1]
    
    
    directory = directory or challenge_name
    directory = os.path.join(root, tag, directory)
    
    print(f"Using directory: {directory}")
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

    docker_url = get_docker_compose_url(url)
    
    if docker_url:
        print(f"Downloading docker-compose file from {docker_url}...")
        cmd = f"curl {docker_url} -o {directory}/docker-compose.yml"
        os.system(cmd)
    else:
        print("Could not find docker-compose URL on challenge page.")

    print("Setting up writeup.md...")
    writeup_path = os.path.join(directory, "writeup.md")
    
    if os.path.exists(writeup_path) and not overwrite:
        print("writeup.md already exists, avoiding overwrite.")
    else:
        with open(writeup_path, "w", encoding="utf-8") as f:
            f.write(f"# {challenge['title']}\n\n")
            f.write(f"> Titre: {challenge['title']}\n")
            if author['link']:
                f.write(f"> Auteur: [{author['name']}]({author['link']})\n")
            else:
                f.write(f"> Auteur: {author['name']}\n")
            f.write(f"> Difficulté: {difficulty}\n")
            f.write("\n## Description\n\n")
            f.write(f"{challenge['content']}\n")
            f.write("## Objectif\n\n")
            f.write("Décrivez ici l'objectif du challenge.\n\n")
            f.write("## Analyse\n\n")
            f.write("Décrivez ici votre analyse du challenge.\n\n")
            f.write("## Flag\n\n")
            f.write("Indiquez ici le flag une fois trouvé.\n")
        print("writeup.md created successfully.")

    print("Setting up images directory...")
    images_dir = os.path.join(directory, "images")
    
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Created images directory: {images_dir}")
    elif overwrite:
        print(f"images directory already exists, recreating due to --overwrite flag.")
    else:
        print("images directory already exists, avoiding overwrite.")
        
    print("Preparation complete.")
    
    
main()
