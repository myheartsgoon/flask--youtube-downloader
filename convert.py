import pdfkit
import requests
from bs4 import BeautifulSoup

options = {
    'quiet': '',
    'encoding': "UTF-8",
    }
path_wkthmltopdf = '/app/wkhtmltox/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)


class Convert_to_PDF():
    def __init__(self, url):
        self.url = url

    def get_name(self):
        try:
            if not self.url.startswith('http'):
                self.url = 'http://' + self.url
            res = requests.get(self.url)
            html = BeautifulSoup(res.text, 'html.parser')
            return html.title.text
        except Exception as e:
            return 'No title'

    def convert_page_to_pdf(self):
        try:
            #if self.url.split()
            result = pdfkit.from_url(self.url, 'file/output.pdf', options=options, configuration=config)
            return result
        except Exception as e:
            return str(e)

# c = Convert_to_PDF('www.google.com')
# print(type(c.get_name()))