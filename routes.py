# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, send_file, Response
from forms import GenerateForm, SearchUserForm, DownloadForm
from datetime import timedelta
from download_video import Download, Get_user_videos
import os
import time

app = Flask(__name__)

@app.before_request
def make_session_permant():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

app.secret_key = 'development-key'



#--------Direct download from URL----------
@app.route('/', methods=['GET', 'POST'])
def home():
    form = GenerateForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('home.html', form=form)
        else:
            url = form.youtube_url.data
            video = Download(url)
            quality = video.get_resolution()
            extension = quality[0]
            resolution = quality[1]
            return render_template('home.html', form=form, quality=quality, url=url)
            #return redirect(url_for('download', quality=all_resolutions))

            '''
            files = os.listdir('file/')
            video = Download(form.youtube_url.data)
            video_name = video.get_name() + '.mp4'
            if video_name not in files:
                video.download()
                download_url = url_for('downloadfile', filename=video_name,  _external=True)
                return render_template('home.html', form=form, download_url=download_url)
            else:
                download_url = url_for('downloadfile', filename=video_name, _external=True)
                return render_template('home.html', form=form, download_url=download_url)
            '''

    elif request.method == 'GET':
        return render_template('home.html', form=form)

@app.route('/download', methods=['GET'])
def download():
    extension = request.args.get('extension')
    resolution = request.args.get('resolution')
    url = request.args.get('url')
    files = os.listdir('file/')
    video = Download(url)
    video_name = video.get_name() + '.' + extension
    if video_name not in files:
        video.download(extension, resolution)
        download_url = url_for('downloadfile', filename=video_name, _external=True)
        return render_template('download.html', download_url=download_url)
    else:
        download_url = url_for('downloadfile', filename=video_name, _external=True)
        return render_template('download.html', download_url=download_url)


    '''
    form = DownloadForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('download.html', form=form)
        else:

            return render_template('download.html', form=form)

    elif request.method == 'GET':
        return render_template('download.html', form=form)

    '''



#--------Search user acoount----------
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchUserForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('search.html', form=form)
        else:
            user = Get_user_videos(form.user_acct.data)
            user.get_infos()
            group = user.group
            return render_template('search.html', form=form, video_list=group)

    elif request.method == 'GET':
        return render_template('search.html', form=form)





@app.route('/file/<path:filename>')
def downloadfile(filename):
    return send_from_directory('file',
                               filename, as_attachment=True)

@app.route('/<filename>')
def music(filename):
    return render_template('music.html',
                        title=filename,
                        music_file=filename)


'''
#---------Demo for progress---------
@app.route('/page')
def get_page():
    return send_file('templates/progress.html')

@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x < 100:
            print(x)
            x = x + 1
            time.sleep(0.2)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')
'''





@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080)
