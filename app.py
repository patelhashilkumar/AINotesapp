from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
db = SQLAlchemy(app)

# Load API key from environment variable
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("Warning: GEMINI_API_KEY environment variable is not set")
    api_key = "dummy_key"  # Fallback for development
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')  # Using the correct model name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Note', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='uncategorized')
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'summary': self.summary,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_summary(content):
    """Generate a summary of the note content using Gemini API"""
    try:
        response = model.generate_content(f"Summarize this text in one or two sentences: {content}")
        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    notes = Note.query.filter_by(user_id=session['user_id']).order_by(Note.created_at.desc()).all()
    return render_template('index.html', notes=notes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/notes', methods=['POST'])
@login_required
def create_note():
    data = request.json
    summary = generate_summary(data['content'])
    
    note = Note(
        title=data['title'],
        content=data['content'],
        category=data.get('category', 'uncategorized'),
        summary=summary,
        user_id=session['user_id']
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201

@app.route('/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    data = request.json
    
    note.title = data['title']
    note.content = data['content']
    note.category = data.get('category', note.category)
    
    if note.content != data['content']:
        note.summary = generate_summary(data['content'])
    
    db.session.commit()
    return jsonify(note.to_dict())

@app.route('/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return '', 204

@app.route('/notes/search')
@login_required
def search_notes():
    query = request.args.get('q', '')
    notes = Note.query.filter(
        Note.user_id == session['user_id'],
        (Note.title.ilike(f'%{query}%')) |
        (Note.content.ilike(f'%{query}%')) |
        (Note.summary.ilike(f'%{query}%'))
    ).order_by(Note.created_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@app.route('/notes/<int:note_id>/summarize', methods=['POST'])
@login_required
def regenerate_summary(note_id):
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    note.summary = generate_summary(note.content)
    db.session.commit()
    return jsonify(note.to_dict())

@app.route('/notes/reorder', methods=['POST'])
@login_required
def reorder_notes():
    data = request.json
    order = data.get('order', [])
    
    for index, note_id in enumerate(order):
        note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
        if note:
            note.order = index
    
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))