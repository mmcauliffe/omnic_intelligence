import os
import json
import requests
import csv
import datetime
import calendar
import shutil
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


def transform_oi_heroes(hero):
    if hero == 'Lúcio':
        return 'lucio'
    if hero == 'Torbjörn':
        return 'torbjorn'
    if hero == 'D.Va':
        return 'dva'
    if hero == 'Soldier: 76':
        return 'soldier76'
    return hero.lower()

def scrape_wl():
    errors = []
    not_found = []
    for i in range(2400, 3100):
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


def match_up_players(left_names, right_names, team_one_players, team_two_players):
    import editdistance
    # hypothesis one:  left = one, right = two
    mean_hyp_one_dist = 0
    hyp_one_left = {}
    hyp_one_right = {}
    scores = {}
    for i, n in left_names.items():
        scores[i] = {}
        m = 100
        out = None
        for p in team_one_players:
            dist = editdistance.eval(n.lower(), p.name) / len(p.name)
            scores[i][p.name] = dist
            if dist < m:
                m = dist
                out = p
        for k, v in hyp_one_left.items():
            if v == out:
                if scores[k][out.name] <= scores[i][out.name]:
                    out_name = min([x for x in scores[i].keys() if x != out.name], key=lambda x: scores[i][x])
                    out = [p for p in team_one_players if p.name == out_name][0]
                else:
                    out_name = min([x for x in scores[k].keys() if x != v.name], key=lambda x: scores[k][x])
                    hyp_one_left[k] = [p for p in team_one_players if p.name == out_name][0]
        mean_hyp_one_dist += m / 12
        hyp_one_left[i] = out
    scores = {}
    for i, n in right_names.items():
        scores[i] = {}
        m = 100
        out = None
        for p in team_two_players:
            dist = editdistance.eval(n.lower(), p.name) / len(p.name)
            scores[i][p.name] = dist
            if dist < m:
                m = dist
                out = p
        for k, v in hyp_one_right.items():
            if v == out:
                if scores[k][out.name] <= scores[i][out.name]:
                    out_name = min([x for x in scores[i].keys() if x != out.name], key=lambda x: scores[i][x])
                    out = [p for p in team_two_players if p.name == out_name][0]
                else:
                    out_name = min([x for x in scores[k].keys() if x != v.name], key=lambda x: scores[k][x])
                    hyp_one_right[k] = [p for p in team_two_players if p.name == out_name][0]
        mean_hyp_one_dist += m / 12
        hyp_one_right[i] = out
    print(scores)
    # hypothesis two:  right = one, left = two
    mean_hyp_two_dist = 0
    hyp_two_left = {}
    hyp_two_right = {}
    scores = {}
    for i, n in right_names.items():
        scores[i] = {}
        m = 20
        out = None
        for p in team_one_players:
            dist = editdistance.eval(n.lower(), p.name) / len(p.name)
            scores[i][p.name] = dist
            if dist < m:
                m = dist
                out = p
        for k, v in hyp_two_left.items():
            if v == out:
                if scores[k][out.name] <= scores[i][out.name]:
                    out_name = min([x for x in scores[i].keys() if x != out.name], key=lambda x: scores[i][x])
                    out = [p for p in team_one_players if p.name == out_name][0]
                else:
                    out_name = min([x for x in scores[k].keys() if x != v.name], key=lambda x: scores[k][x])
                    hyp_two_left[k] = [p for p in team_one_players if p.name == out_name][0]
        mean_hyp_two_dist += m / 12
        hyp_two_left[i] = out
    scores = {}
    for i, n in left_names.items():
        scores[i] = {}
        m = 20
        out = None
        for p in team_two_players:
            dist = editdistance.eval(n.lower(), p.name) / len(p.name)
            scores[i][p.name] = dist
            if dist < m:
                m = dist
                out = p
        for k, v in hyp_two_right.items():
            if v == out:
                if scores[k][out.name] <= scores[i][out.name]:
                    out_name = min([x for x in scores[i].keys() if x != out.name], key=lambda x: scores[i][x])
                    out = [p for p in team_two_players if p.name == out_name][0]
                else:
                    out_name = min([x for x in scores[k].keys() if x != v.name], key=lambda x: scores[k][x])
                    hyp_two_right[k] = [p for p in team_two_players if p.name == out_name][0]
        mean_hyp_two_dist += m / 12
        hyp_two_right[i] = out
    if mean_hyp_one_dist < mean_hyp_two_dist:
        if len(set(x.name for x in hyp_one_left.values())) != 6:
            print(left_names)
            print(hyp_one_left)
            raise Exception
        if len(set(x.name for x in hyp_one_right.values())) != 6:
            print(right_names)
            print(hyp_one_right)
            raise Exception
        return  hyp_one_left, hyp_one_right, True
    if len(set(x.name for x in hyp_two_left.values())) != 6:
        print(left_names)
        print(hyp_two_left)
        raise Exception
    if len(set(x.name for x in hyp_two_right.values())) != 6:
        print(right_names)
        print(hyp_two_right)
        raise Exception
    return hyp_two_left, hyp_two_right, False

def lookup_team(team_name):
    safe_team_name = team_name.replace(' ', '_')
    url_template = 'http://liquipedia.net/overwatch/' + safe_team_name
    page = requests.get(url_template)

    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all('table', class_='sortable')
    team_members = []
    for t in tables:
        theadrows = t.find_all('th')
        active = False
        for th in theadrows:
            if 'active' in th.text.lower():
                active = True
                break
        if not active:
            continue
        for s in t.find_all('span'):
            team_members.append(s.find('a').text)
    return team_members


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

def get_stream_channel(event_id):
    twitch_pattern = r'https?://(www.)?twitch.tv/(\w+)'
    page = requests.get(event_template.format(event_id))

    soup = BeautifulSoup(page.content, 'html.parser')
    info = soup.find('div', class_='event-general-info')
    streams = info.find_all('a')
    links = [x['href'] for x in streams if 'twitch' in x['href']]
    streams = []
    if links:
        streams = [(re.match(twitch_pattern, x).groups()[0], x) for x in links] [0]
    else:
        return None
    return streams


def parse_page(id):
    match_dir = os.path.join(settings.SCRAPE_CACHE_DIRECTORY, 'matches', str(id))
    json_path = os.path.join(match_dir, '{}.json'.format(id))
    if os.path.exists(match_dir) and all(x == '{}.json'.format(id) for x in os.listdir(match_dir)):
        shutil.rmtree(match_dir)
    if not os.path.exists(json_path):
        page = requests.get(match_template.format(id))

        soup = BeautifulSoup(page.content, 'html.parser')
        check_exists(soup)
        date = get_date(soup)
        today = date.today()
        if date > today:
            print("Match hasn't happened yet", date, today)
            return None, None
        os.makedirs(match_dir, exist_ok=True)
        team1_name, team1_id = get_team_name(soup, '1')
        team2_name, team2_id = get_team_name(soup, '2')
        game_metas = get_maps_and_scores(soup)
        for i, g in enumerate(game_metas):
            print(g)
            game_dir = os.path.join(match_dir, str(i + 1))
            os.makedirs(game_dir, exist_ok=True)
            game_json_path = os.path.join(game_dir, 'game{}.json'.format(i + 1))
            with open(game_json_path, 'w', encoding='utf8') as f:
                json.dump(g, f, sort_keys=True, indent=4)
        event, event_id = get_event(soup)
        stream_channel = get_stream_channel(event_id)
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
        if stream_channel is not None:
            match_metadata['event_channel'] = stream_channel[0]
            match_metadata['event_channel_link'] = stream_channel[1]
        else:
            match_metadata['event_channel'] = ''
            match_metadata['event_channel_link'] = ''
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
        for ri in range(1, 20):
            json_path = os.path.join(game_dir, '{}_{}_data.json'.format(gi, ri))
            if os.path.exists(json_path):
                continue
            page = requests.post(
                match_data_template.format(id, gi, ri), {'matchID': id, 'gameNumber': gi, 'roundNumber': ri})
            try:
                resp = page.content.decode('utf8')
            except:
                continue
            if not resp:
                print(gi, ri)
                break
            os.makedirs(game_dir, exist_ok=True)
            data = json.loads(resp)

            with open(json_path, 'w', encoding='utf8') as dataf:
                json.dump(data, dataf)


def player_box(frame, team, number, style='REGULAR'):
    params = settings.BOX_PARAMETERS[style][team.upper()]
    x = params['X']
    x += (params['WIDTH'] + params['MARGIN']) * (number)
    return frame[params['Y']: params['Y'] + params['HEIGHT'], x: x + params['WIDTH']]

