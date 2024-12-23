#!/usr/bin/env python3

from flask import request, session, Flask, make_response, jsonify
from flask_restful import Resource
from config import app, db, api, bcrypt
from models import User, Post, Comment, post_tags, post_genres, Tag, Genre

bcrypt.init_app(app)

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

class Login(Resource):  
    def post(self):  
        try:  
            data = request.form  
            username = data["username"]  
            password = data["password"]  
            user = User.query.filter(User.username==username).first()  
            if user and user.check_password(password):
                session['user_id'] = user.id
                return make_response(user.to_dict(rules=("-posts",)), 200) 
            else:  
                return make_response({"Error": "Invalid username or password"}, 401)  
        except Exception as e:  
            print(e)   
            return make_response({"Error": str(e)}, 500)

class Logout(Resource):

    def delete(self):
        if 'user_id' in session:
            session['user_id'] = None 
            return make_response({'message': 'Successfully logged out'}, 204)
            
class CheckSession(Resource):


    def get(self):
        if 'user_id' in session:  
            user = db.session.get(User, session['user_id'])  
            if user:  
                return make_response(user.to_dict(), 200)  
            else:  
                return make_response({"Error": "User not found"}, 404)  
        else:  
            return make_response({"Error": "Not logged in"}, 401)
 
class Posts(Resource):

    def get(self):
        post = Post.query.all()    
        posts = []    
        for write in post:  
            post_dict = write.to_dict(rules=("-comments",))  
            if write.user:  
                story_dict["user"] = write.user.to_dict(rules=("-posts",))  
            posts.append(post_dict)    
        return make_response(posts, 200)
  
    def post(self):

        if 'user_id' not in session:   
            return make_response({"Error": "Not logged in"}, 401)   
        data = request.form   
        try:   
            new_post = Post(   
               image=data["image"],   
               title=data["title"],   
               text=data["text"],  
               user_id=session["user_id"]  
            )   
            db.session.add(new_post)   
            db.session.commit()   
            return make_response(new_story.to_dict(rules=("-comments",)), 200)   
        except Exception as e:
            print(e)   
            return make_response({"Error": str(e)}, 400)  
  
class Post_ID(Resource):  
    
    def get(self, id):
        post = Post.query.filter(Post.id == id).first()  
        if post:  
            post_dict = post.to_dict(rules=("-comments",))
            if post.user:
                post_dict["user"] = post.user.to_dict(rules=("-posts",))    
            return make_response(post_dict, 200)  
        else:  
            return make_response({"Error": "Post does not exist"}, 404)


    def patch(self, id):

        post = Post.query.filter(Post.id==id).first()  
        if post:  
            data = request.form  
            if data:
                try:
                    for attr in data:  
                        if attr == 'post' and not data[attr]:  
                            return make_response({"Error": "Post cannot be empty"}, 400)  
                        setattr(post, attr, data[attr])  
                    db.session.commit()  
                    return make_response(post.to_dict(rules=("-comments",)), 202)  
                except:  
                    return make_response({"Error": "Validation Error"}, 400)  
            else:  
                return make_response({"Error: No Data Provided"}, 400)  
        else:  
            return make_response({"Error": "Post Does Not Exist"}, 404)

    def delete(self, id):
        post = Post.query.filter(Post.id == id).first()
        if post:
            if "user_id" in session and post.user_id == session["user_id"]:
                db.session.delete(post)
                db.session.commit()
                return make_response({"message": "Post deleted successfully"}, 200)
            else:
                return make_response({"Error": "Not Authorized to delete this story"}, 401)
        else:
            return make_response({"Error": "Post does not exist"}, 404)
  
class PostsByUser(Resource):
      
  
    def get(self, username):

        user = User.query.filter(User.username==username).first()  
        if user:  
            posts = Post.query.filter(Post.user_id==user.id).all()  
            return make_response([post.to_dict(rules=("-user","-comments")) for post in posts], 200)  
        else:  
            return make_response({"Error": "User not found"}, 404)  
  




api.add_resource(Users, '/users')  
api.add_resource(User_ID, '/users/<int:id>')
api.add_resource(Username, '/users/<string:username>')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout') 
api.add_resource(Posts, '/posts')
api.add_resource(Post_ID, '/posts/<int:id>')
api.add_resource(PostsByUser, '/posts/by-user/<string:username>')  





if __name__ == '__main__':
    app.run(port=5555, debug=True)