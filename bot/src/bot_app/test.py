from flask import Flask, render_template
from flask_babel import Babel, gettext

app = Flask(__name__)
babel = Babel(app)

@babel.localeselector()
def get_locale():
    return 'uk'  # Отримуйте мову з сесії або запиту

@app.route('/')
def hello_world():
    return gettext('Hello, World!')

if __name__ == '__main__':
    app.run()
