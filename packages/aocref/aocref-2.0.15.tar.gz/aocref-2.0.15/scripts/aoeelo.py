import requests
from ruamel.yaml import YAML

p = requests.get('https://aoe-elo.com/api/?request=players').json()

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=4, offset=2)
with open('data/players.yaml', 'r') as handle:
    player_data = yaml.load(handle)

last_id = max([p.get('id') for p in player_data])

i = 0
for player in p:
    d = requests.get(player['api_url']).json()
    aoeelo_id = d['id']
    steam_id = None
    profile_id = None
    voobly_id = None
    print('---------', d['name'], f"({aoeelo_id})")
    if 'steam_id' in d and d['steam_id']:
        print('s', d['id'], '->', d['steam_id'])
        steam_id = d['steam_id']
        p = requests.get(f'https://aoe2.net/api/player/lastmatch?game=aoe2de&steam_id={steam_id}').json()
        print('p', d['id'], '->', p['profile_id'])
        profile_id = str(p['profile_id'])
    if 'voobly_id' in d and d['voobly_id']:
        print('v', d['id'], '->', d['voobly_id'])
        voobly_id = str(d['voobly_id'])
    found = False
    for k in player_data:
        if 'aoeelo' not in k:
            if 'platforms' in k and 'rl' in k['platforms'] and profile_id in k['platforms']['rl']:
                print("adding aoeelo based on profile id")
                k['aoeelo'] = aoeelo_id
                found = True
            elif 'platforms' in k and 'voobly' in k['platforms'] and k['platforms']['voobly'] is None:
                print(k)
            elif 'platforms' in k and 'voobly' in k['platforms'] and voobly_id in k['platforms']['voobly']:
                print("adding aoeelo based on voobly id")
                k['aoeelo'] = aoeelo_id
                found = True
            elif d['name'].lower().replace(' ', '_').replace('_', '') == k['name'].lower().replace(' ', '_').replace('_', ''):
                print("adding aoeelo based on name")
                k['aoeelo'] = aoeelo_id
                found = True
            elif 'liquipedia' in k and k['liquipedia'] and d['name'].lower().replace(' ', '_').replace('_', '') == k['liquipedia'].lower().replace(' ', '_').replace('_', ''):
                print("adding aoeelo based on liquipedia")
                k['aoeelo'] = aoeelo_id
                found = True
            elif 'aka' in k and isinstance(k['aka'], list):
                for aka in k['aka']:
                    if d['name'].lower().replace(' ', '_').replace('_', '') == aka.lower().replace(' ', '_').replace('_', ''):
                        print("adding aoeelo based on aka")
                        k['aoeelo'] = aoeelo_id
                        found = True

        if 'aoeelo' in k and k['aoeelo'] == aoeelo_id:
            print(">>FOUND")
            found = True
            if 'platforms' in k:
                if 'rl' in k['platforms'] and profile_id not in k['platforms']['rl'] and profile_id:
                    print("adding profile id to known aoeelo")
                    k['platforms']['rl'].append(profile_id)
                if 'rl' not in k['platforms'] and profile_id:
                    print("adding new rl platform to known aoeelo")
                    k['platforms']['rl'] = [profile_id]
                if 'voobly' in k['platforms'] and voobly_id not in k['platforms']['voobly'] and voobly_id:
                    print("adding voobly id to known aoeelo")
                    k['platforms']['voobly'].append(voobly_id)
                if 'voobly' not in k['platforms'] and voobly_id:
                    print("adding new voobly platform to known aoeelo")
                    k['platforms']['voobly'] = [voobly_id]
            else:
                if profile_id and not voobly_id:
                    print("adding new platform and rl platform to known aoeelo")
                    k['platforms'] = {'rl': [profile_id]}
                elif voobly_id and not profile_id:
                    print("adding new platform and rl platform to known aoeelo")
                    k['platforms'] = {'voobly': [voobly_id]}
                elif voobly_id and profile_id:
                    print("adding new platform and rl platform and voobly platform to known aoeelo")
                    k['platforms'] = {'rl': [profile_id], 'voobly': [voobly_id]}

    if not found and d['rank'] <= 200 and (voobly_id or profile_id):
        last_id += 1
        platforms = {}
        if voobly_id:
            platforms['voobly'] = [voobly_id]
        if profile_id:
            platforms['rl'] = [profile_id]
        player_data.append(dict(
            name=d['name'],
            aoeelo=aoeelo_id,
            platforms=platforms,
            id=last_id
        ))
        print(f"adding untracked player {d['name']}")

    #i += 1
    #if i == 20:
    #    break


def strip_leading_double_space(stream):
    if stream.startswith("  "):
        stream = stream[2:]
    return stream.replace("\n  ", "\n")


with open('data/players.yaml', 'w') as handle:
    yaml.dump(player_data, handle, transform=strip_leading_double_space)

