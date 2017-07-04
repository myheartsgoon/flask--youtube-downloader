# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
from forms import DownloadForm
from datetime import timedelta
from download_video import Download


app = Flask(__name__)

@app.before_request
def make_session_permant():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

app.secret_key = 'development-key'

@app.route('/', methods=['GET', 'POST'])
def home():
    form = DownloadForm()
    video = Download(form.youtube_url.data)
    if request.method == 'POST':
        if not form.validate():
            return render_template('home.html', form=form)
        else:
            video.download()
            filename = video.name + '.mp4'
            download_url = url_for('download', filename=filename,  _external=True)
            return render_template('home.html', form=form, download_url=download_url)

    elif request.method == 'GET':
        return render_template('home.html', form=form)

@app.route('/file/<path:filename>')
def download(filename):
    return send_from_directory('file',
                               filename, as_attachment=True)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
