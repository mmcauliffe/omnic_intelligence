import os
import json
import requests
import csv
import datetime
import calendar
import re
import time
from django.conf import settings
from bs4 import BeautifulSoup

match_template = 'https://www.winstonslab.com/matches/match.php?id={}'
event_template = 'https://www.winstonslab.com/events/event.php?id={}'
match_data_template = 'https://www.winstonslab.com/matches/getMatchData.php?matchID={}&gameNumber={}&roundNumber={}'
map_pt_template = 'https://www.winstonslab.com/matches/mapAndPtCaps.php?matchID={}&gameNumber={}&roundNumber={}'


class NotFoundID(Exception):
    pass


def scrape_wl():
    errors = []
    not_found = []
    for i in range(1, 2500):
        # if i != 513:
        #    continue
        if i in [201, 685, 1658]:  # Bad ones
            continue
        print(i)
        try:
            parse_page(i)
        except NotFoundID:
            not_found.append(str(i))
            continue
        except Exception as e:
            raise
            print(e)
            errors.append(str(i))
            continue


def get_event(soup):
    link = soup.find_all('a', class_='match-event')[0]
    m = re.search(r'id=(\d+)', link['href'])
    id = m.groups()[0]
    name = link.get_text().lower()
    return name, id


def get_date(soup):
    date_span = soup.find('span', id="tzDate_1")
    date_text = date_span.get_text()
    m = re.match('(\d+)\w+\sof\s(\w+)\s(\d+)', date_text)
    day, month_name, year = m.groups()
    date = datetime.date(year=int(year), day=int(day), month=list(calendar.month_abbr).index(month_name[:3]))
    return date


def check_exists(soup):
    not_found = soup.find_all('span', class_='label-danger')
    if not_found:
        raise (NotFoundID())


def parse_page(id):
    match_dir = os.path.join(settings.SCRAPE_CACHE_DIRECTORY, 'matches', str(id))
    json_path = os.path.join(match_dir, '{}.json'.format(id))
    if not os.path.exists(json_path):
        page = requests.get(match_template.format(id))

        soup = BeautifulSoup(page.content, 'html.parser')
        check_exists(soup)
        date = get_date(soup)
        today = date.today()
        if date >= today:
            print("Match hasn't happened yet")
            return None, None
        os.makedirs(match_dir, exist_ok=True)
        team1_name, team1_id = get_team_name(soup, '1')
        team2_name, team2_id = get_team_name(soup, '2')
        game_metas = get_maps_and_scores(soup)
        for i, g in enumerate(game_metas):
            print(g)
            game_dir = os.path.join(match_dir, str(i+1))
            os.makedirs(game_dir, exist_ok=True)
            game_json_path = os.path.join(game_dir, 'game{}.json'.format(i+1))
            with open(game_json_path, 'w', encoding='utf8') as f:
                json.dump(g, f, sort_keys=True, indent=4)
        event, event_id = get_event(soup)
        vod = get_vod_link(soup)
        match_metadata = {'event': event,
                          'event_id': event_id,
                          'team1': team1_name,
                          'team1_id': team1_id,
                          'team2': team2_name,
                          'team2_id': team2_id
                          }
        if vod is not None:
            match_metadata['vod'] = vod
        else:
            match_metadata['vod'] = ''
        cache_timeline_data(id)
        with open(json_path, 'w', encoding='utf8') as f:
            json.dump(match_metadata, f, sort_keys=True, indent=4)
        time.sleep(0.5)


def get_vod_link(soup):
    twitch_div = soup.find('a', class_='stream')
    if twitch_div is None:
        return None
    return twitch_div['href']

def get_team_name(soup, team_id):
    team = soup.find_all('div', class_='team{}-name'.format(team_id))
    team_name = team[0].find_all('a')[0].get_text().lower()
    team_id = re.search(r'id=(\d+)', team[0].find_all('a')[0]['href']).groups()[0]
    return team_name, team_id


def get_players(soup, class_name):
    team_table = soup.find_all('table', class_=class_name)
    if team_table:
        cells = team_table[0].find_all('td')
        team_players = []
        for c in cells:
            link = c.find_all('a')
            if not link:
                continue
            team_players.append(link[0].get_text().lower())
    else:
        return []
    return sorted(team_players)


def get_maps_and_scores(soup):

    game_metas = []
    try:
        map_scores = soup.find('div', class_='mini-map-scores').find_all('div', class_='map-score')
    except AttributeError:
        return []
    for ms in map_scores:
        meta = {}
        map_name = ms.find('div', class_='mapname')['title'].lower()
        score1 = [x.get_text() for x in ms.find('div', class_='score1').find_all('span')]
        score2 = [x.get_text() for x in ms.find('div', class_='score2').find_all('span')]
        meta['map'] = map_name
        meta['left_score'] = score1
        meta['right_score'] = score2
        game_metas.append(meta)
    return game_metas


def cache_timeline_data(id):
    match_dir = os.path.join(settings.SCRAPE_CACHE_DIRECTORY, 'matches', str(id))
    for gi in range(1, 7):
        game_dir = os.path.join(match_dir, str(gi))
        os.makedirs(game_dir, exist_ok=True)
        for ri in range(1, 20):
            json_path = os.path.join(game_dir, '{}_{}_data.json'.format(gi, ri))
            if os.path.exists(json_path):
                continue
            page = requests.get(
                match_data_template.format(id, gi, ri))
            try:
                resp = page.content.decode('utf8')
            except:
                continue
            if not resp:
                print(gi, ri)
                break
            data = json.loads(resp)

            with open(json_path, 'w', encoding='utf8') as dataf:
                json.dump(data, dataf)
