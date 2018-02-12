# encoding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, send_file, \
    Response, make_response, g
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized
from models import db, User, Youtube, Convert, OAuth
from forms import GenerateForm, SearchUserForm, ConvertForm, SearchVideoForm, SignupForm, LoginForm, OAuthForm
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import timedelta
from download_video import Download, Get_user_videos, Search_video
from convert import Convert_to_PDF
from send_mail import send_mail
import unicodedata
from werkzeug.urls import url_quote
import os, config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.login_message = "该页面需要登陆"
login_manager.init_app(app)
github_blueprint = make_github_blueprint(client_id='c554930667ddac2389f5',
                                         client_secret='563713ea1c1358b15441b12b040a445b576b1ea3', scope=['user:email'])
app.register_blueprint(github_blueprint, url_prefix='/login')
github_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

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
        and request.endpoint != 'unconfirmed'\
        and request.endpoint != 'get_github':
        return redirect(url_for('unconfirmed'))


@app.context_processor
def get_avatar_url():
    if session.get('avatar_url'):
        return dict(avatar_url=session.get('avatar_url'))
    return dict(avatar_url='')


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('index'))
    return render_template('unconfirmed.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/get_github')
def get_github():
    if not github.authorized:
        return redirect(url_for('github.login'))

    account_info = github.get('/user/emails')

    if account_info.ok:
        account_info_json = account_info.json()[0]
        print(account_info_json)

        return '<h1>Your Github name is {}'.format(account_info_json['email'])

    return '<h1>Request failed!</h1>'

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    get_account = blueprint.session.get('/user')
    get_email = blueprint.session.get('/user/emails')
    if get_account.ok and get_email.ok:
        account_info_json = get_account.json()
        email_info = get_email.json()[0]
        username = account_info_json['login']
        avatar_url = account_info_json['avatar_url']
        email = email_info['email']
        session['avatar_url'] = avatar_url

        user_q = User.query.filter_by(email=email).first()
        if user_q is not None:
            login_user(user_q)
        else:
            print('else')
            session['username'] = username
            session['email'] = email
            return redirect(url_for('set_account'))
    else:
        print('failed')

@app.route('/set_account', methods=['GET', 'POST'])
def set_account():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = OAuthForm()
    username = session['username']
    email = session['email']
    if request.method == 'POST':
        if not form.validate():
            return render_template('set_account.html', form=form, username=username)
        else:
            password1 = form.password1.data
            password2 = form.password2.data
            if password1 != password2:
                flash("两次密码输入不一致，请检查后重新输入")
                return render_template("set_account.html", form=form, username=username)
            else:
                user = User(username, email, password1)
                user.confirmed = True
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('set_account.html', form=form, username=username)



#--------Direct download from URL----------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/youtube', methods=['GET', 'POST'])
def youtube():
    form = GenerateForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('youtube.html', form=form)
        else:
            url = form.youtube_url.data
            video = Download(url)
            quality = video.get_resolution()
            name = video.get_name()
            return render_template('youtube.html', form=form, quality=quality, name=name, url=url)

    elif request.method == 'GET':
        return render_template('youtube.html', form=form)

@app.route('/download', methods=['GET'])
def download():
    extension, resolution, url = request.args.get('quality').split('&')
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
    try:
        filename = filename.encode('latin-1')
    except UnicodeEncodeError:
        filenames = {
            'filename': unicodedata.normalize('NFKD', filename).encode('latin-1', 'ignore'),
            'filename*': "UTF-8''{}".format(url_quote(filename)),
        }
    else:
        filenames = {'filename': filename}

    response.headers.set('Content-Disposition', 'attachment', **filenames)
    return response


# ---------------------------------User control part---------------------------------------
# -----------------------------------------------------------------------------------------
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template("signup.html", form=form)
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        # user_q = User.query.filter_by(username=username).first()
        email_q = User.query.filter_by(email=email).first()
        # if user_q is not None:
        #     flash("用户名已被使用，请重新输入")
        #     return render_template("signup.html", form=form)
        if email_q is not None:
            flash("邮箱已被使用，请重新输入!")
            return render_template("signup.html", form=form)
        if password1 != password2:
            flash("两次密码输入不一致，请检查后重新输入")
            return render_template("signup.html", form=form)
        else:
            newuser = User(username, email, password1)
            db.session.add(newuser)
            db.session.commit()
            token = newuser.generate_confirmation_token()
            send_mail(newuser.email, newuser.username, token)
            return render_template('confirm.html', user=newuser.username)
    elif request.method == 'GET':
        return render_template("signup.html", form=form)


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index'))
    if current_user.confirm(token):
        flash('你已经成功激活了你的账户！')
        return render_template('welcome.html')
    else:
        flash('激活链接无效或已过期，请重试。')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
                return redirect(session.get('next') or url_for('welcome_back'))
            else:
                flash('邮箱或密码不正确！')
                return render_template('login.html', form=form)
    elif request.method == 'GET':
        session['next'] = request.args.get('next')
        return render_template('login.html', form=form)


@app.route('/welcome_back')
@login_required
def welcome_back():
    return render_template('welcome_back.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.template_filter('get_emb_url')
def get_emb_url(url):
    vid = url.split('?v=')[1]
    emb_url = "https://www.youtube.com/embed/" + vid
    return emb_url


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
    app.run('0.0.0.0', port=8080,debug=True)
