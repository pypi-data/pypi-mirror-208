from .handler import *


class ScrapingDecorator:
    def __init__(self, defaultHandler=BaseHandler()):

        if not isinstance(defaultHandler, BaseHandler):
            raise ValueError(
                "Argument (defaultHandler) must be a subclass of BaseHandler or 'scrape' or 'ignore'")
 
        self.defaultHandler = defaultHandler


    def setDefaultHandler(self, defaultHandler):
        if defaultHandler is None:
            raise ValueError(
                "Argument (defaultHandler) must be a subclass of parent (BaseHandler)")
        self.defaultHandlers[defaultHandler.name] = defaultHandler
        self.updateHandler(defaultHandler)

    def updateHandler(self, handler):

        if not isinstance(handler, BaseHandler):
            raise ValueError(
                "Argument (handler) must be a subclass of BaseHandler")
        self.attachHandler(handler)

class VideosScraper(ScrapingDecorator):
    def __init__(self, videosDefaultHandler=VideosDefaultHandler()):
        if videosDefaultHandler is None or commentDefaultHandler == 'ignore':
            videosDefaultHandler = VideosDefaultHandler()
        elif videosDefaultHandler == 'scrape':
            videosDefaultHandler = VideosScrapingHandler()

        super(VideosScraper, self).__init__(videosDefaultHandler)

        self.updateHandler(videosDefaultHandler)

    def withVideos(self, n_videos=29):

        handler = VideosScrapingHandler(n_videos=n_videos)
        self.updateHandler(handler)
        return self


class TranscriptScraper(ScrapingDecorator):
    def __init__(self, transcriptDefaultHandler=TranscriptionDefaultHandler()):
        if transcriptDefaultHandler is None or transcriptDefaultHandler == 'ignore':
            transcriptDefaultHandler = TranscriptionDefaultHandler()
        elif transcriptDefaultHandler == 'scrape':
            transcriptDefaultHandler = TranscriptionScrapingHandler()
        super(TranscriptScraper, self).__init__(transcriptDefaultHandler)
        self.updateHandler(transcriptDefaultHandler)

    def withTranscripts(self, only_in_langs=[]):

        handler = TranscriptionScrapingHandler(only_in_langs=only_in_langs)
        self.updateHandler(handler)
        return self

class CommentScraper(ScrapingDecorator):
    def __init__(self, commentDefaultHandler=CommentDefaultHandler()):
        if commentDefaultHandler is None or commentDefaultHandler == 'ignore':
            commentDefaultHandler = CommentDefaultHandler()
        elif commentDefaultHandler == 'scrape':
            commentDefaultHandler = CommentScrapingHandler()

        super(CommentScraper, self).__init__(commentDefaultHandler)

        self.updateHandler(commentDefaultHandler)

    def withComments(self, n_comments=15):

        handler = CommentScrapingHandler(n_comments=n_comments)
        self.updateHandler(handler)
        return self