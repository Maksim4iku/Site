from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from data import db_session, posts_api
from data.users import User
from data.posts import Posts
from data.messages import Message
from forms.message import MessageForm
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.posts import PostsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
import os

import datetime
import jinja2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(posts_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/posts_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def posts_delete(id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.id == id,
                                        Posts.user == current_user
                                        ).first()
    if posts:
        db_sess.delete(posts)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.errorhandler(404)
def abort_if_posts_not_found(posts_id):
    session = db_session.create_session()
    posts = session.query(Posts).get(posts_id)
    if not posts:
        abort(404, message=f"Posts {posts_id} not found")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):
    form = PostsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id,
                                            Posts.user == current_user
                                            ).first()
        if posts:
            form.title.data = posts.title
            form.content.data = posts.content
            form.is_private.data = posts.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id,
                                            Posts.user == current_user
                                            ).first()
        if posts:
            posts.title = form.title.data
            posts.content = form.content.data
            posts.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('posts.html',
                           title='Редактирование новости',
                           form=form
                           )



@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(Posts).filter(
            (Posts.user == current_user) | (Posts.is_private != True))
    else:
        posts = db_sess.query(Posts).filter(Posts.is_private != True)
    return render_template("index.html", posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def add_posts():
    form = PostsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = Posts()
        posts.title = form.title.data
        posts.content = form.content.data
        posts.is_private = form.is_private.data
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Добавление новости',
                           form=form)


@app.route('/messager', methods=['GET', 'POST'])
@login_required
def messager():
    db_sess = db_session.create_session()
    messages = db_sess.query(Message).filter(
        Message.from_user_id == current_user.id or Message.where_user_id == current_user.id)
    for i in messages:
        print(i)
    return render_template('messager.html', messages=messages)


@app.route('/new_message', methods=['GET', 'POST'])
@login_required
def add_message():
    form = MessageForm()
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id != current_user.id)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        message = Message()
        message.text = form.text.data
        message.from_user_id = current_user.id
        message.where_user_id = form.id_user.data
        db_sess.add(message)
        db_sess.commit()
        return redirect("/messager")
    return render_template('new_message.html', users=users, form=form)


@login_required
def add_posts():
    form = PostsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = Posts()
        posts.title = form.title.data
        posts.content = form.content.data
        posts.is_private = form.is_private.data
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Добавление новости',
                           form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


if __name__ == '__main__':
    main()
