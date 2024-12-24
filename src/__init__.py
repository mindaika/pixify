from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        UPLOAD_FOLDER='/tmp',
    )
    
    @app.route('/')
    def hello():
        return {"message": "Pixify API running"}
    
    @app.route('/api/status')
    def api_status():
        """Health check endpoint"""
        return jsonify({"status": "okeydokey-pixify"})
        
    return app