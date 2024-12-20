#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, session, Flask, make_response, jsonify
from flask_restful import Resource

# Local imports
from config import app, db, api
# Add your model imports
from models import User, Post, Comment, post_tags, post_genres, Tag, Genre

# Views go here!

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


class Users(Resource):

    def get(self):
        user = User.query.all()
        users = []
        for us in user:
            user_dict = us.to_dict(rules=("-posts",))
            users.append(user_dict)
        return make_response(users, 200)

    def post(self):
        data = request.form
        try:
            new_user = User(
            username=data["username"],
            password=data["password"]
            )
        except:
            return make_response({"Error": "Validation Error"})
        db.session.add(new_user)
        db.session.commit()
        return make_response(new_user.to_dict(rules=("-posts",)), 200)

class Username(Resource):

    def get(self, username):
        if username and username != "null":
            user = User.query.filter(User.username==username).first()
            if user:
                return make_response(user.to_dict(), 200)
            else:
                return make_response({"Error": "User not found"}, 404)
        else:
            return make_response({"Error": "Invalid Username"}, 400)

class User_ID(Resource):
    
    def get(self, id):
        user = User.query.filter(User.id == id).first()
        if user:
            return make_response(user.to_dict(rules=("-posts",)), 200)
        else:
            return make_response({"Error": "User not found"}, 404)
    
    def patch(self, id):
        user = User.query.filter_by(id=id).first()
        data = request.form
        if user:
            try:
                for attr in data:
                    setattr(user, attr, data[attr])
                db.session.commit()
                user_dict = user.to_dict(rules=("-posts",))
                return make_response(user_dict, 202)
            except:
                return make_response({"Error": "Validation Error"}, 400)
        else:
            return make_response({"Error": "User not found"}, 404)

    def delete(self, id):
        user = User.query.filter(User.id==id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response({"Error": "User not found"}, 404)







api.add_resource(Users, '/users')  
api.add_resource(User_ID, '/users/<int:id>')
api.add_resource(Username, '/users/<string:username>')




if __name__ == '__main__':
    app.run(port=5555, debug=True)