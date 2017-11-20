# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, send_file, \
    Response, make_response, g
from models import db, User, Youtube, Convert
from forms import GenerateForm, SearchUserForm, ConvertForm, SearchVideoForm, SignupForm, LoginForm
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import timedelta
from download_video import Download, Get_user_videos, Search_video
from convert import Convert_to_PDF
from send_mail import send_mail
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['YT_DATABASE_URL']
#app.config['SQLALCHEMY_NATIVE_UNICODE'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.login_message = "Please login to access this page."
login_manager.init_app(app)


@app.before_request
def make_session_permant():
    g.next = None
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.before_request
def before_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint != 'confirm' \
        and request.endpoint != 'logout' \
        and request.endpoint != 'unconfirmed':
        return redirect(url_for('unconfirmed'))


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('home'))
    return render_template('unconfirmed.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    if current_user.is_authenticated:
        new_video = Youtube(video_name, url, current_user.id)
        db.session.add(new_video)
        db.session.commit()
    if filename not in files:
        video.download(extension, resolution, video_name)
        download_url = url_for('downloadfile', filename=filename, _external=True)
        return render_template('download.html', download_url=download_url)
    else:
        download_url = url_for('downloadfile', filename=filename, _external=True)
        return render_template('download.html', download_url=download_url)


@app.route('/youtube_history', methods=['GET'])
@login_required
def youtube_history():
    download_history = current_user.youtube
    return render_template('youtube_history.html', download_history=download_history)


@app.route('/convert_history', methods=['GET'])
@login_required
def convert_history():
    convert_history = current_user.convert
    return render_template('convert_history.html', convert_history=convert_history)


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    form = ConvertForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('convert.html', form=form)
        else:
            url = form.web_url.data
            web_title, new_url = Convert_to_PDF(url).get_name()
            if new_url == 'invalid':
                return render_template('convert.html', form=form, invalid=True)
            result = Convert_to_PDF(url).convert_page_to_pdf()
            if result == True:
                if current_user.is_authenticated:
                    new_convert = Convert(web_title, new_url, current_user.id)
                    db.session.add(new_convert)
                    db.session.commit()
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


# ---------------------------------User control part---------------------------------------
# -----------------------------------------------------------------------------------------
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template("signup.html", form=form)
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash("Email has been used, please use another one!")
            return render_template("signup.html", form=form)
        else:
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            token = newuser.generate_confirmation_token()
            send_mail(newuser.email, newuser.firstname, token)
            return render_template('confirm.html', user=newuser.firstname)
    elif request.method == 'GET':
        return render_template("signup.html", form=form)


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('home'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
        return render_template('welcome.html')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user, form.remember_me.data)
                return redirect(session['next'] or url_for('home'))
            else:
                flash('Email address or password incorrect!')
                return render_template('login.html', form=form)
    elif request.method == 'GET':
        session['next'] = request.args.get('next')
        return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


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
    app.run('0.0.0.0', port=80)
