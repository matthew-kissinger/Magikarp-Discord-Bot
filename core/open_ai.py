import openai
from config import OPENAI_KEY

# Initialize OpenAI API key
openai.api_key = OPENAI_KEY


def generate_image(image_prompt):
    image_data = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_data