# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, send_file, \
    Response, make_response
from forms import GenerateForm, SearchUserForm, ConvertForm, SearchVideoForm
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import timedelta
from download_video import Download, Get_user_videos, Search_video
from convert import convert_page_to_pdf
import os
import time

app = Flask(__name__)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.login_message = "Please login to access this page."
login_manager.init_app(app)


@app.before_request
def make_session_permant():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
'''

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
            name = video.get_name()
            return render_template('home.html', form=form, quality=quality, name=name, url=url)
            #return redirect(url_for('download', quality=all_resolutions))

    elif request.method == 'GET':
        return render_template('home.html', form=form)

@app.route('/download', methods=['GET'])
def download():
    extension = request.args.get('extension')
    resolution = request.args.get('resolution')
    url = request.args.get('url')
    files = os.listdir('file/')
    video = Download(url)
    video_name = (video.get_name() + '(%s)') % resolution
    filename = video_name + '.' + extension
    if filename not in files:
        video.download(extension, resolution, video_name)
        download_url = url_for('downloadfile', filename=filename, _external=True)
        return render_template('download.html', download_url=download_url)
    else:
        download_url = url_for('downloadfile', filename=filename, _external=True)
        return render_template('download.html', download_url=download_url)

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    form = ConvertForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('convert.html', form=form)
        else:
            url = form.web_url.data
            result = convert_page_to_pdf(url)
            if result == True:
                pdf_link = url_for('downloadfile', filename='output.pdf', _external=True)
                return render_template('convert.html', form=form, pdf_link=pdf_link)
            else:
                return render_template('convert.html', form=form, failed=True)

    elif request.method == 'GET':
        return render_template('convert.html', form=form)



#--------Search user acoount----------
@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    form = SearchUserForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('search_user.html', form=form)
        else:
            user = Get_user_videos(form.user_acct.data)
            user.get_infos()
            group = user.group
            return render_template('search_user.html', form=form, video_list=group)

    elif request.method == 'GET':
        return render_template('search_user.html', form=form)


@app.route('/search_video', methods=['GET', 'POST'])
def search_video():
    form = SearchVideoForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('search_vid.html', form=form)
        else:
            video = Search_video()
            video.search(form.keyword.data)
            video_group = video.vid_group
            return render_template('search_vid.html', form=form, search_result=video_group)

    elif request.method == 'GET':
        return render_template('search_vid.html', form=form)




#---------Download files--------------
@app.route('/file/<path:filename>')
def downloadfile(filename):
    response = make_response(send_from_directory('file',
                               filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response

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


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080)
