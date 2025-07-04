from flask import Blueprint, jsonify, current_app, request


auth_bp = Blueprint("auth", __name__)
supabase = None

@auth_bp.before_app_request
def setup_supabase():
    global supabase
    if not supabase:
        supabase = current_app.supabase


@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    existing_user = supabase.table("User").select("*").eq("email", email).execute()
    if existing_user.data:
        return jsonify({"error": "Email already in use"}), 400
    

    existing_user = supabase.table("User").select("*").eq("username", username).execute()
    if existing_user.data:
        return jsonify({"error": "Username already in use"}), 400

    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        supabase.table("User").insert({"id": res.user.id, "name": name, "username": username, "email": email}).execute()
        return jsonify({
            "message": "Signup successful.",
            "user_id": res.user.id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@auth_bp.route("/api/login", methods=["POST"])
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

