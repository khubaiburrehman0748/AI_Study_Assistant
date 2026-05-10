"""
AI Study Assistant - Main Flask Application
Serves both the API and the frontend HTML/static files.
"""



import os

from flask import Flask, send_from_directory

from flask_cors import CORS



                      

try:

    from dotenv import load_dotenv

    env_path = os.path.join(os.path.dirname(__file__), '.env')

    load_dotenv(env_path)

except ImportError:

    pass



import sys

sys.path.insert(0, os.path.dirname(__file__))



from routes.chat    import chat_bp

from routes.planner import planner_bp

from routes.tracker import tracker_bp



BASE_DIR     = os.path.dirname(__file__)

FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")

STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")





def create_app():

    app = Flask(

        __name__,

        template_folder=TEMPLATE_DIR,

        static_folder=STATIC_DIR

    )

    CORS(app)



    app.register_blueprint(chat_bp,    url_prefix="/api")

    app.register_blueprint(planner_bp, url_prefix="/api")

    app.register_blueprint(tracker_bp, url_prefix="/api")



    @app.route("/api/health")

    def health():

        return {"status": "ok", "message": "AI Study Assistant is running"}



    @app.route("/")

    def index():

        return send_from_directory(TEMPLATE_DIR, "index.html")



    @app.route("/static/<path:filename>")

    def static_files(filename):

        return send_from_directory(STATIC_DIR, filename)



    return app





if __name__ == "__main__":

    print("\n" + "="*55)

    print("  🎓  AI Study Assistant")

    print("  ──────────────────────────────────────────────")

    print("  URL:  http://localhost:5000")

    print("  API:  http://localhost:5000/api/health")

    print("="*55 + "\n")

    app = create_app()

    app.run(debug=True, port=5000, host="0.0.0.0")

