from flask import Flask, jsonify
from flask_restful import  Api
from flask_jwt_extended import JWTManager

from resources.user import (
    UserLogin,
    TokenRefresh,
    UserLogout
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'secretKey'
api = Api(app)


app.config['JWT_SECRET_KEY'] = 'howhow'  # we can also use app.secret like before, Flask-JWT-Extended can recognize both
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens

@app.before_first_request
def create_tables():
    db.create_all()


# jwt = JWT(app, authenticate, identity)
jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin':True}
    return {'is_admin':False}

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expored ..',
        'error' : 'token_expired'
    }),401

@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401



@app.route("/")
def home():
    return "<h1>Hello World</h1>"


api.add_resource(UserLogin,'/login')
api.add_resource(TokenRefresh,'/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True, host='0.0.0.0')