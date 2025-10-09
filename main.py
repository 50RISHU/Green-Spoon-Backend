from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS
from utils.token_required import token_required
from routes.admin import admin_bp
from routes.auth_routes import auth_bp
from routes.recipe_routes import recipe_bp
from routes.comment_routes import comment_bp
from routes.user_routes import user_bp
import os

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://green-spoon.vercel.app","http://localhost:5173"], supports_credentials=True)
# CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app.supabase = supabase


# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")  # service role key needed for decoding JWT

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/api/validate_token", methods=["GET", "OPTIONS"])
def validate_token():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight"}), 200

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing or invalid authorization header"}), 401

    token = auth_header.split("Bearer ")[1].strip()

    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if not user:
            raise ValueError("Invalid or expired token")

        user_data = supabase.table("User").select("*").eq("id", user.id).execute()
        if not user_data.data:
            return jsonify({"valid": False, "error": "User not found"}), 401

        user_info = user_data.data[0]
        return jsonify({
            "valid": True,
            "user": {
                "id": user_info["id"],
                "email": user_info["email"],
                "name": user_info["name"],
                "profile": user_info.get("profile_picture_url"),
                "is_admin": user_info.get("is_admin", False)
            }
        }), 200

    except Exception as e:
        print(f"Token validation error: {e}")
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

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)