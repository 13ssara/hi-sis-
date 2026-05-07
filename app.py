import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, or_
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'profile_pics')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), default='')
    email = db.Column(db.String(120), default='')
    profile_pic = db.Column(db.String(255), default='')
    older_hearts = db.Column(db.Integer, default=0)
    younger_hearts = db.Column(db.Integer, default=0)

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    cover_color = db.Column(db.String(50), default='#d4689f')
    is_public = db.Column(db.Boolean, default=False)
    is_friend_only = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    hearts = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def hearted_by_user(self, user_id):
        return ThreadHeart.query.filter_by(thread_id=self.id, user_id=user_id).first() is not None

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    hearts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def hearted_by_user(self, user_id):
        return CommentHeart.query.filter_by(comment_id=self.id, user_id=user_id).first() is not None

class ThreadHeart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (db.UniqueConstraint('thread_id', 'user_id', name='unique_thread_heart'),)

class CommentHeart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='unique_comment_heart'),)

class PrivateChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_one_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_two_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def other_user(self, user_id):
        return self.user_two_id if self.user_one_id == user_id else self.user_one_id

class PrivateMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('private_chat.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)


def ensure_user_columns():
    with db.engine.begin() as conn:
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info('user')")).fetchall()]
        if 'name' not in columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN name VARCHAR(100) DEFAULT ""'))
        if 'email' not in columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(120) DEFAULT ""'))
        if 'profile_pic' not in columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN profile_pic VARCHAR(255) DEFAULT ""'))
        if 'older_hearts' not in columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN older_hearts INTEGER DEFAULT 0'))
        if 'younger_hearts' not in columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN younger_hearts INTEGER DEFAULT 0'))

with app.app_context():
    db.create_all()
    ensure_user_columns()


def save_profile_picture(file, user_id):
    if not file:
        return None
    filename = secure_filename(file.filename)
    if not filename:
        return None
    name, ext = os.path.splitext(filename)
    final_name = f"user_{user_id}_{int(datetime.now().timestamp())}{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], final_name)
    file.save(save_path)
    return f"profile_pics/{final_name}"


@app.route('/')
def home():
    return render_template('home1.html')

@app.route('/home1')
def home1():
    return render_template('home1.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # In production, use proper password hashing
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home1'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists')
        user = User(username=username, password=password)  # In production, hash the password
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('home1'))
    return render_template('signup.html')

@app.route('/profile')
def profile():
    user = None
    journals = []
    friends = []
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        journals = Journal.query.filter_by(author_id=session['user_id']).all()
        friends = db.session.query(User).join(Friend, or_(
            (Friend.user_id == session['user_id']) & (Friend.friend_id == User.id),
            (Friend.user_id == User.id) & (Friend.friend_id == session['user_id'])
        )).all()
    return render_template('profile.html', user=user, journals=journals, journal_count=len(journals), friends=friends)

@app.route('/save_profile', methods=['POST'])
def save_profile():
    username = request.form['username']
    password = request.form['password']
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    avatar_file = request.files.get('avatar')

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user:
            return redirect(url_for('login'))
        if username != user.username and User.query.filter_by(username=username).first():
            return render_template('profile.html', error='Username already exists', user=user, journals=Journal.query.filter_by(author_id=user.id).all(), journal_count=len(Journal.query.filter_by(author_id=user.id).all()))
        user.username = username
        if password:
            user.password = password
        user.name = name
        user.email = email
        if avatar_file and avatar_file.filename:
            profile_path = save_profile_picture(avatar_file, user.id)
            if profile_path:
                user.profile_pic = profile_path
        db.session.commit()
        session['username'] = user.username
        return redirect(url_for('profile'))

    if not password:
        return render_template('profile.html', error='Password is required to create an account.', user=None, journals=[], journal_count=0)

    if User.query.filter_by(username=username).first():
        return render_template('profile.html', error='Username already exists', user=None, journals=[], journal_count=0)

    user = User(username=username, password=password, name=name, email=email)
    db.session.add(user)
    db.session.commit()
    if avatar_file and avatar_file.filename:
        profile_path = save_profile_picture(avatar_file, user.id)
        if profile_path:
            user.profile_pic = profile_path
            db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return redirect(url_for('profile'))

@app.route('/journal')
def journal():
    return redirect(url_for('library'))

@app.route('/journal/new')
def journal_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('journal_editor.html', journal=None)

@app.route('/journal/<int:journal_id>')
def journal_edit(journal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    journal = Journal.query.get_or_404(journal_id)
    if journal.author_id != session['user_id']:
        return redirect(url_for('journal_view', journal_id=journal_id))
    return render_template('journal_editor.html', journal=journal)

@app.route('/journal/<int:journal_id>/view')
def journal_view(journal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    journal = Journal.query.get_or_404(journal_id)
    return render_template('journal_view.html', journal=journal)

@app.route('/journal/save', methods=['POST'])
def journal_save():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    try:
        data = request.get_json()
        journal_id = data.get('id')
        
        if journal_id:
            journal = Journal.query.get(journal_id)
            if not journal or journal.author_id != session['user_id']:
                return jsonify({'error': 'Journal not found or access denied'}), 404
        else:
            journal = Journal(author_id=session['user_id'])
        
        journal.title = data.get('title', 'Untitled')
        journal.content = data.get('content', '')
        journal.cover_color = data.get('cover_color', '#d4689f')
        journal.is_public = data.get('is_public', False)
        journal.is_friend_only = data.get('is_friend_only', False)
        
        db.session.add(journal)
        db.session.commit()
        
        return jsonify({'success': True, 'journal_id': journal.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/library')
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    public_journals = Journal.query.filter_by(is_public=True).all()
    private_journals = Journal.query.filter_by(author_id=user_id, is_public=False, is_friend_only=False).all()
    friend_journals = Journal.query.filter_by(is_friend_only=True).all()  # For now, show all friend journals
    return render_template('journal.html', public_journals=public_journals, private_journals=private_journals, friend_journals=friend_journals)


@app.route('/community')
def community():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    public_threads = Thread.query.filter_by(is_public=True).order_by(Thread.created_at.desc()).all()
    private_chats = PrivateChat.query.filter(
        or_(PrivateChat.user_one_id == user_id, PrivateChat.user_two_id == user_id)
    ).order_by(PrivateChat.created_at.desc()).all()
    chat_previews = []
    for chat in private_chats:
        friend_id = chat.other_user(user_id)
        friend = User.query.get(friend_id)
        last_message = PrivateMessage.query.filter_by(chat_id=chat.id).order_by(PrivateMessage.created_at.desc()).first()
        chat_previews.append({
            'chat': chat,
            'friend': friend,
            'last_message': last_message,
        })
    return render_template('community.html', public_threads=public_threads, chat_previews=chat_previews)

@app.route('/community/thread/new', methods=['GET', 'POST'])
def community_thread_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_public = request.form.get('is_public') == 'public'
        if title and content:
            thread = Thread(title=title, content=content, author_id=session['user_id'], is_public=is_public)
            db.session.add(thread)
            db.session.commit()
            return redirect(url_for('community_thread_view', thread_id=thread.id))
    return render_template('community_thread_new.html')

@app.route('/community/thread/<int:thread_id>', methods=['GET', 'POST'])
def community_thread_view(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    thread = Thread.query.get_or_404(thread_id)
    if not thread.is_public and thread.author_id != session['user_id']:
        return redirect(url_for('community'))
    comments = Comment.query.filter_by(thread_id=thread.id).order_by(Comment.created_at.asc()).all()
    if request.method == 'POST':
        comment_content = request.form.get('comment', '').strip()
        if comment_content:
            comment = Comment(thread_id=thread.id, content=comment_content, author_id=session['user_id'])
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('community_thread_view', thread_id=thread.id))
    return render_template('community_thread_view.html', thread=thread, comments=comments)

@app.route('/community/thread/<int:thread_id>/heart', methods=['POST'])
def community_thread_heart(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    thread = Thread.query.get_or_404(thread_id)
    user = User.query.get(session['user_id'])
    if not thread.hearted_by_user(user.id):
        db.session.add(ThreadHeart(thread_id=thread.id, user_id=user.id))
        thread.hearts += 1
        thread_author = User.query.get(thread.author_id)
        if thread_author:
            thread_author.younger_hearts += 1
        db.session.commit()
    return redirect(url_for('community_thread_view', thread_id=thread.id))

@app.route('/comment/<int:comment_id>/heart', methods=['POST'])
def comment_heart(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    user = User.query.get(session['user_id'])
    if not comment.hearted_by_user(user.id):
        db.session.add(CommentHeart(comment_id=comment.id, user_id=user.id))
        comment.hearts += 1
        comment_author = User.query.get(comment.author_id)
        if comment_author:
            comment_author.older_hearts += 1
        db.session.commit()
    return redirect(url_for('community_thread_view', thread_id=comment.thread_id))

@app.route('/community/chat/new', methods=['GET', 'POST'])
def community_chat_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    error = None
    friends = db.session.query(User).join(Friend, or_(
        (Friend.user_id == session['user_id']) & (Friend.friend_id == User.id),
        (Friend.user_id == User.id) & (Friend.friend_id == session['user_id'])
    )).all()
    if request.method == 'POST':
        friend_username = request.form.get('friend_username', '').strip()
        if friend_username:
            friend = User.query.filter_by(username=friend_username).first()
            if not friend or friend.id == session['user_id']:
                error = 'Enter a valid friend username.'
            else:
                chat = PrivateChat.query.filter(
                    or_(
                        (PrivateChat.user_one_id == session['user_id']) & (PrivateChat.user_two_id == friend.id),
                        (PrivateChat.user_two_id == session['user_id']) & (PrivateChat.user_one_id == friend.id)
                    )
                ).first()
                if not chat:
                    chat = PrivateChat(user_one_id=session['user_id'], user_two_id=friend.id)
                    db.session.add(chat)
                    db.session.commit()
                return redirect(url_for('community_chat_view', chat_id=chat.id))
    return render_template('community_chat_new.html', error=error, friends=friends)

@app.route('/community/chat/<int:chat_id>', methods=['GET', 'POST'])
def community_chat_view(chat_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    chat = PrivateChat.query.get_or_404(chat_id)
    if session['user_id'] not in (chat.user_one_id, chat.user_two_id):
        return redirect(url_for('community'))
    friend_id = chat.other_user(session['user_id'])
    friend = User.query.get(friend_id)
    messages = PrivateMessage.query.filter_by(chat_id=chat.id).order_by(PrivateMessage.created_at.asc()).all()
    
    # Get all chats for sidebar
    user_chats = PrivateChat.query.filter(
        or_(PrivateChat.user_one_id == session['user_id'], PrivateChat.user_two_id == session['user_id'])
    ).all()
    all_chats = []
    for c in user_chats:
        f_id = c.other_user(session['user_id'])
        f = User.query.get(f_id)
        last_msg = PrivateMessage.query.filter_by(chat_id=c.id).order_by(PrivateMessage.created_at.desc()).first()
        all_chats.append({'chat': c, 'friend': f, 'last_message': last_msg})
    
    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        if content:
            message = PrivateMessage(chat_id=chat.id, sender_id=session['user_id'], content=content)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('community_chat_view', chat_id=chat.id))
    return render_template('community_chat.html', chat=chat, friend=friend, messages=messages, all_chats=all_chats)

@app.route('/add-friend', methods=['POST'])
def add_friend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    friend_username = request.form.get('friend_username', '').strip()
    if friend_username:
        friend = User.query.filter_by(username=friend_username).first()
        if friend and friend.id != session['user_id']:
            existing = Friend.query.filter(
                or_(
                    (Friend.user_id == session['user_id']) & (Friend.friend_id == friend.id),
                    (Friend.user_id == friend.id) & (Friend.friend_id == session['user_id'])
                )
            ).first()
            if not existing:
                friendship = Friend(user_id=session['user_id'], friend_id=friend.id)
                db.session.add(friendship)
                db.session.commit()
    return redirect(url_for('profile'))

@app.route('/friends')
def friends():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_friends = db.session.query(User).join(Friend, or_(
        (Friend.user_id == session['user_id']) & (Friend.friend_id == User.id),
        (Friend.user_id == User.id) & (Friend.friend_id == session['user_id'])
    )).all()
    return render_template('friends.html', friends=user_friends)


if __name__ == '__main__':
    app.run(debug=True)