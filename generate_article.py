import os
import sys
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# --- SETUP & INITIALIZATION ---
# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")
client = OpenAI(api_key=api_key)

# Define the path to the Hugo content directory
HUGO_CONTENT_PATH = "content/posts"

# --- CORE FUNCTIONS ---
def generate_article_content(topic: str) -> str:
    """
    Generates the main body of a blog post on a given topic using the OpenAI API.
    """
    print(f"Generating article content for topic: {topic}...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content writer specializing in the AI and LLM technology niche. Your tone is authoritative, clear, and engaging. You write high-quality, well-structured blog posts. You only output the raw Markdown content of the article, without a title, as the title will be added separately."
                },
                {
                    "role": "user",
                    "content": f"Write a comprehensive blog post about '{topic}'. The post should be approximately 500 words and include an introduction, several body paragraphs, and a concluding summary. Do not include a title in the output."
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No content generated."
    except Exception as e:
        return f"An error occurred: {e}"

def create_hugo_post(title: str, filename: str, content: str):
    """
    Creates a new Hugo content file with the correct front matter.
    """
    # Ensure the content directory exists
    os.makedirs(HUGO_CONTENT_PATH, exist_ok=True)

    # Get the current date in the format Hugo expects
    current_date = datetime.now().isoformat()

    # Construct the front matter
    front_matter = f"""---
title: "{title}"
date: {current_date}
draft: true
---
"""

    # Combine front matter and content
    full_content = f"{front_matter}\n{content}"

    # Define the full file path
    file_path = os.path.join(HUGO_CONTENT_PATH, f"{filename}.md")

    # Write the content to the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Successfully created new post: {file_path}")
    except IOError as e:
        print(f"Error writing to file: {e}")

# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python generate_article.py \"<Article Title>\" \"<filename-without-extension>\"")
        sys.exit(1)

    article_title = sys.argv[1]
    output_filename = sys.argv[2]

    # 1. Generate the article's main body
    article_body = generate_article_content(article_title)

    # 2. Create the Hugo post file with front matter
    if "Error:" not in article_body:
        create_hugo_post(article_title, output_filename, article_body)
    else:
        print(f"Could not create post due to content generation error: {article_body}")
