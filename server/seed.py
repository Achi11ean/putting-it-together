#!/usr/bin/env python3

from random import randint, choice as rc

from faker import Faker

from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()

    fake = Faker()

    print("Creating users...")

    # make sure users have unique usernames
    users = []
    usernames = []

    for i in range(20):
        
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.append(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.url(),
        )

        user.password_hash = user.username + 'password'

        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = []
    for i in range(100):
        recipe = Recipe(
            title=fake.sentence(),
            instructions=fake.paragraph(nb_sentences=8),
            minutes_to_complete=randint(15, 90),
        )

        # Associate the recipe with a random user
        assigned_user = rc(users)
        assigned_user.recipes.append(recipe)  # Add the recipe to the user's recipe collection

        recipes.append(recipe)

    db.session.add_all(recipes)  # Ensure all recipes are added to the session
    db.session.commit()
    print("Complete.")