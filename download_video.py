from pytube.api import YouTube
class Download():
    def __init__(self, link):
        self.link = link

    def get_name(self):
        yt = YouTube(self.link)
        return yt.filename

    def download(self):
        yt = YouTube(self.link)
        video = yt.get('mp4', '360p')
        video.download('file/')



#------------------test part----------------
