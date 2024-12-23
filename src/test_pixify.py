# Standard library imports
import os
import tkinter as tk
from io import BytesIO
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest
import requests
from PIL import Image
from PIL.ImageFile import ImageFile

# Local application imports
import pixify


def test_pytest_env_variable():
    pytest_current_test = os.getenv("PYTEST_CURRENT_TEST")
    print(f"PYTEST_CURRENT_TEST: {pytest_current_test}")
    assert pytest_current_test is not None, "PYTEST_CURRENT_TEST is not set!"

def test_load_image():
    # Create a mock image file
    image_path = "test_image.png"
    image = Image.new("RGB", (100, 100))
    image.save(image_path)

    # Test the load_image function
    loaded_image = pixify.load_image(image_path)
    assert isinstance(loaded_image, Image.Image)

def test_resize_image():
    # Create a mock image
    image = Image.new("RGB", (100, 100))
    new_size = (50, 50)

    # Test the resize_image function
    resized_image = pixify.resize_image(image, new_size)
    assert resized_image.size == (100, 100)

def test_reduce_colors():
    # Create a mock image
    image = Image.new("RGB", (100, 100))

    # Test the reduce_colors function
    reduced_image = pixify.reduce_colors(image, 16)
    assert reduced_image.getcolors() is not None

def test_get_input(monkeypatch: pytest.MonkeyPatch):
    # Mock the tkinter input
    def mock_get_input():
        return 32, 256, "test prompt", "/test/path/"

    monkeypatch.setattr(pixify, "get_input", mock_get_input)
    pixel_size, num_colors, prompt, path = pixify.get_input()
    assert pixel_size == 32
    assert num_colors == 256
    assert prompt == "test prompt"
    assert path == "/test/path/"

@patch("pixify.requests.get")
def test_create_image_file_object(mock_get):
    # Mock the requests.get response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'image/png'}
    with open(r"./test_image.png", "rb") as image_file:
        image_bytes = image_file.read()
    mock_response.content = image_bytes
    mock_get.return_value = mock_response

    # Test the create_image_file_object function
    image_url = (
        "https://www.adverthia.com/wp-content/uploads/2020/02/"
        "instagram-logo-png-transparent-background-1024x1024-1.png"
    )
    image = pixify.create_image_file_object(image_url)

    assert isinstance(image, Image.Image)

def test_generate_random_filename():
    # Test the generate_random_filename function
    filename = pixify.generate_random_filename()
    assert filename.startswith("IMAGE-")
    assert filename.endswith(".png")

@patch("pixify.pixellate")
def test_pixellate(mock_pixellate):
    # Mock the pixellate function
    mock_pixellate.return_value = None

    # Test the pixellate function
    pixify.pixellate()
    mock_pixellate.assert_called_once()
