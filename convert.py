import pdfkit
import requests
from bs4 import BeautifulSoup
import re, os
from config import options, PATH_wkthmltopdf

config = pdfkit.configuration(wkhtmltopdf=PATH_wkthmltopdf)


class Convert_to_PDF():
    def __init__(self, url):
        self.url = url

    def get_name(self):
        try:
            if not self.url.startswith('http'):
                self.url = 'http://' + self.url
            if len(self.url.split('.')) == 1 \
                or re.match(r'[0-9]+\.[0-9]+',self.url):
                return ('invalid', 'invalid')
            res = requests.get(self.url)
            res.encoding = 'uft-8'
            html = BeautifulSoup(res.text, 'html.parser')
            return (html.title.text, self.url)
        except Exception as e:
            return ('No title', self.url)

    def convert_page_to_pdf(self):
        try:
            #if self.url.split()
            result = pdfkit.from_url(self.url, 'file/output.pdf', options=options, configuration=config)
            return result
        except Exception as e:
            return str(e)

# c = Convert_to_PDF('www.google.com')
# print(type(c.get_name()))