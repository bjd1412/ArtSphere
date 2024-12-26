#!/usr/bin/env python3

from flask import request, session, Flask, make_response, jsonify
from flask_restful import Resource
from config import app, db, api, bcrypt
from models import User, Post, Comment, post_tags, post_genres, Tag, Genre

bcrypt.init_app(app)


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
                return make_response(user.to_dict(rules=("-posts",)), 200)
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
        posts = Post.query.all()  
        response = []  
        for post in posts:  
            post_dict = post.to_dict(rules=("-comments", "-user", "-tags", "-genres", "-user_id",))  
            if post.user:
                post_dict["user"] = {"id": post.user.id, "username": post.user.username}  
            if post.tags:  
                post_dict["tags"] = [{"id": tag.id, "name": tag.name} for tag in post.tags]  
            if post.genres:  
                post_dict["genres"] = [{"id": genre.id, "name": genre.name} for genre in post.genres]  
            response.append(post_dict)  
        return make_response(response, 200)

  
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
            return make_response(new_post.to_dict(rules=("-comments", "-user", "-tags", "-genres", "-user_id",)), 200)   
        except Exception as e:
            print(e)   
            return make_response({"Error": str(e)}, 400)  
  
class Post_ID(Resource):  
    
    def get(self, id):
        post = Post.query.filter(Post.id == id).first()  
        if post:  
            post_dict = post.to_dict(rules=("-comments","-user", "-tags", "-genres", "-user_id",))
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
                    return make_response(post.to_dict(rules=("-comments", "-user", "-tags", "-genres", "-user_id",)), 202)  
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
            return make_response([post.to_dict(rules=("-user", "-comments", "-tags", "-genres")) for post in posts], 200)  
        else:  
            return make_response({"Error": "User not found"}, 404)  
  
  
class Comments(Resource):

    def get(self):    
        comments = Comment.query.all()    
        response = [comment.to_dict(rules=("-text", "-user")) for comment in comments]  
        return make_response(response, 200)  

    def post(self):  
        if 'user_id' not in session:  
            return make_response({"Error": "Not logged in"}, 401)  
        data = request.form   
        try:   
            new_comment = Comment(comment=data["comment"], post_id=data["post_id"], user_id=session['user_id'])
            db.session.add(new_comment)   
            db.session.commit()
            return make_response(new_comment.to_dict(rules=("-posts",)), 200)
        except:   
            return make_response({"Error": "Validation Error"}, 400)  
        

class CommentResource(Resource):

    def get(self, id):
        comment = Comment.query.filter_by(id=id).first()  
        if comment:  
            return make_response(comment.to_dict(rules=("-text", "-user")), 200)  
        else:  
            return make_response({"Error": "Comment not found"}, 404)  
  
    def patch(self, id):
        comment = Comment.query.filter(Comment.id == id).first()  
        data = request.form  
        if comment:
            try:  
                for attr in data:  
                    setattr(comment, attr, data[attr])  
                db.session.commit()  
                return make_response(comment.to_dict(), 200)  
            except:  
                return make_response({"Error": "Validation Error"}, 400)  
        else:  
            return make_response({"Error": "Comment not found"}, 404)  
  
    def delete(self, id):
        comment = Comment.query.filter(Comment.id==id).first()  
        if comment:  
            if 'user_id' in session and comment.user_id == session['user_id']:  
                db.session.query(Comment).filter(Comment.id==id).delete()  
                db.session.commit()  
                return make_response({"message": "Comment deleted successfully"}, 200)  
            else:  
                return make_response({"Error": "Not Authorized to delete this comment"}, 401)  
        else:  
            return make_response({"Error": "Comment not found."}, 404)
  
class CommentsByPostID(Resource):  
    def get(self, post_id):
        comments = Comment.query.filter(Comment.post_id == post_id).all()  
        return make_response([comment.to_dict(rules=("-text", "-user",)) for comment in comments], 200)  

class Tags(Resource):

    def get(self):
        tags = Tag.query.all()
        response = [tag.to_dict(rules=("-posts",)) for tag in tags]
        return make_response(response, 200)

    def post(self):
        if 'user_id' not in session:  
            return make_response({"Error": "Not logged in"}, 401)  
        data = request.form   
        try:   
            new_tag = Tag(name=data["name"])
            db.session.add(new_tag)   
            db.session.commit()
            return make_response(new_tag.to_dict(rules=("-posts",)), 200)
        except:   
            return make_response({"Error": "Validation Error"}, 400)  
        
        
    
class Tags_ID(Resource):

    def get(self, id):
        tag = Tag.query.filter(Tag.id == id).first()
        if tag:
            return make_response(tag.to_dict(rules=("-posts",)))
        else:
            return make_response({"Error": "Validation Error"})

    def delete(self, id):
        tag = Tag.query.filter(Tag.id == id).first()
        if tag:
            db.session.delete(tag)
            db.session.commit()
            return make_response({"message": "Tag deleted successfully"}, 200)
        else:
            return make_response({"Error": "Genre does not exist"}, 404)

class Genres(Resource):
    
    def get(self):
        genres = Genre.query.all()
        response = [genre.to_dict(rules=("-posts",)) for genre in genres]
        return make_response(response, 200)

    def post(self):
        if 'user_id' not in session:  
            return make_response({"Error": "Not logged in"}, 401)  
        data = request.form   
        try:   
            new_genre = Genre(name=data["name"])
            db.session.add(new_genre)   
            db.session.commit()
            return make_response(new_genre.to_dict(rules=("-posts",)), 200)
        except:   
            return make_response({"Error": "Validation Error"}, 400)

class Genre_ID(Resource):
    
    def get(self, id):
        genre = Genre.query.filter_by(id=id).first()
        if genre:
            return make_response(genre.to_dict(rules=("-posts",)))
        else:
            return make_response({"Error": "Validation Error"})

    def delete(self, id):
        genre = Genre.query.filter(Genre.id == id).first()
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return make_response({"message": "Genre deleted successfully"}, 200)
        else:
            return make_response({"Error": "Genre does not exist"}, 404)


    



api.add_resource(Users, '/users')  
api.add_resource(User_ID, '/users/<int:id>')
api.add_resource(Username, '/users/<string:username>')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout') 
api.add_resource(Posts, '/posts')
api.add_resource(Post_ID, '/posts/<int:id>')
api.add_resource(PostsByUser, '/posts/by-user/<string:username>')
api.add_resource(Tags, '/tags')
api.add_resource(Tags_ID, '/tags/<int:id>')
api.add_resource(Genres, '/genres')
api.add_resource(Genre_ID, '/genres/<int:id>')
api.add_resource(Comments, '/comments')  
api.add_resource(CommentResource, '/comments/<int:id>')  
api.add_resource(CommentsByPostID, '/comments/by-post/<int:post_id>')  





if __name__ == '__main__':
    app.run(port=5555, debug=True)