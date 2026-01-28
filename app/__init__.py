from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from app import models

    # INIT EXTENSIONS
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


    # Register BLUEPRINTS (must be imported inside function)
    from app.routes import main_bp  # ← NOWY blueprint na login/dashboard
    from app.modules.descriptions import descriptions_bp
    from app.modules.icons import icons_bp
    from app.modules.settings import settings_bp
    from app.modules.variants import variants_bp
    from app.modules.descriptions_export import descriptions_export_bp
    from app.modules.photos import photos_bp
    from app.modules.seo import seo_bp
    from app.modules.integrations import integrations_bp



    app.register_blueprint(main_bp)
    app.register_blueprint(descriptions_bp, url_prefix="/descriptions")
    app.register_blueprint(icons_bp, url_prefix="/icons")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(variants_bp, url_prefix="/variants")
    app.register_blueprint(descriptions_export_bp, url_prefix="/descriptions-export")
    app.register_blueprint(photos_bp, url_prefix="/photos")
    app.register_blueprint(seo_bp, url_prefix="/seo")
    app.register_blueprint(integrations_bp, url_prefix="/integrations")

    return app
