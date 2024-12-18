from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy

from config import db

class User(db.Model, SerializerMixin):
    __tablename__="users"

    serialize_rules = ("-comments",)


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

 
    stories = db.relationship("Story", back_populates="user", cascade="all, delete-orphan")
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

class Story(db.Model, SerializerMixin):  
   __tablename__="stories"  
  
   serialize_rules = ("-comments","-user",)  
  
   id = db.Column(db.Integer, primary_key=True) 
   image = db.Column(db.String) 
   title = db.Column(db.String)  
   story = db.Column(db.String)
   user_id = db.Column(db.Integer, db.ForeignKey("users.id")) 
   created_at = db.Column(db.DateTime, server_default=db.func.now())  
   updated_at = db.Column(db.DateTime, onupdate=db.func.now())  

   user = db.relationship("User", back_populates="stories")
   comments = db.relationship("Comment", back_populates='stories', cascade="all, delete-orphan")  
  
  
   @validates("title")  
   def validate_title(self, key, title):  
      if not title:  
        raise ValueError("Your work must have a title")  
      else:  
        return title  
  
   @validates("story")  
   def validate_story(self, key, story):  
      if not story:  
        raise ValueError("There is no work to submit")         
      else:  
        return story  
  
   def __repr__(self):  
      return f"<Story: {self.id}, {self.story}>"


class Comment(db.Model, SerializerMixin):
    __tablename__="comments"

    serialize_rules = ("-user.comments", "-story.comments", "story_id", "-stories",)

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    story_id = db.Column(db.Integer, db.ForeignKey("stories.id"))

    user = db.relationship("User", back_populates='comments', cascade="all")
    stories = db.relationship("Story", back_populates="comments", cascade="all")
    

    @validates("comment")
    def validate_comment(self, key, comment):
        if not comment:
            raise ValueError("There is no comment to submit")
        else:
            return comment

    def __repr__(self):
        return f"<Comment {self.id}>"
