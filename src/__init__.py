from flask import Flask, jsonify
from flask_cors import CORS
from .routes import init_routes

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        UPLOAD_FOLDER='/tmp',
    )

    @app.route('/')
    def hello():
        return {"message": "Pixify API running"}

    # Initialize routes
    init_routes(app)

    return app