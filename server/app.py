#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

user_schema = UserSchema()


class Signup(Resource):

    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio'),
            )
            user.password_hash = data.get('password')

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user_schema.dump(user), 201

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            return user_schema.dump(user), 200

        return {'error': '401 Unauthorized'}, 401

class Login(Resource):

    def post(self):
        data = request.get_json()

        user = User.query.filter(User.username == data.get('username')).first()

        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return user_schema.dump(user), 200

        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):

    def delete(self):
        if not session.get('user_id'):
            return {'error': '401 Unauthorized'}, 401

        session['user_id'] = None

        return {}, 204

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
