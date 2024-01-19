import requests
import os

STOPPED = 0
PAUSED = 1
PLAYING = 2

authorization = f'MediaBrowser Client="Light automation",Device="ha01",DeviceId="ha01.tre.esav.fi",Version="0.0.1",Token="{os.environ["TOKEN"]}"' 
api = f'{os.environ["URL"]}/Sessions'

def get_state():

    resp = requests.get(api, headers={'Authorization': authorization})
    sessions = resp.json()

    state = STOPPED

    for session in sessions:
        if session['UserName'] != 'lgtv':
            continue

        now_playing = session.get('NowPlayingItem') is not None
        paused = session['PlayState']['IsPaused']

        if now_playing and not paused:
            state = max(state, PLAYING)
        elif now_playing:
            state = max(state, PAUSED)
        else:
            state = max(state, STOPPED)

    return state
