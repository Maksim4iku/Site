import flask

from . import db_session
from .posts import Posts
from flask import jsonify, make_response, request

blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts/<int:posts_id>', methods=['DELETE'])
def delete_posts(posts_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(News).get(posts_id)
    if not posts:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts', methods=['POST'])
def create_posts():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    posts = News(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private']
    )
    db_sess.add(posts)
    db_sess.commit()
    return jsonify({'id': posts.id})


@blueprint.route('/api/posts/<int:posts_id>', methods=['GET'])
def get_one_posts(posts_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(posts_id)
    if not posts:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'posts': posts.to_dict(only=(
                'title', 'content', 'user_id', 'is_private'))
        }
    )
