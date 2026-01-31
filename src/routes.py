import os
from typing import Tuple, Union
from flask import jsonify, request, Response, send_file
from .auth import AuthError, requires_auth
from .utils import get_image_processor
from io import BytesIO
import base64

JsonResponse = Union[Response, Tuple[Response, int]]

def init_routes(app):
    @app.route('/api/status')
    def api_status() -> JsonResponse:
        """Health check endpoint."""
        return jsonify({"status": "okeydokey-pixify"})

    @app.route('/api/generate_pixelated_image', methods=['POST', 'OPTIONS'])
    @requires_auth
    def generate_pixelated_image(current_user: str) -> JsonResponse:
        """
        Generate a pixelated image based on prompt and specifications.

        Args:
            current_user: User ID from JWT token

        Returns:
            JSON response with image data or error
        """
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response

        try:
            # Get form data
            data = request.get_json()

            prompt = data.get('prompt', '').strip()
            pixel_size = int(data.get('pixel_size', 32))
            num_colors = int(data.get('num_colors', 256))
            size = data.get('size', '1024x1024')

            # Validation
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': 'Image prompt is required'
                }), 400

            if pixel_size < 1 or pixel_size > 100:
                return jsonify({
                    'success': False,
                    'error': 'Pixel size must be between 1 and 100'
                }), 400

            if num_colors < 2 or num_colors > 256:
                return jsonify({
                    'success': False,
                    'error': 'Number of colors must be between 2 and 256'
                }), 400

            if size not in ['256x256', '512x512', '1024x1024']:
                return jsonify({
                    'success': False,
                    'error': 'Size must be 256x256, 512x512, or 1024x1024'
                }), 400

            # Process image
            try:
                processor = get_image_processor()
                image_data = processor.process_image(
                    prompt=prompt,
                    pixel_size=pixel_size,
                    num_colors=num_colors,
                    size=size
                )
                
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                return jsonify({
                    'success': True,
                    'image_data': f'data:image/png;base64,{image_base64}'
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error generating image: {str(e)}'
                }), 500

        except AuthError as e:

            return jsonify({
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Error handlers
    @app.errorhandler(AuthError)
    def handle_auth_error(ex: AuthError) -> JsonResponse:
        """Handle authentication errors."""
        response = jsonify({
            "success": False,
            "error": ex.error
        })
        return response, ex.status_code
