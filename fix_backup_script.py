import os
import json
from decimal import Decimal

base_dir = os.path.dirname(os.path.abspath(__file__))
orig_json = os.path.join(base_dir, '20181010_backup.json')
new_json = os.path.join(base_dir, '20181010_revised.json')

with open(orig_json, 'r') as f:
    j = json.load(f)

new_j = []

pauses = []
unpauses = []
replay_starts = []
replay_ends = []
overtime_starts = []
overtime_ends = []
smaller_window_starts = []
smaller_window_ends = []

for item in j:
    if item['model'] == 'annotator.pause':
        pauses.append(item)
    elif item['model'] == 'annotator.unpause':
        unpauses.append(item)
    elif item['model'] == 'annotator.replaystart':
        replay_starts.append(item)
    elif item['model'] == 'annotator.replayend':
        replay_ends.append(item)
    elif item['model'] == 'annotator.overtimestart':
        overtime_starts.append(item)
    elif item['model'] == 'annotator.overtimeend':
        overtime_ends.append(item)
    elif item['model'] == 'annotator.smallerwindowstart':
        smaller_window_starts.append(item)
    elif item['model'] == 'annotator.smallerwindowend':
        smaller_window_ends.append(item)
    else:
        item['model'] = item['model'].replace('annotator', 'api')
        if 'wl_id' in item['fields']:
            del item['fields']['wl_id']
        new_j.append(item)

# PAUSE FIX

for item in pauses:
    item['model'] = item['model'].replace('annotator', 'api')
    item['fields']['start_time'] = Decimal(item['fields']['time_point'])
    del item['fields']['time_point']
    for item2 in unpauses:
        item2['fields']['time_point'] = Decimal(item2['fields']['time_point'])
        #if item2['fields']['round'] == item['fields']['round']:
        #    print('    ', item2)
        if item2['fields']['round'] == item['fields']['round'] and item2['fields']['time_point'] > item['fields']['start_time']:
            item['fields']['end_time'] = item2['fields']['time_point']
            break
    item['fields']['start_time'] = str(item['fields']['start_time'])
    if 'end_time' in item['fields']:
        item['fields']['end_time'] = str(item['fields']['end_time'])
    new_j.append(item)

# REPLAY FIX

for item in replay_starts:
    item['model'] = item['model'].replace('annotator', 'api').replace('start', '')
    item['fields']['start_time'] = Decimal(item['fields']['time_point'])
    del item['fields']['time_point']
    for item2 in replay_ends:
        item2['fields']['time_point'] = Decimal(item2['fields']['time_point'])
        #if item2['fields']['round'] == item['fields']['round']:
        #    print('    ', item2)
        if item2['fields']['round'] == item['fields']['round'] and item2['fields']['time_point'] > item['fields']['start_time']:
            item['fields']['end_time'] = item2['fields']['time_point']
            break
    #print(item)
    item['fields']['start_time'] = str(item['fields']['start_time'])
    if 'end_time' in item['fields']:
        item['fields']['end_time'] = str(item['fields']['end_time'])
    new_j.append(item)

# OVERTIME FIX

for item in overtime_starts:
    item['model'] = item['model'].replace('annotator', 'api').replace('start', '')
    item['fields']['start_time'] = Decimal(item['fields']['time_point'])
    del item['fields']['time_point']
    for item2 in overtime_ends:
        item2['fields']['time_point'] = Decimal(item2['fields']['time_point'])
        #if item2['fields']['round'] == item['fields']['round']:
        #    print('    ', item2)
        if item2['fields']['round'] == item['fields']['round'] and item2['fields']['time_point'] > item['fields']['start_time']:
            item['fields']['end_time'] = item2['fields']['time_point']
            break

    #print(item)
    item['fields']['start_time'] = str(item['fields']['start_time'])
    if 'end_time' in item['fields']:
        item['fields']['end_time'] = str(item['fields']['end_time'])
    new_j.append(item)

# SMALLERWINDOW FIX

for item in smaller_window_starts:
    item['model'] = item['model'].replace('annotator', 'api').replace('start', '')
    item['fields']['start_time'] = Decimal(item['fields']['time_point'])
    del item['fields']['time_point']
    for item2 in smaller_window_ends:
        item2['fields']['time_point'] = Decimal(item2['fields']['time_point'])
        #if item2['fields']['round'] == item['fields']['round']:
        #    print('    ', item2)
        if item2['fields']['round'] == item['fields']['round'] and item2['fields']['time_point'] > item['fields']['start_time']:
            item['fields']['end_time'] = item2['fields']['time_point']
            break
    #print(item)
    item['fields']['start_time'] = str(item['fields']['start_time'])
    if 'end_time' in item['fields']:
        item['fields']['end_time'] = str(item['fields']['end_time'])
    new_j.append(item)

with open(new_json, 'w') as f:
    json.dump(new_j, f)