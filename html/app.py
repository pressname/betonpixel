import os
import sys

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from authlib.integrations.flask_client import OAuth
from functools import wraps

from dotenv import load_dotenv


from models import db
from db_helper import get_user_from_users, add_user_to_users
from utils import sanitize_string

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)
# Create the database tables
with app.app_context():
    db.create_all()

# Configure flask app with parameters from .env file
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Cookie flags
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'lax'


oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:name'},
)


def login_required(view):
    """
    Decorator function to protect routes that require authentication.
    Redirects unauthenticated users to the login page.
    """
    @wraps(view)
    def decorated_view(*args, **kwargs):
        # Redirect to the login route if the user do not have a session
        if not session.get('token'):
            return redirect(url_for('login', next=request.url))

        # If username from session don't dissolve to a user obj, return index page
        user = get_user_from_users(session['user_name'])
        if not user:
            return redirect(url_for('index'))

        session['user_role'] = user.role.id
        return view(*args, **kwargs)
    return decorated_view

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return github.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = github.authorize_access_token()
    if not token: 
        return error_page("Login failed")

    user = github.get('https://api.github.com/user', token=token)
    if not user.ok:
        return error_page("Failed to fetch user data from GitHub")

    user_data = user.json()
    session['user_data'] = user_data
    session['user_name'] = user_data['login']
    
    user = get_user_from_users(session['user_name'])

    if user:                                            # Authenticate existing user
        session['token'] = token
        session['user_role'] = user.role.id
        return redirect(url_for('dashboard'))
    else:                                               # Add a new user
        if add_user_to_users(session['user_name']):
            return redirect(url_for('dashboard'))
        return error_page("User couldn't be added to the database")


@app.route('/logout', methods=['GET'])
def logout():
    if session.get('token'):
        session.clear()
        return render_template('logout.html')
    else:
        return error_page("You are already logged out")

@login_required
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/stats', methods=['GET'])
def stats():
    return None

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowd_chars=True)
    return render_template('errors/error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")