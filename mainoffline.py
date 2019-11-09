from flask import Flask
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from config import *
from lxml import html
import requests
import urllib.request, json


def main():
    userinput = 'csgo chefmarcy'
    if userinput.lower().__contains__('csgo'):
        steam_id =userinput.lower().replace('csgo', '').strip()
        print('STEAM ID[{}]'.format(steam_id))
        cs_go_stats = cs_go_api(steam_id)
        output = ['CSGO STATS:\n']
        if cs_go_stats is not False:
            for stat in cs_go_stats:
                output.append('{}:{}\n'.format(cs_go_stats[stat]['displayName'], cs_go_stats[stat]['displayValue']))
            print(''.join(output))
            return output


def cs_go_api(steam_id):
    steamID64 = get_steam_dict(steam_id)['steamID64']
    print('STEAMID64', steamID64)
    platform = 'steam'
    headers = {'TRN-Api-Key': tracker_key}
    response = requests.get(
            'https://public-api.tracker.gg/v2/csgo/standard/profile/{}/{}'.format(platform, steamID64),
            headers=headers)
    try:
        if response.json()['errors'][0]['code']:
            print(response.json()['errors'][0]['message'])
            return False
    except Exception:
        stats = response.json()['data']['segments'][0]['stats']
        print('STATS:', stats)
        return stats


def get_steam_dict(steam_id):
    tree = html.fromstring(requests.get('https://steamidfinder.com/lookup/{}/'.format(steam_id)).content)
    profile = [i.strip().replace('\n', '').replace(':', '') for i in tree.xpath('//div[@class="panel-body"]/text()')]
    steam_profile_data = [profile[i] for i in range(0, len(profile)) if profile[i] != '']
    links = tree.xpath('//code/a/text()')
    profile_info = tree.xpath('//code/text()')
    steam_profile_dict = {steam_profile_data[0]: profile_info[0],  # steamID
                          steam_profile_data[1]: profile_info[1],  # steamID3
                          steam_profile_data[2]: profile_info[2],  # steamID64
                          steam_profile_data[3]: links[0],  # customURL (../id/steam_id)
                          steam_profile_data[4]: links[1],  # profile (../profiles/steamID64
                          steam_profile_data[5]: profile_info[3],  # profile state
                          steam_profile_data[6]: profile_info[4],  # profile created
                          steam_profile_data[7]: profile_info[5],  # name
                          steam_profile_data[8]: profile_info[6],  # real name
                          steam_profile_data[9]: profile_info[7],  # location
                          }
    print('STEAMPROFILEDICT', steam_profile_dict)
    return steam_profile_dict



main()