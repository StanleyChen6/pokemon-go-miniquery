from flask import Flask, render_template, request
import pandas as pd
import requests
import time
import csv

app = Flask(__name__)

def get_pokemon_data(league):

    df = pd.read_csv(f"{league}.csv")
    
    return df['Pokemon'].apply(lambda x: x.split()[0]).tolist()

def fetch_pokemon_image(pokemon_name):

    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")

    if response.status_code == 200:
        return response.json()['sprites']['other']['official-artwork']['front_default']
    return None

def get_species_id(pokemon_name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")
    
    if response.status_code == 200:
        return response.json()['id']
    return None

def get_preevolution(species_number):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{species_number}")

    if response.status_code == 200:
        data = response.json()
        if data['evolves_from_species'] is not None:
            pre_evolution_name = data['evolves_from_species']['name']
            while data['evolves_from_species'] is not None:
                pre_evolution_name = data['evolves_from_species']['name']
                response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{get_species_id(pre_evolution_name)}")
                data = response.json()
            
            return pre_evolution_name
        else:
            return "null"
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    pokemon_set = set() 
    pokemon_list = []
    
    if request.method == 'POST':
        league = request.form.get('league')
        number = int(request.form.get('number', 0))
        
        if number > 0 and number <= 200:
            pokemon_names = get_pokemon_data(league)
            
            i = 0
            rank = 0
            
            while len(pokemon_set) < number:
                name = pokemon_names[i]
                if name is not None: 
                    if name.lower() not in pokemon_set:
                        pokemon_set.add(name.lower())
                        rank += 1
                        image = fetch_pokemon_image(name)
                        id = get_species_id(name)
                        evolution = get_preevolution(id)
                        if evolution is not None and evolution != "null":
                            evolution_image = fetch_pokemon_image(evolution)
                            evolution_id = get_species_id(evolution)
                            pokemon_list.append((name, image, rank, id, str.capitalize(evolution), evolution_image, evolution_id, -1))
                        else:
                            pokemon_list.append((name, image, rank, id, "null", "null", "null", -2))
                i += 1
                # time.sleep(.5)

            #with open("greatleague_out.csv", "w", newline="") as csvfile:
                #writer = csv.writer(csvfile)
                #writer.writerow(["Pokemon", "Image", "Rank", "ID", "Pre-Evolution", "Pre-Evolution Image", "Pre-Evolution ID", "Evolved?"])
                #writer.writerows(pokemon_list)


    return render_template('intex2.html', pokemon_list=pokemon_list)

if __name__ == '__main__':
    app.run(debug=True)