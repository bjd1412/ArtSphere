#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Post, Comment, post_tags, post_genres, Tag, Genre

if __name__ == '__main__':
    fake = Faker()
    with app.app_context():
        print("Starting seed...")
                # Clear existing data
        Comment.query.delete()
        Post.query.delete()
        User.query.delete()
        Tag.query.delete()
        Genre.query.delete()

        # Create Users
        users = []
        for _ in range(10):  # Create 10 users
            username = fake.user_name()
            password = "password123"  # Default password for all users
            user = User(username=username, password=password)
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        # Create Tags
        tags = []
        for _ in range(5):  # Create 5 tags
            tag = Tag(name=fake.word())
            tags.append(tag)
        db.session.add_all(tags)
        db.session.commit()

        # Create Genres
        genres = []
        for _ in range(5):  # Create 5 genres
            genre = Genre(name=fake.word())
            genres.append(genre)
        db.session.add_all(genres)
        db.session.commit()

        # Create Posts
        posts = []
        for _ in range(20):  # Create 20 posts
            post = Post(
                title=fake.sentence(),
                text=fake.text(max_nb_chars=500),
                image=fake.image_url(),
                user_id=rc(users).id, )
            posts.append(post)
        db.session.add_all(posts)
        db.session.commit()

        genres_for_post = set()
        while len(genres_for_post) < randint(1, 2):  # Assign 1-2 random genres
            genres_for_post.add(rc(genres))
        post.genres = list(genres_for_post)

        posts.append(post)
        db.session.add_all(posts)
        db.session.commit()

        # Create Comments
        comments = []
        for _ in range(50):  # Create 50 comments
            comment = Comment(
                comment=fake.sentence(),
                user_id=rc(users).id,  # Assign to random user
                post_id=rc(posts).id,  # Assign to random post
            )
            comments.append(comment)
        db.session.add_all(comments)
        db.session.commit()
