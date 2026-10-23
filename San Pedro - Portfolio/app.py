import os

from flask import Flask

base_dir = os.path.abspath(os.path.dirname(__file__))
portfolio_dir = os.path.join(base_dir, 'portfolio')


def load_local_settings():
    settings_path = os.path.join(base_dir, '.env')
    if not os.path.isfile(settings_path):
        return

    with open(settings_path, encoding='utf-8-sig') as settings_file:
        for line_number, line in enumerate(settings_file, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise ValueError(f'Invalid .env entry on line {line_number}: expected KEY=VALUE.')

            key, value = (part.strip() for part in line.split('=', 1))
            if not key:
                raise ValueError(f'Invalid .env entry on line {line_number}: key cannot be empty.')
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            os.environ.setdefault(key, value)


load_local_settings()

app = Flask(
    __name__,
    template_folder=os.path.join(portfolio_dir, 'templates'),
    static_folder=os.path.join(portfolio_dir, 'static'),
)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)

from portfolio.Python.Area import bp

app.register_blueprint(bp)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
