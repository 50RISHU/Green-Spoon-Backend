from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS
from utils.token_required import token_required
from routes.auth_routes import auth_bp
from routes.recipe_routes import recipe_bp
from routes.comment_routes import comment_bp
from routes.user_routes import user_bp
import os

load_dotenv()
app = Flask(__name__)
# CORS(app, origins=["https://green-spoon.vercel.app"], supports_credentials=True)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app.supabase = supabase


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")  # service role key needed for decoding JWT

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/api/validate_token", methods=["GET"])
def validate_token():
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing or invalid authorization header"}), 401
    
    token = auth_header.replace("Bearer ", "").strip()

    if not token:
        return jsonify({"valid": False, "error": "Token is empty"}), 401

    try:
        # Validate token via Supabase REST API directly
        response = supabase.auth.get_user(token)
        user = response.user
        user_data = supabase.table("User").select("*").eq("id", user.id).execute()

        if user_data.data:
            user_info = user_data.data[0]
            print(user_data)
            return jsonify({
                "valid": True,
                "user": {
                    "id": user_info["id"],
                    "email": user_info["email"],
                    "name": user_info["name"],
                    "profile": user_info["profile_picture_url"],
                    "created_at": user_info["created_at"]
                }
            }), 200
        else:
            return jsonify({"valid": False, "error": "User not found"}), 401

    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return jsonify({"valid": False, "error": "Token validation failed"}), 401

@app.route("/api/contact", methods = ['POST'])
@token_required
def contact(user_id):
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    if not email or not message or not name or not phone:
        return jsonify({"error": "Email, message, name, and phone are required"}), 400

    contact_data = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "message": message
    }
    try:
        supabase.table("contact_us").insert(contact_data).execute()
        print(f"User {user_id} contacted support with message: {message}")
        return jsonify({"message": "Support request submitted successfully"}), 200
    except Exception as e:
        print(f"Error submitting support request: {str(e)}")
        return jsonify({"error": "Failed to submit support request"}), 500


app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)