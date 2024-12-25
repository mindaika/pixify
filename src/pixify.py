"""
This script provides functionality to generate and manipulate images using 
the OpenAI API and the PIL library. 

It includes functions to load, resize, and reduce colors in images, as well as a GUI to 
collect user input for 
image generation and manipulation parameters.
Functions:
    load_image(image_path):
    resize_image(image, new_size):
        Resizes the image to a new size and then resizes it back to the original size 
        using nearest neighbor.
    reduce_colors(image, num_colors):
    get_input():
        Creates a window to collect user input for pixel size, number of colors, and 
        a drawing prompt.
    generate_image(prompt: str):
    pixellate(output_path):
    create_image_file_object(image_url):
    generate_random_filename():
        Generates a random filename for the output image.
"""
# Standard library imports
import os
import tkinter as tk
import uuid
from io import BytesIO
from tkinter import ttk

# Third-party imports
import openai
import requests
from openai import OpenAI
from PIL import Image, UnidentifiedImageError
from PIL.ImageFile import ImageFile


# Load an image from a file
def load_image(image_path):
    """
    Takes the URL for an image and returns an ImageFile object.
    
    Parameters:
        image_path (str): The path to the image file.
    
    Returns:
        An ImageFile object.
    """
    return Image.open(image_path)

def resize_image(image, new_size):
    """
    Resizes the img to a new size and then resizes it back to the orig size using nearest neighbor
    
    Parameters:
        image (PIL.Image.Image): The image to be resized.
        new_size (tuple): The new size as a tuple (width, height).
    
    Returns:
        PIL.Image.Image: The resized image.
    """
    smaller_image = image.resize(new_size, Image.Resampling.NEAREST)
    return smaller_image.resize(image.size, Image.Resampling.NEAREST)

def reduce_colors(image, num_colors):
    """
    Reduces the number of colors in an image.

    Parameters:
    image (PIL.Image.Image): The input image to be processed.
    num_colors (int): The number of colors to reduce the image to.

    Returns:
    PIL.Image.Image: The image with reduced colors.
    """
    # Convert to RGB if necessary
    image = image.convert("RGB")
    return image.quantize(num_colors)

def get_input():
    """
    Creates a window to collect user input for pixel size, number of colors, 
    and a drawing prompt.

    The GUI contains:
    - An entry for pixel size with a default value of 32.
    - An entry for the number of colors with a default value of 256.
    - An entry for a drawing prompt with a default value of a descriptive text.

    The function waits for the user to press the "Pixellate" button, 
    then retrieves the values from the entries,
    closes the GUI window, and returns the collected values.

    Returns:
        tuple: A tuple containing:
            - pixel_size (int): The size of the pixels.
            - num_colors (int): The number of colors.
            - prompt (str): The drawing prompt.
    """
    root = tk.Tk()
    root.title("Pixify")

    fields = {}

    fields['pixel_size_label'] = ttk.Label(text='Enter the pixel size:')
    fields['pixel_size'] = ttk.Entry()
    fields['pixel_size'].insert(0, "32")

    fields['num_colors_label'] = ttk.Label(text='Enter the number of colors:')
    fields['num_colors'] = ttk.Entry(show="*")
    fields['num_colors'].insert(0, "256")

    fields['path_label'] = ttk.Label(text='Where do you wanna stick it?')
    fields['path'] = ttk.Entry()
    fields['path'].insert(0, '/Users/mindaika/Downloads/')

    fields['prompt_label'] = ttk.Label(text='Tell me what you want to draw and pixellate')
    fields['prompt'] = ttk.Entry()
    fields['prompt'].insert(0, "Imagine a tiny hamster with a superhero cape, balancing on top of \
        a giant banana peel, while juggling three flaming donuts under a disco ball.")


    for field in fields.values():
        field.pack(anchor=tk.W, padx=10, pady=5, fill=tk.X)

     # Create a button
    button = tk.Button(root, text="Pixellate", command=root.quit)
    button.pack()

    # Run the main loop
    # Typically, in a Tkinter program, you place the call to the mainloop()
    # method as the last statement after creating the widgets, or so it says
    root.mainloop()

    # Get the values from the entries
    pixel_size = int(fields['pixel_size'].get())
    num_colors = int(fields['num_colors'].get())
    prompt = str(fields['prompt'].get())
    path = str(fields['path'].get())

    # Destroy the window
    root.destroy()

    return pixel_size, num_colors, prompt, path

def generate_image(prompt: str):
    """
    Generates an image based on the given prompt using the OpenAI API.
    Args:
        prompt (str): The text prompt to generate the image from.
    Returns:
        str: The URL of the generated image if successful, None otherwise.
    Raises:
        Exception: If there is an error during the image generation process.
    """
    load_dotenv()
    OpenAI.api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI()

    try:
        response = client.images.generate(
            prompt=prompt,
            n=2,
            size="1024x1024"
        )

        # Get the image URL
        image_url = response.data[0].url

        return image_url

    except openai.APIError as e:
        print(e.message)

        return None

def pixellate():
    """
    Pixellates an image, reduces the number of colors, and saves the result.

    This function performs the following steps:
    1. Retrieves the pixel size, number of colors, and prompt text from the user.
    2. Uses the Prompt API to generate an image based on the prompt text.
    3. Converts the generated image URL to an ImageFile object.
    4. Calculates the new size for the image based on the pixel size.
    5. Resizes the image to create a pixelated effect.
    6. Reduces the number of colors in the pixelated image.
    7. Saves the final image to the specified output path.

    Args:
        output_path (str): The file path where the final image will be saved.

    Returns:
        None
    """

    # Get the pixel size, number of colors, and prompt text
    try:
        pixel_size, num_colors, prompt, path = get_input()

    # Gracefully handles closing the dialog
    except tk.TclError as e:
        print("Dialog closed; no " + str(e))
        return

    # Use the Prompt API to generate an image and convert it to an ImageFile object
    image_url = generate_image(prompt)
    image = create_image_file_object(image_url)

    # Calculate the new size
    new_size = (image.width // pixel_size, image.height // pixel_size)

    # Pixellate the image
    pixelated_image = resize_image(image, new_size)

    # Reduce the number of colors
    low_color_image = reduce_colors(pixelated_image, num_colors)

    # Get the output path
    output = path + generate_random_filename()

    # Save the image
    low_color_image.save(output)
    print(f"Saved {output}")

def create_image_file_object(image_url):
    """
    Fetches an image from the given URL and creates an Image object.
    Args:
        image_url (str): The URL of the image to fetch.
    Returns:
        Image: An Image object created from the fetched image.
        None: If an error occurs during the process.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        PIL.UnidentifiedImageError: If the image cannot be identified or opened.
    """
    try:
        # Fetch the image from the URL
        response = requests.get(image_url, timeout=60)

        # Raise an error for bad responses
        response.raise_for_status()

        # Load the image into a BytesIO stream
        image_stream = BytesIO(response.content)

        # Create an Image object using PIL
        image = Image.open(image_stream)

        # Optionally, convert the Image to an ImageFile object
        if isinstance(image, ImageFile):
            return image  # It's already an ImageFile

        # Convert explicitly if necessary
        return image.convert("RGB")  # or appropriate mode

    except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
        print(f"Error creating image file object: {e}")
        return None

def generate_random_filename():
    """
    Generate a random filename for an image.

    This function generates a random unique string of 8 characters using UUID,
    and returns a filename in the format "IMAGE-<random_part>.png".

    Returns:
        str: A randomly generated filename in the format "IMAGE-<random_part>.png".
    """
    random_part = uuid.uuid4().hex[:8]  # Generate a random unique string (8 characters)
    return f"IMAGE-{random_part}.png"

def main():
    """
    Main function to execute the pixellate process.
    """
    pixellate()

if __name__ == "__main__":
    main()