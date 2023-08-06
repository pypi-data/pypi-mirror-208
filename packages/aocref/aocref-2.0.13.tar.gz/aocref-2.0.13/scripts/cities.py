from dashboard.sources import twitter
import asyncio
import logging
from ruamel.yaml import YAML


def strip_leading_double_space(stream):
    if stream.startswith("  "):
        stream = stream[2:]
    return stream.replace("\n  ", "\n")



async def main():
    logging.basicConfig(level=logging.INFO)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(sequence=4, offset=2)

    with open('data/players.yaml', 'r') as handle:
        player_data = yaml.load(handle)

    pmap = {}
    for p in player_data:
        if 'twitter' in p:
            for t in p['twitter']:
                pmap[p['id']] = t.split('/')[-1].lower()


    locs = await twitter.locations(pmap.values())
    for sn, city in locs.items():
        print(sn, city)

    for p in player_data:
        if p['id'] in pmap and pmap[p['id']] in locs and ('city' not in p or not p['city']):
            p['city'] = locs[pmap[p['id']]]

    with open('data/players.yaml', 'w') as handle:
        yaml.dump(player_data, handle, transform=strip_leading_double_space)



if __name__ == '__main__':
    asyncio.run(main())
