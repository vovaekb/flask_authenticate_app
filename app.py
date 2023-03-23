from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_debugtoolbar import DebugToolbarExtension
import uuid
import jwt
import datetime
from functools import wraps

TOKEN_EXP_TIME = 15

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True

app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

from models import *

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/')
def hello():
    return "<html><body>hello</body></html>"


@app.route('/register', methods=['GET', 'POST'])
def signup_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, balance=100)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    auth = request.authorization
    print('login: ', auth.username)
    print('password: ', auth.password)

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXP_TIME)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/balance')
@token_required
def get_user(current_user):
    return jsonify({'balance': current_user.balance})


if __name__ == '__main__':
    app.run()
