
import paramiko
import subprocess

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from flask_restful import Resource, reqparse
from models.user import UserModel
from blacklist import BLACKLIST



_user_paser = reqparse.RequestParser()
_user_paser.add_argument('username',
                         type=str,
                         required=True,
                         help="This field cannot be blank"
                         )
_user_paser.add_argument('password',
                         type=str,
                         required=True,
                         help="This field cannot be blank"
                         )


class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = _user_paser.parse_args()
        host = "172.250.25.75"
        try:
            client = paramiko.client.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=data['username'], password=data['password'])
            print("login Success !")
            access_token = create_access_token(identity="123", fresh=True)
            refresh_token = create_refresh_token("123")
            return{
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        except Exception as e:
            return {'message': 'Invalid credentials'}, 401
        finally:
            client.close()



        


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        print(jti)
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)
        return {'access_token':new_token},200