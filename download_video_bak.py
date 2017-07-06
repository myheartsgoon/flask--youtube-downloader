from pytube.api import YouTube
import requests
from bs4 import BeautifulSoup


class Get_user_videos():
    def __init__(self, user):
        self.user = user
        self.user_url = 'https://www.youtube.com/user/' + user + '/videos'
        self.title = ''
        self.link = ''
        self.time = ''

    def get_infos(self):
        res = requests.get(self.user_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        itemlist = soup.select('.channels-browse-content-grid')[0].select('.channels-content-item')
        for item in itemlist:
            self.link = 'https://www.youtube.com' + item.select('a')[1]['href']
            self.title = item.select('a')[1]['title']
            self.time = item.select('.yt-lockup-meta-info')[0].select('li')[1].text
            print(self.title, self.link, self.time)

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
#new = Get_user_videos('marquesbrownlee')
#new.get_infos()