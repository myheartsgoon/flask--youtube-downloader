import pdfkit

options = {
    'quiet': ''
    }
path_wkthmltopdf = '/app/wkhtmltox/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
def convert_page_to_pdf(url):
    result = pdfkit.from_url(url, 'file/output.pdf', options=options, configuration=config)
    return result
