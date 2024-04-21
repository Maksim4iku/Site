from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify

app = Flask(__name__)
api = Api(app)


def main():
    app.run()


if __name__ == '__main__':
    main()

@app.errorhandler(404)
def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")