from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from .views import main_views, artist_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(artist_views.bp)

    return app