from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import json



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Load users from JSON file
def load_users():
    with open('users.json') as file:
        return json.load(file)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect(url_for('index'))

        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        print(f'{session["username"]} connected')
    else:
        return False  # Reject connection if user is not logged in

@socketio.on('new_message')
def handle_message(message):
    if 'username' in session:
        emit('new_message', {'username': session['username'], 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
