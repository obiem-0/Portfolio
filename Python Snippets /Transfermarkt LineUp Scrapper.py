import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

URLS = [
    "https://www.transfermarkt.co.uk/spielbericht/index/spielbericht/4095173",
    "https://www.transfermarkt.co.uk/spielbericht/index/spielbericht/4095174"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}

def extract_game_id(url):
    parsed_url = urlparse(url)
    match = re.search(r'(\d+)', parsed_url.path)
    return match.group(1) if match else None

def extract_coordinates(style_str):
    coord_pattern = re.compile(r"top:\s?(?P<y>\d+(\.\d+)?%)?;.*?left:\s?(?P<x>\d+(\.\d+)?%)?")
    match = coord_pattern.search(style_str)
    
    if match:
        y_coord = float(match.group("y").replace('%', ''))
        x_coord = float(match.group("x").replace('%', ''))
        return {"y": y_coord, "x": x_coord}
    return None

def get_player_details(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting team name
    team_div = soup.find('div', class_='unterueberschrift aufstellung-unterueberschrift-mannschaft')
    team_name = None
    if team_div:
        team_link = team_div.find('a', class_='sb-vereinslink')
        if team_link:
            team_name = team_link.text.strip()

    players = []
    containers = soup.find_all('div', class_='aufstellung-spieler-container')
    
    game_id = extract_game_id(url)
    
    for container in containers:
        player = {}
        shirt_number = container.find('div', class_='tm-shirt-number tm-shirt-number--large tm-shirt-number--bordered')
        name_link = container.find('span', class_='aufstellung-rueckennummer-name').find('a')
        
        coordinates = extract_coordinates(container['style'])
        
        if shirt_number:
            player['shirt_number'] = shirt_number.text.strip()
        
        if name_link:
            player['name'] = name_link.text.strip()
            player['profile_link'] = "https://www.transfermarkt.co.uk" + name_link['href']
        
        if coordinates:
            player['coordinates'] = coordinates
        
        if game_id:
            player['game_id'] = game_id
        
        if team_name:
            player['team'] = team_name

        players.append(player)
    
    return players

if __name__ == "__main__":
    all_details = []
    for url in URLS:
        details = get_player_details(url)
        all_details.extend(details)

    for player in all_details:
        print(player)
