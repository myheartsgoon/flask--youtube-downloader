from pytube.api import YouTube
class Download():
    def __init__(self, link):
        self.link = link
        self.name = None

    def download(self):
        yt = YouTube(self.link)
        self.name = yt.filename
        video = yt.get('mp4', '360p')
        video.download('file/')



#------------------test part----------------
