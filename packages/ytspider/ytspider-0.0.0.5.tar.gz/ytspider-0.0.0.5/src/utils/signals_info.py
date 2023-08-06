def getSignalsInfo(width="1366", height="768", media="video"):
    context = {
        'params': [
            {'key': 'dt', 'value': '1680643875586'},
            {'key': 'flash', 'value': '0'},
            {'key': 'frm', 'value': '0'},
            {'key': 'u_tz', 'value': '120'},
            {'key': 'u_his', 'value': '6'},
            {'key': 'u_h', 'value': height},
            {'key': 'u_w', 'value': width},
            {'key': 'u_ah', 'value': '720'},
            {'key': 'u_aw', 'value': width},
            {'key': 'u_cd', 'value': '24'},
            {'key': 'bc', 'value': '31'},
            {'key': 'bih', 'value': '575'},
            {'key': 'biw', 'value': '454'},
            {'key': 'brdim','value': '0,0,0,0,1366,0,1366,720,471,592'},
            {'key': 'vis', 'value': '1'},
            {'key': 'wgl', 'value': 'true'},
            {'key': 'ca_type', 'value': media}
            ]
        }
    return context