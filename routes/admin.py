from flask import Blueprint, jsonify, current_app, request, redirect, url_for
from utils.token_required import token_required, admin_required
from supabase import create_client, Client
import cloudinary
from dotenv import load_dotenv
import os

load_dotenv()

admin_bp = Blueprint("admin", __name__)
supabase = None

cloud_name = os.getenv("CLAUD_NAME")
api_key = os.getenv("CLAUD_API_KEY")
api_secret = os.getenv("CLAUD_API_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# print(cloud_name)
# print(api_key)
# print(api_secret)

cloudinary.config( 
    cloud_name = cloud_name, 
    api_key = api_key, 
    api_secret = api_secret, 
    secure=True
)

@admin_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@admin_bp.route("/api/get_all_users", methods=['GET'])
@token_required
@admin_required
def get_all_users(user_id):
    try:
        users = supabase.table("User").select("*").execute()
        return jsonify(users.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@admin_bp.route("/api/get_user/<string:user_id2>", methods=['GET'])
@token_required
@admin_required
def get_user(user_id, user_id2):
    try:
        user = supabase.table("User").select("*").eq("id", user_id2).execute()
        if user.data:
            return jsonify(user.data), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@admin_bp.route("/api/remove_user/<string:user_id2>", methods=['DELETE'])
@token_required
@admin_required
def remove_user(user_id, user_id2):
    try:
        supabase.table("User").delete().eq("id", user_id2).execute()

        admin_client:Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        admin_client.auth.admin.delete_user(user_id2)

        return jsonify({"message": "User removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@admin_bp.route("/api/get_contact_messages", methods=['GET'])
@token_required
@admin_required
def get_contact_messages(user_id):
    try:
        messages = supabase.table("contact_us").select("*").order("created_at", desc=True).execute()
        return jsonify(messages.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@admin_bp.route("/api/get_report_messages", methods=['GET'])
@token_required
@admin_required
def get_report_messages(user_id):
    try:
        messages = supabase.table("report").select("""
            *,
            reporter:user_id(
                id,
                name,
                username
            ),
            recipe:recipe_id(
                id,
                title
            )
        """).order("reported_at", desc=True).execute()
        return jsonify(messages.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@admin_bp.route("/api/remove_report/<string:report_id>", methods=['DELETE'])
@token_required
@admin_required
def remove_report(user_id, report_id):
    try:
        supabase.table("report").delete().eq("id", report_id).execute()
        return jsonify({"message": "Report removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@admin_bp.route("/api/remove_contact/<string:contact_id>", methods=['DELETE'])
@token_required
@admin_required
def remove_contact(user_id, contact_id):
    try:
        supabase.table("contact_us").delete().eq("id", contact_id).execute()
        return jsonify({"message": "Contact message removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@admin_bp.route("/api/search_user", methods=['POST'])
@token_required
@admin_required
def search_user(user_id):
    data = request.json
    search_query = data.get("query", "").strip()

    if not search_query:
        return redirect(url_for("admin.get_all_users"))

    try:
        users = supabase.table("User").select("*").ilike("username", f"%{search_query}%").execute()
        return jsonify(users.data), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 400