#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.json

        if 'username' not in data or 'password' not in data:
            return {"error": "Username and password are required."}, 422

        try:
            # Create a new user
            new_user = User(
                username=data['username'],
                password=data['password'],  # This invokes the password setter
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
            )
            db.session.add(new_user)
            db.session.commit()

            # Store the user's ID in the session
            session['user_id'] = new_user.id  # Ensure session is set up correctly

            return {
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists."}, 422

class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data['username']).first()

        if user and user.authenticate(data['password']):
            session['user_id'] = user.id  # Store the user's ID in the session
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        else:
            return {"error": "Invalid username or password"}, 401
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Not logged in"}, 401

        user = db.session.get(User, user_id)
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        else:
            return {"error": "User not found"}, 404    



class Logout(Resource):
    def delete(self):
        # Check if user_id is present in session
        if 'user_id' not in session or session.get('user_id') is None:
            return {"error": "Not logged in"}, 401

        # Remove user_id from session if it exists
        session.pop('user_id')
        return {}, 204

class RecipeIndex(Resource):
    # GET /recipes (Recipe List Feature)
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Not logged in"}, 401

        # Fetch all recipes for the logged-in user
        recipes = Recipe.query.filter_by(user_id=user_id).all()

        return [
            {
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            }
            for recipe in recipes
        ], 200

    # POST /recipes (Recipe Creation Feature)
    def post(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Not logged in"}, 401

        data = request.json

        # Validate required fields
        if not all(key in data for key in ['title', 'instructions', 'minutes_to_complete']):
            return {"error": "Missing required fields: title, instructions, and minutes_to_complete."}, 422

        if len(data['instructions']) < 50:
            return {"error": "Instructions must be at least 50 characters long."}, 422

        try:
            # Create a new recipe and associate it with the logged-in user
            new_recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user_id  # This associates the recipe with the logged-in user
            )

            db.session.add(new_recipe)
            db.session.commit()

            # Fetch the user object associated with the new recipe
            user = new_recipe.user

            # Return a response with the new recipe details and the nested user object
            return {
                'title': new_recipe.title,
                'instructions': new_recipe.instructions,
                'minutes_to_complete': new_recipe.minutes_to_complete,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
            }, 201  # HTTP status code for 'Created'

        except IntegrityError:
            db.session.rollback()
            return {"error": "There was an issue with the data provided."}, 422
        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)