import os
from flask import Flask, session, g, render_template
from config import Config
from database import init_db, query_db
from seed_2025_archive import seed_database
from utils.translations import get_translation

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure database exists
    if not os.path.exists(Config.DATABASE_PATH):
        print("Database not found. Seeding initial database...")
        seed_database()

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.vargani import vargani_bp
    from routes.mahaprasad import mahaprasad_bp
    from routes.expenses import expenses_bp
    from routes.dj_procession import dj_bp
    from routes.daily_accounts import daily_bp
    from routes.transactions import transactions_bp
    from routes.members import members_bp
    from routes.pending import pending_bp
    from routes.reports import reports_bp
    from routes.archive_2025 import archive_bp
    from routes.public import public_bp
    from routes.settings import settings_bp
    from routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vargani_bp)
    app.register_blueprint(mahaprasad_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(dj_bp)
    app.register_blueprint(daily_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(pending_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(archive_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(audit_bp)

    @app.context_processor
    def inject_globals():
        lang = session.get('lang', 'mr')
        def t(key):
            return get_translation(key, lang)
        
        # Load settings
        try:
            mandal_name = Config.MANDAL_NAME_MR if lang == 'mr' else Config.MANDAL_NAME_EN
            festival_title = Config.FESTIVAL_TITLE_MR if lang == 'mr' else Config.FESTIVAL_TITLE_EN
        except Exception:
            mandal_name = "जागृती चौक सार्वजनिक गणेश मंडळ"
            festival_title = "गणेशोत्सव २०२६ हिशोब व व्यवस्थापन प्रणाली"

        return dict(
            t=t,
            lang=lang,
            mandal_name=mandal_name,
            festival_title=festival_title,
            current_user_name=session.get('full_name'),
            current_user_role=session.get('user_role')
        )

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Listen on host '0.0.0.0' to enable mobile access on local Wi-Fi / Hotspot
    app.run(host='0.0.0.0', port=5000, debug=True)
