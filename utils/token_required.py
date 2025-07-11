from functools import wraps
from flask import request, jsonify, current_app

supabase = None



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global supabase
        if not supabase:
            supabase = current_app.supabase

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



def admin_required(f):
    @wraps(f)
    def decorated(user_id,*args, **kwargs):
        global supabase
        if not supabase:
            supabase = current_app.supabase

        try:
            res = supabase.table("User").select("is_admin").eq("id", user_id).execute()
            print(res.data)
            if res.data and res.data[0]["is_admin"]:
                return f(user_id, *args, **kwargs)
            else:
                return jsonify({"error": "Admin access required"}), 401

        except Exception as e:
            print("Auth Error:", e)
            return jsonify({"error": "Invalid token", "details": str(e)}), 401
        
    return decorated
