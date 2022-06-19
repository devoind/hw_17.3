# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource
from schemas import movie_schema, movies_schema
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        """
        Функция запроса информации по всем фильмам, а также фильм по id директора и жанра

        :return: возвращает список всех фильмов, а также фильм по id директора и жанра
        """
        movie_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description,
                                                         Movie.rating, Movie.trailer, Genre.name.label('genre'),
                                                         Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.genre_id == genre_id)

        all_movies = movie_with_genre_and_director.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        """
        Функция добавления нового фильма

        :return: возвращает добавленный фильм по id
        """
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект c id {new_movie.id} создан", 201


@movie_ns.route('/<int:movie_id>')
class MovieView(Resource):
    def get(self, movie_id):
        """
        Функция вывода фильма по id

        :param movie_id: получает id
        :return: возвращает фильм по id
        """
        movie = db.session.query(Movie.id, Movie.title, Movie.description,
                                 Movie.rating, Movie.trailer, Genre.name.label('genre'),
                                 Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == movie_id).first()
        if movie:
            return movie_schema.dump(movie), 200
        return "Нет такого фильма", 404

    def patch(self, movie_id):
        """
        Функция обновления информации о фильме по id

        :param movie_id: получает id
        :return: возвращает сообщение об обновленном фильме по id или информацию, что такого фильма не найдено
        """
        movie = db.session.query(Movie).get(movie_id)

        if not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Объект c id {movie_id} обновлен", 204

    def put(self, movie_id):
        """
        Функция обновления информации о фильме по id

        :param movie_id: получает id
        :return: возвращает сообщение об обновленном фильме по id или информацию, что такого фильма не найдено
        """
        movie = db.session.query(Movie).get(movie_id)

        if not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Объект c id {movie_id} обновлен", 204

    def delete(self, movie_id):
        """
        Функция удаления информации о фильме по id

        :param movie_id: получает id
        :return: возвращает сообщение об удаленном фильме по id или информацию, что такого фильма не найдено
        """
        movie = db.session.query(Movie).get(movie_id)

        if not movie:
            return "Нет такого фильма", 404

        db.session.delete(movie)
        db.session.commit()
        return f"Объект c id {movie_id} удален", 204


if __name__ == '__main__':
    app.run(debug=True)
