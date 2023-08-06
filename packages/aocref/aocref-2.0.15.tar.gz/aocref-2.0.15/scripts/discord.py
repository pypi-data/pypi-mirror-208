import json
import helpers
from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(sequence=4, offset=2)
yaml.preserve_quotes = True

def strip_leading_double_space(stream):
    if stream.startswith("  "):
        stream = stream[2:]
    return stream.replace("\n  ", "\n")


with open('../aoe2-events/safe') as h:
    #ids = json.loads(h.read())
    with open('data/players.yaml') as h2:
        players = yaml.load(h2)
        lines = h.readlines()
        for player in players:
            for line in lines:
                p = line.strip().split(" ")
                if p[1].strip() == player['name']:
                    print(p[1], p[2])
                    player['discord_id'] = p[2].strip()
    """
        for discord_id in ids:
            for p in players:
                nicks = [p['name']]
                if 'aka' in p:
                    nicks += p['aka']
                if 'liquipedia' in p:
                    nicks.append(p['liquipedia'])
                for n in set(nicks):
                    #print(discord_id.split('#')[1], n)
                    if helpers.same(discord_id.split('#')[0], n):
                        print(discord_id, '->', p['name'])
                        p['discord_id'] = discord_id
    """
    with open('data/players.yaml', 'w') as handle:
        yaml.dump(players, handle, transform=strip_leading_double_space)
