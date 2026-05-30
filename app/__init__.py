from flask import Flask
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth
from .config import Config

socketio = SocketIO(cors_allowed_origins="*") 
oauth = OAuth()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    socketio.init_app(app)

    with app.app_context():
        # Inicializamos base de datos
        from .database import init_db
        init_db()

    # Registramos las Rutas Web (Blueprint)
    from .routes import main
    app.register_blueprint(main)
    
    # Importamos los sockets para que escuchen los eventos
    from . import sockets

    return app