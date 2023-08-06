from flask import Flask

__version__ = '1.0.0'

def create_app():
    from .routes import server_bp

    app = Flask(__name__)
    app.register_blueprint(server_bp)
    
    return app


