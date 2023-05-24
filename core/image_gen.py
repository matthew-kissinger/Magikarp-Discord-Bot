import os
import requests
import openai

def generate_image(image_prompt):
    image_data = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_data

def save_image(url, file_path):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a successful response

    with open(file_path, 'wb') as f:
        f.write(response.content)

def generate_filename(directory):
    i = 1
    while os.path.exists(f"{directory}/image{i}.png"):
        i += 1
    return f"{directory}/image{i}.png"