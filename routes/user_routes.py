from flask import Blueprint, jsonify, current_app, request
from utils.token_required import token_required
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader

load_dotenv()

user_bp = Blueprint("user", __name__)
supabase = None

cloud_name = os.getenv("CLAUD_NAME")
api_key = os.getenv("CLAUD_API_KEY")
api_secret = os.getenv("CLAUD_API_SECRET")

# print(cloud_name)
# print(api_key)
# print(api_secret)

cloudinary.config( 
    cloud_name = cloud_name, 
    api_key = api_key, 
    api_secret = api_secret, 
    secure=True
)

# print(cloudinary.config().cloud_name)  # should print your cloud_name
# print(cloudinary.config().api_key)     # should print your API key
# print(cloudinary.config().api_secret)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


@user_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@user_bp.route("/api/profile", methods = ['GET'])
@token_required
def profile(user_id):
    try:
        user = supabase.table("User").select("*").eq("id", user_id).execute()
        if not user.data:
            return jsonify({"error": "User not found"}), 404

        created_recipe = supabase.table("recipe").select("id").eq("created_by", user_id).execute() or 0
        total_recipe = len(created_recipe.data) or 0

        saved_recipe = supabase.table("savedrecipe").select("id").eq("user_id", user_id).execute() or 0
        total_saved = len(saved_recipe.data) or 0

        return jsonify({"user": user.data[0], "total_recipes": total_recipe, "total_saved": total_saved}), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve user profile", "details": str(e)}), 500


@user_bp.route("/api/update_profile", methods=["PUT"])
@token_required
def update_profile(user_id):
    # Fetch form fields
    name = request.form.get("name")
    new_password = request.form.get("new_password")
    username = request.form.get("username")
    profile_pic = request.files.get("profile_pic")
    image_url = None

    if not name:
        return jsonify({"error": "Name is required"}), 400


    try:
        # 1. Upload profile picture if provided
        if profile_pic:
            upload_result = cloudinary.uploader.upload(profile_pic, folder="profile_pics")
            image_url = upload_result.get("secure_url")
            supabase.table("User").update({"profile_picture_url": image_url}).eq("id", user_id).execute()

        # 2. Update user in Supabase
        supabase.table("User").update({"name": name, "username": username}).eq("id", user_id).execute()

        # 3. If new password provided, update it using Admin API
        if new_password:
            admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            res = admin_client.auth.admin.update_user_by_id(user_id, {"password": new_password})
            if not res.user:
                return jsonify({"error": "Password update failed"}), 400

        return jsonify({
            "message": "Profile updated successfully.",
            "name": name,
            "image_url": image_url,
            "password_updated": bool(new_password)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/forgot_password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        res = supabase.auth.reset_password_email(email,{
        "redirect_to": "http://localhost:5173/reset-password",
    })

        # if res.get('error'):
        #     return jsonify({"error": res['error']['message']}), 400

        return jsonify({"message": "Password reset email sent"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to send reset email", "details": str(e)}), 400


@user_bp.route("/api/reset_password", methods = ['POST'])
@token_required
def reset_password(user_id):
    data = request.json
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    try:
        admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        res = admin_client.auth.admin.update_user_by_id(user_id, {"password": new_password})

        if res.user:
            return jsonify({"message": "Password reset successful!"}), 200
        else:
            return jsonify({"error": "Password reset failed."}), 400
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500