from flask import Blueprint, jsonify, current_app, request
from utils.token_required import token_required
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()

user_bp = Blueprint("user", __name__)
supabase = None

cloudinary.config( 
    cloud_name = os.getenv("CLOUD_NAME"), 
    api_key = os.getenv("CLOUD_API_KEY"), 
    api_secret = os.getenv("CLOUD_API_SECRET"), 
    secure=True
)

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
    user = supabase.table("User").select("*").eq("id", user_id).execute()
    if not user.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.data[0]}), 200


@user_bp.route("/api/upload_profile_pic", methods = ['POST'])
@token_required
def upload_profile_pic(user_id):
    profile_pic = request.files.get("profile_pic")
    if not profile_pic:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(profile_pic)
        image_url = upload_result.get("secure_url")

        # Update user profile in Supabase
        supabase.table("User").update({"profile_picture_url": image_url}).eq("id", user_id).execute()
        return jsonify({"message": "Profile picture uploaded successfully.", "url": image_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

   
@user_bp.route("/api/change_password", methods=["POST"])
@token_required
def change_password(user_id):
    data = request.json
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    try:
        # Use service role key for admin operations
        # This bypasses RLS and allows admin operations
        admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Update user password using admin client
        res = admin_client.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )

        if res.user:
            return jsonify({
                "message": "Password changed successfully",
                "user_id": res.user.id
            }), 200
        else:
            return jsonify({"error": "Password update failed"}), 400
            
    except Exception as e:
        return jsonify({"error": "Failed to change password", "details": str(e)}), 400


@user_bp.route("/api/forgot_password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        supabase.auth.reset_password_email(email)
        return jsonify({"message": "Password reset email sent"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to send reset email", "details": str(e)}), 400
