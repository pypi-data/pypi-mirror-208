import json
from .client import getClient
from .playback_context import getPlaybackContext
from .signals_info import getSignalsInfo

class Context:
    def __init__(self, contentCheckOk=False):
        self.contentCheckOk = contentCheckOk
        self.context = {
            'context':
            {
                'client': getClient("en"),
                'user': {'lockedSafetyMode': False},
                'request': {'useSsl': True,
                            'internalExperimentFlags': [],
                            'consistencyTokenJars': []},
                'clickTracking': {'clickTrackingParams': 'CDIQvU4YACITCLfOn-6Xkf4CFRPeFgodhAgHNTIJZW5kc2NyZWVuSOayt8W2i9D-9QGaAQUIAhD4HQ=='},
                'adSignalsInfo': getSignalsInfo(media="image"),
            },
            'videoId': 'hfyLjRZmEFc',
            'playbackContext': getPlaybackContext(splay=False),
            'racyCheckOk': False,
            'contentCheckOk': self.contentCheckOk}
        self.defaultId = "hfyLjRZmEFc"

    def replace(self, key, value):
        context_str = json.dumps(self.context)
        context_str = context_str.replace(key, value)
        self.context = json.loads(context_str)
        return self

    def replaceVideoId(self, value):
        self.replace(self.defaultId, value)
        self.defaultId = value
        return self

    def add(self, key, value):
        self.context[key] = value
        return self

    def remove(self, key):
        del self.context[key]
        return self

    def get(self):
        return self.context

    def getDefaultVideoId(self):
        return self.defaultId


