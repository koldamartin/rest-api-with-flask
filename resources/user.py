from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel(username = user_data["username"],
                         password=pbkdf2_sha256.hash(user_data["password"])
                         # this will hash the password, if it was returned. it would be unreadable
                         )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created"}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200


@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        # user = UserModel.query.filter(
        #     UserModel.username == user_data["username"]
        # ).first()
        user = UserModel.query.filter_by(username=user_data["username"]).first()

        if user:
            print(f"Retrieved user: {user.username}, password: {user.password}")
            if pbkdf2_sha256.verify(user_data["password"], user.password):
                print("Password verified")

                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(identity=user.id)

                return {"access_token": access_token, "refresh_token": refresh_token}
        else:
            print("User not found")
            abort(401, message="Invalid credentials")


@blp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt().get("jti")
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200
