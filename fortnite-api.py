from config import tracker_key
import requests


# THIS ONLY WORKS WITH EPIC NAME AND DOES LIFETIME STATS ONLY
def fortnite_api(platform, epic_name):
    url = "https://api.fortnitetracker.com/v1/profile/%s/%s" % (platform, epic_name)
    headers = {
        'TRN-Api-Key': tracker_key
    }

    response = requests.get(url, headers=headers)
    responsejson = response.json()
    print(responsejson)

    response_dict = {
        'Top 5s': responsejson['lifeTimeStats'][0]['value'],
        'Top 3s': responsejson['lifeTimeStats'][1]['value'],
        'Top 10s': responsejson['lifeTimeStats'][3]['value'],
        'Top 25s': responsejson['lifeTimeStats'][5]['value'],
        'Score': responsejson['lifeTimeStats'][6]['value'],
        'Matches Played': responsejson['lifeTimeStats'][7]['value'],
        'Wins': responsejson['lifeTimeStats'][8]['value'],
        'Win Percentage': responsejson['lifeTimeStats'][9]['value'],
        'Kills': responsejson['lifeTimeStats'][10]['value'],
        'K/D': responsejson['lifeTimeStats'][11]['value']
    }

    print response_dict

fortnite_api("psn", "dksilv4")

# Platforms: pc, xbl, psn
