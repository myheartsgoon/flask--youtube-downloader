from pytube.api import YouTube
import requests
from bs4 import BeautifulSoup


class Get_user_videos():
    def __init__(self, user):
        self.user = user
        self.user_url = 'https://www.youtube.com/user/' + user + '/videos'
        self.title = []
        self.link = []
        self.time = []

    def get_infos(self):
        res = requests.get(self.user_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        itemlist = soup.select('.channels-browse-content-grid')[0].select('.channels-content-item')
        for item in itemlist:
            self.link.append('https://www.youtube.com' + item.select('a')[1]['href'])
            self.title.append(item.select('a')[1]['title'])
            self.time.append(item.select('.yt-lockup-meta-info')[0].select('li')[1].text)
            self.group = zip(self.title, self.link, self.time)

class Download():
    def __init__(self, link):
        self.link = link
        self.extension = ''
        self.resolutions = set()

    def get_name(self):
        yt = YouTube(self.link)
        return yt.filename

    def download(self, extension, resolution):
        yt = YouTube(self.link)
        video = yt.get(extension, resolution)
        video.download('file/')

    def get_resolution(self):
        yt = YouTube(self.link)
        all_info = yt.get_videos()
        quality = [(i.extension, i.resolution) for i in all_info]
        return quality





#------------------test part----------------
#new = Get_user_videos('marquesbrownlee')
#new.get_infos()
