# YTSpider
YouTube Scraper (Un-official API)

Available features:
- videos
- comments
- transcripts
- channels
- playlists.

# Installation
    pip install ytspider

# Usage

<h2>Scrape Videos</h2>

```
from ytspider import YTSVideo

vid_id = "jNQXAC9IVRw"

video = YTSVideo()
video.scrape(vid_id)
videoData = video.get()
```


<h2>Scrape Videos with Comments</h2>

```
from ytspider import YTSVideo

vid_id = "jNQXAC9IVRw"

video = YTSVideo()
video.scrape(vid_id).withComments(n_comments=100)
videoData = video.get()
```

```.get()``` returns ```dict<str, dict>```, str is videoId, dict is data
Now you have list of comments in ```videoData[vid_id]["comments"]```


Or you can set a default behavior for scraping comments
without calling ```withComments()``` each time

```
video = YTSVideo(commentScrapingBehavior="scrape") # ("scrape", "ignore" or None, Custom Behavior)
```

<h2>Scrape Channels</h2>

```
from ytspider import YTSChannel

channel_url = "https://www.youtube.com/@jawed"   # or just screen-name @jawed

channel = YTSChannel()
channel.scrape(channel_url)
channelData = channel.get()
```

```.get()``` returns ```dict<str, dict>```, ```str``` is channel Id, ```dict``` is data


<h2>Scrape Channels with Videos</h2>

```
from ytspider import YTSChannel

channel_url = "https://www.youtube.com/@jawed"   # or just screen-name @jawed

channel = YTSChannel()
channel.scrape(channel_url).withVideos(n_videos=29)
channelData = channel.get()

# .get() returns dict<str, dict>, str is channel Id, dict is data
# Now you have list of videos in channelData["@jawed"]["videos"]
```

# Software Extensibility
<h2>Custom Behaviors (Decorators)</h2>
How to add your own behavior for scraping comments, transcriptions, or additional capabilities<br>
Will be documented soon