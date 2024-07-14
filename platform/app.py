from flask import Flask, render_template


app = Flask(__name__)

import config



import routes


"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
"""


if __name__ == '__main__':
    app.run(debug=True)
