from flask import Blueprint, jsonify, current_app, request
from utils.token_required import token_required
import cloudinary
from dotenv import load_dotenv
import os

load_dotenv()

recipe_bp = Blueprint("recipe", __name__)
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

@recipe_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@recipe_bp.route("/api/create_recipe", methods = ['POST'])
@token_required
def create_recipe(user_id):
    title = request.form.get("title")
    ingredients = request.form.get("ingredients")
    description = request.form.get("description")
    instructions = request.form.get("instructions")
    is_ai_generated = request.form.get("is_ai_generated", "false").lower() == "true"

    if not title or not ingredients or not instructions:
        return jsonify({"error": "All fields are required"}), 400

    image = request.files.get("image")
    image_url = None

    if image:
        upload_result = cloudinary.uploader.upload(image, folder="recipe_images")
        image_url = upload_result.get("secure_url")

    try:
        recipe_data = {
            "created_by": user_id,
            "title": title,
            "ingredients": ingredients,
            "description": description,
            "instructions": instructions,
            "recipe_image_url": image_url,
            "is_ai_generated": is_ai_generated
        }
        supabase.table("recipe").insert(recipe_data).execute()
        return jsonify({"message": "Recipe created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_bp.route("/api/get_recipe/<string:recipe_id>", methods = ['GET'])
def get_recipe(recipe_id):
    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    try:
        recipe = supabase.table("recipe").select("""
            *,
            User:created_by (
                id,
                name,
                username,
                profile_picture_url
            ),
            comment (
                id,
                comment,
                created_at,
                user_id,
                User (
                    id,
                    name,
                    username,
                    profile_picture_url
                )
            )
        """).eq("id", recipe_id).execute()

        if not recipe.data:
            return jsonify({"error": "Recipe not found"}), 404
        
        print(recipe.data)

        return jsonify({"recipe": recipe.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@recipe_bp.route("/api/get_all_recipe", methods=['GET'])
def get_all_recipe():
    try:
        response = supabase.table("recipe").select("""
            *,
            User:created_by (
                id,
                name,
                username
            ),
            comment (
                id,
                comment,
                created_at,
                user_id,
                User (
                    id,
                    name,
                    username,
                    profile_picture_url
                )
            )
        """).execute()

        return jsonify({"recipes": response.data}), 200

    except Exception as e:
        print("Error in get_all_recipe:", e)
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


@recipe_bp.route("/api/get_save_recipe", methods=['GET'])
@token_required
def get_saved_recipes(user_id):
    try:
        # Step 1: Get list of saved recipe IDs by the user
        saved_entries = supabase.table("savedrecipe").select("recipe_id").eq("user_id", user_id).execute()
        recipe_ids = [entry["recipe_id"] for entry in saved_entries.data]
        print(recipe_ids)

        if not recipe_ids:
            return jsonify({"recipes": []}), 200

        # Step 2: Fetch full recipe data + User info + Comments + Comment User info
        all_recipes = []
        for recipe_id in recipe_ids:
            recipe = (
                supabase
                .table("recipe")
                .select("*, User(id, name, username), comment(*, User(id, name, username))")
                .eq("id", recipe_id)
                .limit(1)
                .execute()
            )
            if recipe.data:
                all_recipes.append(recipe.data[0])

        print(all_recipes)

        return jsonify({"recipes": all_recipes}), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch saved recipes",
            "details": str(e)
        }), 500


@recipe_bp.route("/api/update_recipe", methods = ['PUT'])
@token_required
def update_recipe(user_id):
    recipe_id = request.form.get("recipe_id")
    title = request.form.get("title")
    ingredients = request.form.get("ingredients")
    description = request.form.get("description")
    instructions = request.form.get("instructions")
    is_ai_generated = request.form.get("is_ai_generated", False)

    if not recipe_id:
        return jsonify({"error": "Recipe ID is required"}), 400

    recipe = supabase.table("recipe").select("*").eq("id", recipe_id).execute()
    if not recipe.data:
        return jsonify({"error": "Recipe not found"}), 404

    if recipe.data[0]["created_by"] != user_id:
        return jsonify({"error": "You are not authorized to update this recipe"}), 403

    image = request.files.get("image")
    image_url = None

    if image:
        upload_result = cloudinary.uploader.upload(image, folder="recipe_images")
        image_url = upload_result.get("secure_url")

    try:
        recipe_data = {
            "title": title,
            "ingredients": ingredients,
            "description": description,
            "instructions": instructions,
            "recipe_image_url": image_url,
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
