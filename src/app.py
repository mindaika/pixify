import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

@app.route('/api/status')
def api_status():
    """Health check endpoint"""
    return jsonify({"status": "ok"})
