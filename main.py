from flask import Flask
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.recipe_routes import recipe_bp
from routes.comment_routes import comment_bp
from routes.user_routes import user_bp
import os

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app.supabase = supabase


app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)