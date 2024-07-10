import requests

class UselessAPIs:
    def useless_facts(self):
        response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
        return response.json()['text']
    
    def kanye_quote(self):
        response = requests.get("https://api.kanye.rest/")
        return response.json()['quote']
    
    def cat_fact(self):
        response = requests.get("https://catfact.ninja/fact")
        return response.json()['fact']