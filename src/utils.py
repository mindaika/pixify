"""
Utility functions for image generation and pixellation using OpenAI API.
"""
import os
import uuid
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from openai import OpenAI
from .secrets import get_openai_api_key

class ImageProcessor:
    """Handles image generation and pixellation using OpenAI API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the ImageProcessor with OpenAI API key.

        Args:
            api_key: OpenAI API key (defaults to Docker secret or OPENAI_API_KEY env var)
        """
        if api_key:
            self.api_key = api_key
        else:
            # Read from Docker secret file or fall back to environment variable
            self.api_key = get_openai_api_key()

        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt: str, size: str = "1024x1024") -> str:
        """
        Generate an image using OpenAI's DALL-E API.

        Args:
            prompt: Text description of the image to generate
            size: Image size (256x256, 512x512, or 1024x1024)

        Returns:
            str: URL of the generated image

        Raises:
            Exception: If image generation fails
        """
        try:
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size=size
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")

    def fetch_image(self, image_url: str) -> Image.Image:
        """
        Fetch an image from a URL and return a PIL Image object.

        Args:
            image_url: URL of the image to fetch

        Returns:
            PIL.Image.Image: The fetched image

        Raises:
            Exception: If image fetch or processing fails
        """
        try:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            image_stream = BytesIO(response.content)
            image = Image.open(image_stream)
            return image.convert("RGB")
        except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
            raise Exception(f"Failed to fetch image: {str(e)}")

    def pixelate_image(self, image: Image.Image, pixel_size: int) -> Image.Image:
        """
        Create a pixelated effect by downscaling and upscaling.

        Args:
            image: PIL Image to pixelate
            pixel_size: Size of each pixel block

        Returns:
            PIL.Image.Image: Pixelated image
        """
        # Calculate new size for downscaling
        new_width = max(1, image.width // pixel_size)
        new_height = max(1, image.height // pixel_size)
        new_size = (new_width, new_height)

        # Downscale then upscale to create pixel effect
        smaller_image = image.resize(new_size, Image.Resampling.NEAREST)
        return smaller_image.resize(image.size, Image.Resampling.NEAREST)

    def reduce_colors(self, image: Image.Image, num_colors: int) -> Image.Image:
        """
        Reduce the number of colors in an image.

        Args:
            image: PIL Image to process
            num_colors: Number of colors to reduce to

        Returns:
            PIL.Image.Image: Image with reduced color palette
        """
        image = image.convert("RGB")
        return image.quantize(num_colors).convert("RGB")

    def process_image(self, prompt: str, pixel_size: int = 32,
                     num_colors: int = 256, size: str = "1024x1024") -> bytes:
        """
        Generate, pixelate, and reduce colors of an image based on prompt.

        Args:
            prompt: Text description for image generation
            pixel_size: Size of pixel blocks (default: 32)
            num_colors: Number of colors in final image (default: 256)
            size: Generated image size (default: 1024x1024)

        Returns:
            bytes: PNG image data

        Raises:
            Exception: If any step fails
        """
        # Generate image
        image_url = self.generate_image(prompt, size)

        # Fetch image
        image = self.fetch_image(image_url)

        # Pixelate
        pixelated = self.pixelate_image(image, pixel_size)

        # Reduce colors
        final_image = self.reduce_colors(pixelated, num_colors)

        # Convert to bytes
        img_io = BytesIO()
        final_image.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io.getvalue()

def get_image_processor() -> ImageProcessor:
    """
    Factory function to create an ImageProcessor instance.

    Returns:
        ImageProcessor: Configured image processor
    """
    return ImageProcessor()
