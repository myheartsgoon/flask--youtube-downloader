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

    def download(self, extension, resolution, filename):
        yt = YouTube(self.link)
        yt.filename = filename
        video = yt.get(extension, resolution)
        video.download('file/')

    def get_resolution(self):
        yt = YouTube(self.link)
        all_info = yt.get_videos()
        quality = [(i.extension, i.resolution) for i in all_info]
        return quality


class Search_video():
    def __init__(self):
        self.vid_url = []
        self.vid_title = []
        self.vid_author = []
        self.vid_group = []

    def search(self, keyword):
        url = "https://www.youtube.com/results?search_query=" + keyword
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        item_list = soup.select('.item-section')[0].select('.yt-lockup')
        for item in item_list:
            vid_url = 'https://www.youtube.com' + item.select('a')[1]['href']
            if vid_url.startswith('https://www.youtube.com/watch'):
                self.vid_author.append(item.select('a')[2].text)
            elif vid_url.startswith('https://www.youtube.com/channel'):
                self.vid_author.append('Youtube_Channel')
            else:
                continue
            self.vid_url.append(vid_url)
            self.vid_title.append(item.select('a')[1]['title'])
        self.vid_group = zip(self.vid_title, self.vid_url, self.vid_author)





#------------------test part----------------
#new = Get_user_videos('marquesbrownlee')
#new.get_infos()

