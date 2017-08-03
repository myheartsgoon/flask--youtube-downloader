import pdfkit

options = {
    'quiet': ''
    }

def convert_page_to_pdf(url):
    result = pdfkit.from_url(url, 'file/output.pdf', options=options)
    return result
