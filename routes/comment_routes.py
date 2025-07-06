from flask import Blueprint, jsonify, current_app, request
from utils.token_required import token_required

comment_bp = Blueprint("comment", __name__)
supabase = None


@comment_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@comment_bp.route("/api/create_comment", methods = ['POST'])
@token_required
def create_comment(user_id):
    data = request.json
    recipe_id = data.get("recipe_id")
    content = data.get("content")

    if not recipe_id or not content:
        return jsonify({"error": "Recipe ID and content are required"}), 400

    try:
        supabase.table("comment").insert({"user_id": user_id, "recipe_id": recipe_id, "comment": content}).execute()
        return jsonify({"message": "Comment created successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @comment_bp.route("/api/get_comments", methods=["GET"])
# @token_required
# def get_comments(user_id):
#     recipe_id = request.args.get("recipe_id")

#     if not recipe_id:
#         return jsonify({"error": "Recipe ID is required"}), 400

#     try:
#         comments = supabase.table("comments").select("*").eq("recipe_id", recipe_id).execute()
#         return jsonify({"comments": comments.data}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
