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
    valid = False
    if request.form['Body'].lower().__contains__('csgo'):
        valid = True
        steam_id = request.form['Body'].lower().replace('csgo', '').strip()
        output = cs_go_api(steam_id)
        response.message(' '.join(output))
    if request.form['Body'].lower().__contains__('apex'):
        valid = True
        apex_id = request.form['Body'].lower().replace('apex', '').strip()
        platform = 'psn'
        if request.form['Body'].lower().__contains__('xbl'):
            platform = 'xbx'
            apex_id = apex_id.replace('xbx', '').strip()
        if request.form['Body'].lower().__contains__('pc'):
            platform = 'pc'
            apex_id = apex_id.replace('pc', '').strip()
        else:
            apex_id = apex_id.replace('psn', '').strip()
        output = apex_legends_api(platform, apex_id)
        response.message(' '.join(output))
    if request.form['Body'].lower().__contains__('bo4'):
        valid = True
        bo4_id = request.form['Body'].lower().replace('bo4', '').strip()
        platform = 'psn'
        if request.form['Body'].lower().__contains__('xbl'):
            platform = 'xbx'
            bo4_id = bo4_id.replace('xbx', '').strip()
        if request.form['Body'].lower().__contains__('pc'):
            platform = 'pc'
            bo4_id = bo4_id.replace('pc', '').strip()
        else:
            bo4_id = bo4_id.replace('psn', '').strip()
        output = bo4_api(platform, bo4_id)
        response.message(''.join(output))
    if not valid:
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


def apex_legends_api(platform, apex_id):
    headers = {'TRN-Api-Key': tracker_key}
    response = requests.get(
        'https://public-api.tracker.gg/v2/apex/standard/profile/{}/{}'.format(platform, apex_id),
        headers=headers)
    try:
        stats = response.json()['data']['segments'][0]['stats']
        output = ["{}'s APEX LEGENDS STATS:\n".format(apex_id.upper()), '{}\n'.format('-' * 40)]
        for stat in stats:
            output.append('{}: {}\n'.format(stats[stat]['displayName'], stats[stat]['displayValue']))
        return output
    except Exception:
        return ['{} on platform {} not found!'.format(apex_id, platform)]


def bo4_api(platform, bo4_id):
    url = "https://my.callofduty.com/api/papi-client/crm/cod/v2/title/bo4/platform/%s/gamer/%s/profile/" % (
        platform, bo4_id)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/35.0.1916.47 Safari/537.36 '
    headers = {
        'User-Agent': user_agent,
        'Cookie': "check=true; s_dfa=activision.prd; AMCVS_0FB367C2524450B90A490D4C%40AdobeOrg=1; "
                  "_gcl_au=1.1.1054704054.1553245601; _fbp=fb.1.1553245601500.2028367329; "
                  "AMCV_0FB367C2524450B90A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C17978%7CMCMID"
                  "%7C61818798060188250940415165245687586980%7CMCAAMLH-1553850401%7C6%7CMCAAMB-1553850401"
                  "%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1553252801s%7CNONE%7CMCAID"
                  "%7CNONE%7CvVersion%7C3.3.0; "
                  "s_ppvl=https%253A%2F%2Fwww.callofduty.com%2Fuk%2Fen%2F%2C100%2C100%2C979%2C1122%2C979%2C1920"
                  "%2C1080%2C1%2CL; s_cc=true; AAMC_activisionblizzardin_0=REGION%7C6; "
                  "mbox=session#a5a96a6fc4104b5d9d27124b428b9e7b#1553247575|PC#a5a96a6fc4104b5d9d27124b428b9e7b.26_10"
                  "#1616490402; XSRF-TOKEN=68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041; new_SiteId=cod; comid=cod; "
                  "gpv_c8=callofduty%3Ahub%3Ahome; ACT_SSO_LOCALE=en_US; "
                  "s_ppv=callofduty%253Ahub%253Ahome%2C30%2C31%2C979%2C1346%2C979%2C1920%2C1080%2C1%2CL; "
                  "s_nr=1553245754054-New; "
                  "s_sq=activision.prd%3D%2526c.%2526a.%2526activitymap.%2526page%253Dcallofduty%25253Ahub%25253Ahome"
                  "%2526link%253DMY%252520CALL%252520OF%252520DUTY%2526region%253DBODY%2526pageIDType%253D1%2526"
                  ".activitymap%2526.a%2526.c%2526pid%253Dcallofduty%25253Ahub%25253Ahome%2526pidt%253D1%2526oid"
                  "%253Dhttps%25253A%25252F%25252Fmy.callofduty.com%25252Fuk%25252Fen%2526ot%253DA; "
                  "SSO_REDIRECTED_AT_LOGIN=https://my.callofduty.com/uk/en/dashboard; "
                  "ACT_SSO_COOKIE"
                  "=MTQ0OTE2NTk5NDg2MjE1ODcwMDI6MTU1NDQ1NTM1NjMwNjo2NmM3OTkzNTlhYTk0ODQ0OWQ2ODE3OTQ1ZjdkNWQyYw; "
                  "s_ACT_SSO_COOKIE"
                  "=MTQ0OTE2NTk5NDg2MjE1ODcwMDI6MTU1NDQ1NTM1NjMwNjo2NmM3OTkzNTlhYTk0ODQ0OWQ2ODE3OTQ1ZjdkNWQyYw; "
                  "atkn=eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYiLCAia2lkIjogInVub18xIn0"
                  ".PqqRf9LvYpg7blrqSIhl5Ijt7lSOOaiDDjHMx1an1Q5eRjXrsn2biO3844D9WuDroVwZOLW"
                  "-QgCpy91RENYrAyeTgb6igFqXXDZzdFFBAjCuNU923kwTxGS6KGh2bUHk3toYBiW8vUmGMQCv0X5d8FAMmhImOgC5IJBullAugAE.LWdQYIZGxB5FJvbut27b1w.Xk_F5I4RIgTTQxE9KR9FvnwoRALIfG_QCtqgIbEF1mPe9W6m5F_M0E7YEhB9_u0zW1biIJ1gfjOcUKkqD6YwjKnojqI3bBDBQvHl9QmWdDKi1RLcMxlaa03Umb0aFeWdKxcX3lG7Je09FaLxPpiK_Ot1En39T6RACd6GUhmAXckZILTOtUKK4pbUjI6GBy_QKD0xRNGLi3ZQPCANEOSgL2qA-LcQNP5aa3BVbphBREUdaF-ONqa3cGx9Qrj6zi1tf0X3m6bgRyzeEiJyZhSZoPopumaE0uc6bJkjK07XIrP1gPH2sqxSh6oBL2Ize6H_STfyFn3GyOtaqxbhM0t-3tRg47a1NlyBqjUGpzbj20KfvVJdO1fpd1XiDzzFqj1yeegPGv6FLgfcPoyva8vL2v40vwmjmf-EWmUSHhq8oqoICvSsRYCKgvsb-M3bdD0Et9loa112UR169lc2w9xvljbCODh780jkFw4L6sMogVvUiGJu8vj0OGMxZnwwofG4dKAXeXGinMTH5i6JF_Sl7k9KrCjG3Ij9rA3UFylZ76U.aTc-58SN1wfbXhH1vZQRzg; rtkn=eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYiLCAia2lkIjogInVub18xIn0.H_RFSOIclb7gNZ8UwQYFk3KsGB_kIjb12ernpheOIoSZlHkKjVfDdvKGWzZnQbMi5f_98fCRoQl_5GQPOKdpJdFbIrtUrESb-0udhuc0JNfApRDocb06ZOOD1EKelh1xoab6aCAG-KyY5muyL2RG3aGowENWsRsiMpaIznMchpc.a7RTG86crE72z4aXpUjLvg.3MXYDWiEsL52YeKovMvwzLftviEL2f69YRyp0z-mNWbYvWYuzJS5rSaFd1W6ZdDiqA7XgIphfR1MpiFaqfweii0-vVNpW-WtiZvD8BNQcObMpNM7DO6wjBCavra12USmEgv7jYx2FhEEz8KkmtRUgfFQA5iJCnzoUptkvPPECxJlSxf4aBUjrmeHTk662PAU82LUhWt8kUFmtDfzqnQiNlZdc5gFTJsI3mq52bke_FfxLwj3IAMyAfzh53FyeAhM5lH12EFcvBc-GiUxc3TuIbu5fTAEvsHiqwsEYcy_HoKZ-giDwN1SrKeTKX2Gb398A6b-pYUO9SO0WFulQic7F40bH_8FQdBB93iZ5aDOMLshqTAcoCZvPkUdd_xiXbpuXu4lcNCyGcQlnsjKYXsUor8uQcRffi8ARO0q9LA-iOKJ00JYkWV8SMojef5j-6Di_liOACkbOPbBw0Xx8W3ZOmGeX098aniBM54S55cDdZDveMFZcpDtuQYcAfnDglAxBxFnx62WY8vR9a-8foWVKJeVB68Xm6pCaPp6s6KHdPRLEduJq2-T_3DWoEwtSS-_hm8-5oYZTaN52rTjtw-CIA.SvXszntJbbi7ZyCTahr_8g; ACT_SSO_REMEMBER_ME=MTQ0OTE2NTk5NDg2MjE1ODcwMDI6JDJhJDEwJGxNY2kvNVFDT2JWNkVWYk55RGxIdE83WnN1TDRrYzlsdVdPc3oxRWNHRlBtMVZnLzhOcGVp; ACT_SSO_EVENT=LOGIN_SUCCESS:1553245756744; pgacct=psn; CRM_BLOB=eyJ2ZXIiOjEsInBsYXQiOnsicCI6eyJ2IjowLCJ0Ijp7ImJvNCI6eyJtcCI6bnVsbCwieiI6bnVsbCwicHJlcyI6MC4wLCJzcCI6MC4wLCJsZXYiOjQwLjB9LCJ3d2lpIjp7Im1wIjpudWxsLCJ6IjpudWxsLCJwcmVzIjoxLjAsInNwIjowLjAsImxldiI6NDQuMH19fX19; agegate=; country=GB; umbrellaId=3306746010444912014; facebookId=true; psnId=true; twitchId=true; twitterId=true; youTubeId=true",
    }
    response = requests.get(url, headers=headers)
    output = ["{}'s BO4 LEGENDS STATS:\n".format(bo4_id.upper()), '{}\n'.format('-' * 40)]
    stats = {
        'EKIA': int(response.json()['data']['mp']['lifetime']['all']['ekia']),
        'Deaths': int(response.json()['data']['mp']['lifetime']['all']['deaths']),
        'EKIA/D': round((response.json()['data']['mp']['lifetime']['all']['ekiadRatio']), 2),
        'Total Games Played': response.json()['data']['mp']['lifetime']['all']['totalGamesPlayed'],
        'Win Loss Ratio': str(
            round((response.json()['data']['mp']['lifetime']['all']['wlRatio']), 2)) + '%',
        'Accuracy': str(round((response.json()['data']['mp']['lifetime']['all']['accuracy']), 2)) + '%',
        'Time Played': str(
            convert_sec_to_day(
                response.json()['data']['mp']['lifetime']['all']['timePlayedTotal'])),
        'Level': int(response.json()['data']['mp']['level']),
        'Score Per Game': int(response.json()['data']['mp']['lifetime']['all']['scorePerGame'])}
    for stat in stats:
        output.append('{}: {}\n'.format(stat, stats[stat]))
    return ''.join(output)


def convert_sec_to_day(n):
    day = n // (24 * 3600)
    n = n % (24 * 3600)
    hour = n // 3600
    n %= 3600
    minutes = n // 60
    n %= 60
    seconds = n
    return (str(int(day)) + "d " + str(int(hour)) + "hours " + str(int(minutes)) + "minutes " + str(
        int(seconds)) + "seconds")



if __name__ == '__main__':
    app.run(debug=True)

