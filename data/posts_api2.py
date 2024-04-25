from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from .posts import Posts

app = Flask(__name__)
api = Api(app)


def main():
    app.run()


if __name__ == '__main__':
    main()

@app.errorhandler(404)
def abort_if_posts_not_found(post_id):
    session = db_session.create_session()
    news = session.query(Posts).get(post_id)
    if not news:
        abort(404, message=f"Post {post_id} not found")