from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client
from functools import wraps
import os

# Load .env
load_dotenv()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or Authorization header must be in 'Bearer <token>' format"}), 401
        
        token = auth_header.split(" ")[1]
        try:
            res = supabase.auth.get_user(token)
            user_id = res.user.id

        except Exception as e:
            print("Auth Error:", e)
            return jsonify({"error": "Invalid token", "details": str(e)}), 401

        return f(user_id, *args, **kwargs)
    return decorated

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)


# ✅ Signup Route
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    existing_user = supabase.table("User").select("*").eq("email", email).execute()
    if existing_user.data:
        return jsonify({"error": "Email already in use"}), 400

    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        supabase.table("User").insert({"id": res.user.id, "name": name, "username": username, "email": email}).execute()
        return jsonify({
            "message": "Signup successful. Check your email to confirm.",
            "user_id": res.user.id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ✅ Login Route
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        token = res.session.access_token
        user_id = res.user.id
        return jsonify({
            "message": "Login successful.",
            "access_token": token,
            "user_id": user_id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/logout")
@token_required
def logout(user_id):
    try:
        supabase.auth.sign_out()
        return jsonify({"message": "Logout successful."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/create_recipe", methods = ['POST'])
@token_required
def create_recipe(user_id):
    data = request.json
    title = data.get("title")
    ingredients = data.get("ingredients")
    description = data.get("description")
    instructions = data.get("instructions")
    is_ai_generated = data.get("is_ai_generated", False)

    if not title or not ingredients or not instructions:
        return jsonify({"error": "All fields are required"}), 400

    try:
        recipe_data = {
            "created_by": user_id,
            "title": title,
            "ingredients": ingredients,
            "description": description,
            "instructions": instructions,
            "is_ai_generated": is_ai_generated
        }
        supabase.table("recipe").insert(recipe_data).execute()
        return jsonify({"message": "Recipe created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_recipe", methods = ['GET', 'POST'])
@token_required
def get_recipe(user_id):
    data = request.json
    recipe_id = data.get("recipe_id")

    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    try:
        recipe = supabase.table("recipe").select("*").eq("id", recipe_id).execute()
        if not recipe.data:
            return jsonify({"error": "Recipe not found"}), 404

        return jsonify({"recipe": recipe.data[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_all_recipe", methods = ['GET'])
def get_all_recipe():
    try:
        recipes = supabase.table("recipe").select("*").execute()
        return jsonify({"recipes": recipes.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)