from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News
import datetime
import jinja2
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.run(debug=True)

@app.route("/servedata")
def send_data():
    return render_template("file.html", values=["value1", "value2", "value3"])

if __name__ == '__main__':
    main()
