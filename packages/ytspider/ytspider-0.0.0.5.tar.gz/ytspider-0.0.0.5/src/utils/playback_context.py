def getPlaybackContext(splay=True, autoCaptionsDefaultOn=False, signatureTimestamp=19445, vid="hfyLjRZmEFc"):

    context = {
        'contentPlaybackContext': {
            'currentUrl': f'/watch?v={vid}',
            'vis': 0,
            'splay': splay,
            'autoCaptionsDefaultOn': False,
            'autonavState': 'STATE_OFF',
            'html5Preference': 'HTML5_PREF_WANTS',
            'signatureTimestamp': signatureTimestamp,
            'referer': f'https://www.youtube.com/watch?v={vid}',
            'lactMilliseconds': '1',
            'watchAmbientModeContext': {
                'watchAmbientModeEnabled': True
            }
        }
    }
    return context
