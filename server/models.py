from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

from config import db, bcrypt


post_tags = db.Table("post_tags",  
   db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),  
   db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True))

post_genres = db.Table("post_genres",  
   db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),  
   db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True)  
)

class User(db.Model, SerializerMixin):
    __tablename__="users"

    serialize_rules = ("-comments",)


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

 
    posts = db.relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    @validates("username")
    def validate_username(self, key, username):
        if username == User.query.filter(User.username==username).first():
            raise ValueError("Username already taken")
        elif len(username) < 3:
            raise ValueError("Username must have at least 3 characters")
        else:
            return username

    @validates("password")
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError("Password must have at least 8 characters.")
        else:
            return bcrypt.generate_password_hash(password).decode("utf-8")


    def check_password(self, password):  
      return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User: {self.id}, {self.username}"

class Post(db.Model, SerializerMixin):  
   __tablename__="posts"  
  
   serialize_rules = ("-comments","-user",)  
  
   id = db.Column(db.Integer, primary_key=True) 
   image = db.Column(db.String) 
   title = db.Column(db.String)  
   text = db.Column(db.Text)
   user_id = db.Column(db.Integer, db.ForeignKey("users.id")) 
   created_at = db.Column(db.DateTime, server_default=db.func.now())  
   updated_at = db.Column(db.DateTime, onupdate=db.func.now())  

   user = db.relationship("User", back_populates="posts")
   comments = db.relationship("Comment", back_populates='posts', cascade="all, delete-orphan")  
   
   tags = db.relationship("Tag", secondary=post_tags, back_populates="posts")  
   genres = db.relationship("Genre", secondary=post_genres, back_populates="posts")
  
   @validates("title")  
   def validate_title(self, key, title):  
      if not title:  
        raise ValueError("Your work must have a title")  
      else:  
        return title  
  
   @validates("text")  
   def validate_story(self, key, text):  
      if not text:  
        raise ValueError("There is no work to submit")         
      else:  
        return text  
  
   def __repr__(self):  
      return f"<Post: {self.id}, {self.text}>"


class Comment(db.Model, SerializerMixin):
    __tablename__="comments"

    serialize_rules = ("-user.comments", "-text.comments", "post_id", "-posts",)

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    user = db.relationship("User", back_populates='comments', cascade="all")
    posts = db.relationship("Post", back_populates="comments", cascade="all")
    

    @validates("comment")
    def validate_comment(self, key, comment):
        if not comment:
            raise ValueError("There is no comment to submit")
        else:
            return comment

    def __repr__(self):
        return f"<Comment {self.id}>"


class Tag(db.Model, SerializerMixin):

    __tablename__ = "tags"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    posts = db.relationship("Post", secondary=post_tags, back_populates="tags")

class Genre(db.Model, SerializerMixin):

    __tablename__ = "genres"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    posts = db.relationship("Post", secondary=post_genres, back_populates="genres")

