from flask import Flask
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from config import *
from lxml import html
import requests
import urllib.request, json

client = Client(account_sid, auth_token)
app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def main():
    response = MessagingResponse()
    print(request.form)
    if request.form['Body'].lower().__contains__('csgo'):
        steam_id = request.form['Body'].lower().replace('csgo', '').strip()
        output = cs_go_api(steam_id)
        response.message(' '.join(output))
    if request.form['Body'].lower().__contains__('apex'):
        apex_id = request.form['Body'].lower().replace('apex', '').strip()
        output = apex_legends_api(apex_id)
        response.message(' '.join(output))
    else:
        response.message("Sorry but i don't seem to understand your request.")
    return str(response)


def cs_go_api(steam_id):
    tree = html.fromstring(requests.get('https://steamidfinder.com/lookup/{}/'.format(steam_id)).content)
    profile = [i.strip().replace('\n', '').replace(':', '') for i in tree.xpath('//div[@class="panel-body"]/text()')]
    steam_profile_data = [profile[i] for i in range(0, len(profile)) if profile[i] != '']
    links = tree.xpath('//code/a/text()')
    profile_info = tree.xpath('//code/text()')
    steam_profile_dict = {
        steam_profile_data[0]: profile_info[0],  # steamID
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
    steamID64 = steam_profile_dict['steamID64']
    platform = 'steam'
    headers = {'TRN-Api-Key': tracker_key}
    response = requests.get(
        'https://public-api.tracker.gg/v2/csgo/standard/profile/{}/{}'.format(platform, steamID64),
        headers=headers)
    print(response.json())
    try:
        if response.json()['errors'][0]['code']:
            output = [response.json()['errors'][0]['message']]
            return output
    except Exception:
        stats = response.json()['data']['segments'][0]['stats']
        output = ["{}'s CSGO STATS:\n".format(steam_profile_dict['name']), '{}\n'.format('-' * 30)]
        for stat in stats:
            output.append('{}: {}\n'.format(stats[stat]['displayName'], stats[stat]['displayValue']))
        print(' '.join(output))
        return output


def apex_legends_api(apex_id):
    platforms = ['origin', 'xbl', 'psn']
    output = []
    for platform in platforms:
        headers = {'TRN-Api-Key': tracker_key}
        response = requests.get(
            'https://public-api.tracker.gg/v2/apex/standard/profile/{}/{}'.format(platform, apex_id),
            headers=headers)
        print(response.json())
        try:
            if response.json()['errors']:
                continue
        except Exception:
            stats = response.json()['data']['segments'][0]['stats']
            output = ["{}'s APEX LEGENDS STATS:\n".format(apex_id.upper()), '{}\n'.format('-' * 40)]
            for stat in stats:
                output.append('{}: {}\n'.format(stats[stat]['displayName'], stats[stat]['displayValue']))
            return output
        return ['{} not found!'.format(apex_id)]


if __name__ == '__main__':
    app.run(debug=True)

# apex_legends_api('YTDKSILV4')
