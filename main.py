import os
from flask import Flask
from src.blueprints.movies import movies_blueprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.register_blueprint(movies_blueprint)
    return app

app = create_app()

def main():
    app.run(port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    main()
