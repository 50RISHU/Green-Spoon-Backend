from flask import Blueprint, jsonify, current_app, request
from utils.token_required import token_required

recipe_bp = Blueprint("recipe", __name__)
supabase = None


@recipe_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@recipe_bp.route("/api/create_recipe", methods = ['POST'])
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


@recipe_bp.route("/api/get_recipe", methods = ['GET', 'POST'])
def get_recipe():
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


@recipe_bp.route("/api/get_all_recipe", methods = ['GET'])
def get_all_recipe():
    try:
        recipes = supabase.table("recipe").select("*").execute()
        return jsonify({"recipes": recipes.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_bp.route("/api/get_my_recipe", methods = ['GET'])
@token_required
def get_my_recipe(user_id):
    try:
        recipes = supabase.table("recipe").select("*").eq("created_by", user_id).execute()
        if not recipes.data:
            return jsonify({"message": "No recipes Yet."}), 200
        return jsonify({"recipes" : recipes.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_bp.route("/api/save_recipe", methods=["POST"])
@token_required
def save_recipe(user_id):
    data = request.json
    recipe_id = data.get("recipe_id")

    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    try:
        supabase.table("savedrecipe").insert({"user_id": user_id, "recipe_id": recipe_id}).execute()
        return jsonify({"message": "Recipe saved successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_bp.route("/api/update_recipe", methods = ['POST'])
@token_required
def update_recipe(user_id):
    data = request.json
    recipe_id = data.get("recipe_id")
    title = data.get("title")
    ingredients = data.get("ingredients")
    description = data.get("description")
    instructions = data.get("instructions")
    is_ai_generated = data.get("is_ai_generated", False)

    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    recipe = supabase.table("recipe").select("*").eq("id", recipe_id).execute()
    if not recipe.data:
        return jsonify({"error": "Recipe not found"}), 404

    if recipe.data[0]["created_by"] != user_id:
        return jsonify({"error": "You are not authorized to update this recipe"}), 403

    try:
        recipe_data = {
            "title": title,
            "ingredients": ingredients,
            "description": description,
            "instructions": instructions,
            "is_ai_generated": is_ai_generated
        }
        supabase.table("recipe").update(recipe_data).eq("id", recipe_id).execute()
        return jsonify({"message": "Recipe updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_bp.route("/api/delete_recipe", methods=["POST"])
@token_required
def delete_recipe(user_id):
    data = request.json
    recipe_id = data.get("recipe_id")

    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    recipe = supabase.table("recipe").select("*").eq("id", recipe_id).execute()
    if not recipe.data:
        return jsonify({"error": "Recipe not found"}), 404

    if recipe.data[0]["created_by"] != user_id:
        return jsonify({"error": "You are not authorized to delete this recipe"}), 403

    try:
        supabase.table("recipe").delete().eq("id", recipe_id).execute()
        return jsonify({"message": "Recipe deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
