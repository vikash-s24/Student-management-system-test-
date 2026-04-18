from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
db = SQLAlchemy(app)

# Database Tables
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Database create karna
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    uname = request.form.get('username')
    pwd = request.form.get('password')
    if User.query.filter_by(username=uname).first():
        return "User already exists!"
    new_user = User(username=uname, password=pwd)
    db.session.add(new_user)
    db.session.commit()
    return "Registration Successful! Ab login karein."

@app.route('/login', methods=['POST'])
def login():
    uname = request.form.get('username')
    pwd = request.form.get('password')
    user = User.query.filter_by(username=uname, password=pwd).first()
    if user:
        session['user'] = uname
        return redirect(url_for('dashboard'))
    return "Invalid Credentials!"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Clock-in entry
        new_entry = Attendance(username=session['user'])
        db.session.add(new_entry)
        db.session.commit()
        
    logs = Attendance.query.filter_by(username=session['user']).order_by(Attendance.timestamp.desc()).all()
    return render_template('dashboard.html', user=session['user'], logs=logs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)