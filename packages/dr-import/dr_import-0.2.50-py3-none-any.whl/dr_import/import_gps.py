from dateutil.parser import parse
import datetime
import requests
import math
import numpy as np

import tator

def parse_args():
    parser = tator.get_parser()
    parser.add_argument('--username', help="Username for Tracker Systems API.")
    parser.add_argument('--password', help="Password for Tracker Systems API.")
    parser.add_argument('--mdmid', help="MDMID for Tracker Systems API.")
    parser.add_argument('--project', help="Tator project to import GPS data.")
    parser.add_argument('--section', help="Section to import GPS data.")
    return parser.parse_args()

def get_media_info(args, api):
    medias = api.get_media_list(args.project, section=args.section, dtype='multi')
    max_datetime = datetime.datetime.now() - datetime.timedelta(days=365*1000)
    min_datetime = datetime.datetime.now() + datetime.timedelta(days=365*1000)
    datetime_lookup = {}
    child_ids = []
    for media in medias:
        child_ids += media.media_files.ids
    medias = api.get_media_list_by_id(project=args.project,
                                      media_id_query={'ids': child_ids})
    for media in medias:
        start_datetime = parse(media.name.split('.')[0].replace('_', ':'))
        duration = datetime.timedelta(seconds=media.num_frames / media.fps)
        stop_datetime = start_datetime + duration
        if start_datetime < min_datetime:
            min_datetime = start_datetime
        if stop_datetime > max_datetime:
            max_datetime = stop_datetime
        datetime_lookup[media.id] = {
            'start': start_datetime,
            'stop': stop_datetime,
            'obj': media,
        }
    return datetime_lookup, min_datetime, max_datetime

def get_gps_data(args, min_dt, max_dt):
    start_date = min_dt.strftime('%m/%d/%Y')
    end_date = max_dt.strftime('%m/%d/%Y')
    start_time = min_dt.strftime('%H:%M:%S')
    end_time = max_dt.strftime('%H:%M:%S')
    url = ("https://app.trackersystems.net/services/UD"
          f"?unit={args.mdmid}"
          f"&startDate={start_date}"
          f"&endDate={end_date}"
          f"&startTime={start_time}"
          f"&endTime={end_time}")
    response = requests.get(url, auth=(args.username, args.password))
    if response.status_code != 200:
        raise RuntimeError("Failed to retrieve data from Tracker Systems API!")
    data = response.json()
    data = data['FleetData']
    for entry in data:
        entry['datetime'] = parse(entry['locTime'])
    return data

def display_gps_data(args, gps):
    import plotly.graph_objects as go
    lat = [float(entry['coords'].split(':')[0]) for entry in gps]
    lon = [float(entry['coords'].split(':')[1]) for entry in gps]
    fig = go.Figure(data=go.Scattergeo(
        lat=lat,
        lon=lon,
        mode='lines',
        line=dict(width=2, color='blue'),
    ))
    fig.update_layout(
        title_text='Trip Path',
        showlegend=False,
        geo = dict(
            resolution = 50,
            showland = True,
            showlakes = True,
            landcolor = 'rgb(204, 204, 204)',
            countrycolor = 'rgb(204, 204, 204)',
            lakecolor = 'rgb(255, 255, 255)',
            projection_type = "equirectangular",
            coastlinewidth = 2,
            lataxis = dict(
                range = [min(lat) - 0.2, max(lat) + 0.2],
                showgrid = True,
                dtick = 0.1
            ),
            lonaxis = dict(
                range = [min(lon) - 0.2, max(lon) + 0.2],
                showgrid = True,
                dtick = 0.1
            ),
        )
    )
    fig.show()

def to_spec(gps_type, media, entry):
    delta = entry['datetime'] - media['start']
    frame = math.floor(delta.seconds * media['obj'].fps)
    lat, lon = entry['coords'].split(':')
    lat = float(lat)
    lon = float(lon)
    return {
        'type': gps_type.id,
        'media_ids': [media['obj'].id],
        'frame': frame,
        'Satellite Count': entry['satFixScore'],
        'Knots': entry['speed'] / 1.151, # mph to knots
        'Heading': float(entry['direction']),
        'Datecode': parse(entry['locTime']+'+00:00').isoformat(),
        'Position': [lon, lat],
    }

def find_gps(args, api, lookup, gps):
    spec = []
    state_types = api.get_state_type_list(args.project)
    for gps_type in state_types:
        if gps_type.name == 'GPS':
            break
    gps_times = np.array([entry['datetime'] for entry in gps])
    for media_id, media in lookup.items():
        start_index = np.argmin(np.abs(media['start'] - gps_times))
        entries = [to_spec(gps_type, media, gps[start_index])]
        entries += [to_spec(gps_type, media, entry) for entry in gps
                    if entry['datetime'] > media['start']
                    and entry['datetime'] < media['stop']]
        entries[0]['frame'] = 0
        spec += entries
        print(f"Found {len(entries)} GPS entries for media {media_id} ({media['start']} - {media['stop']})...")
    print(f"Found {len(spec)} GPS entries total...")
    return spec

def delete_existing_gps(args, api, lookup):
    state_types = api.get_state_type_list(args.project)
    for gps_type in state_types:
        if gps_type.name == 'GPS':
            break

    media_ids = list(lookup.keys())

    for media_id in media_ids:
        existing = api.get_state_list(args.project, media_id=[media_id], type=gps_type.id)
        if len(existing) > 0:
            print(f"Found {len(existing)} GPS states on media {media_id} - clearing out first.")
            api.delete_state_list(args.project, media_id=[media_id], type=gps_type.id)

def import_gps(args, api, spec):
    created_ids = []
    for response in tator.util.chunked_create(api.create_state_list, args.project,
                                              state_spec=spec):
        created_ids += response.id
        print(response.message)
    print(f"Successfully imported {len(created_ids)} GPS entries!")

if __name__ == '__main__':
    args = parse_args()
    api = tator.get_api(args.host, args.token)
    lookup, min_dt, max_dt = get_media_info(args, api)
    gps = get_gps_data(args, min_dt, max_dt)
    display_gps_data(args, gps)
    spec = find_gps(args, api, lookup, gps)
    ok = input("Continue with import to Tator? [y/N]: ")
    if ok.lower() == 'y':
        delete_existing_gps(args, api, lookup)
        import_gps(args, api, spec)
    else:
        print("Import aborted.")

