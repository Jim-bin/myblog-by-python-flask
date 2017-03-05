from collections import OrderedDict
import os
from datetime import datetime
from math import ceil
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, session, redirect, url_for, render_template, flash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

'''Configuration - Debug can be removed for production use'''
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(basedir, 'data.sqlite'),
    SECRET_KEY='not a password',
    DEBUG=True,
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True,
    USERNAME='admin',
    PASSWORD='admin',
    PER_PAGE=5
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db = SQLAlchemy(app)

'''Data model - one (Post) to many (Comment)'''
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, index=True)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.title 

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    reply = db.Column(db.Text, nullable=False)
    replytime = db.Column(db.DateTime, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return '<Comment %r>' % self.reply

'''index page showing all posts paginated'''
@app.route('/')
def show_entries():
    page=request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(page,per_page=app.config['PER_PAGE'],error_out=False)
    entries=pagination.items
    entries_all = Post.query.all()

    tagss = []
    for i in entries_all:
        tagss.append(i.tag.capitalize())
    tags = set(tagss)

    tag_num = []
    for i in tags:
        count_tag = tagss.count(i)
        tag_num.append(count_tag)

    d = dict(zip(tags, tag_num))
    dict_tag = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    return render_template('show_entries.html', entries=entries, pagination=pagination, 
        tags=tags, tag_num=tag_num, dict_tag=dict_tag)

@app.route('/tags/<tag>')
def show_tags(tag):
    page=request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(tag=tag).order_by(Post.id.desc()).paginate(page,per_page=app.config['PER_PAGE'],error_out=False)
    entries=pagination.items

    entries_all = Post.query.all()

    tagss = []
    for i in entries_all:
        tagss.append(i.tag.capitalize())
    tags = set(tagss)

    tag_num = []
    for i in tags:
        count_tag = tagss.count(i)
        tag_num.append(count_tag)

    d = dict(zip(tags, tag_num))
    dict_tag = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    return render_template('show_entries.html', entries=entries, pagination=pagination, dict_tag=dict_tag)

'''url for each post and its guest comments'''
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    # comments = post.comments.all()
    comments = post.comments.order_by(Comment.id.desc())
    if request.method == 'POST':
        addcomments = Comment(reply=request.form['reply'], post=post, replytime=datetime.now())
        db.session.add(addcomments)
        # return redirect(url_for('show_entries'))

    entries_all = Post.query.all()

    tagss = []
    for i in entries_all:
        tagss.append(i.tag.capitalize())
    tags = set(tagss)

    tag_num = []
    for i in tags:
        count_tag = tagss.count(i)
        tag_num.append(count_tag)

    d = dict(zip(tags, tag_num))
    dict_tag = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    return render_template('post.html', post=post, comments=comments, dict_tag=dict_tag)

'''add a post if the admin is logged in'''
@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        post=Post(title=request.form['title'], tag=request.form['tag'].capitalize(), text=request.form['text'], timestamp=datetime.now())
        db.session.add(post)
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))
    return render_template('add.html')

'''delete a post if admin is logged in'''
@app.route('/delete/<int:id>')
def delete_entry(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        flash('The post has been deleted')
        return redirect(url_for('show_entries'))

@app.route('/update_entry/<int:id>')
def update_entry(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    post = Post.query.get_or_404(id)
    id = post.id
    title = post.title
    text = post.text
    tag = post.tag
    return render_template('update.html', id=id, title=title, text=text, tag=tag)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        post = Post.query.get_or_404(id)
        post.title = request.form['title']
        post.text = request.form['text']
        post.tag = request.form['tag'].capitalize()
        post.timestamp = datetime.now()
        db.session.add(post)
        db.session.commit()

        # post=Post(title=request.form['title'], tag=request.form['tag'].capitalize(), text=request.form['text'], timestamp=datetime.now())
        # db.session.add(post)
        # db.session.commit()

        flash('The post has been updated')
        return redirect(url_for('show_entries'))
    else:       
        return render_template('update.html')


'''login page with error message'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

'''log admin out; return None if key 'logged_in' doesn't exsit'''
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()