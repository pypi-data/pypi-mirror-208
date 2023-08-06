# -*- coding: utf-8 -*-
import json
from collections import namedtuple
from typing import Optional

import requests
from requests.models import PreparedRequest

import logging


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class MandatoryParameterException(Error):
    def __init__(self, message):
        self.message = message


class ResponseException(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ResponseData(object):
    def __init__(self, data=None, code=None, total=None, page=None, regs=None):
        self.data = data
        self.code = code
        self.total = total
        self.page = page
        self.regs = regs


class MyApiMovies(object):
    __URL_BASE = 'https://www.myapimovies.com/api/v1'
    __URL_BASE_MOVIE = '{}/movie'.format(__URL_BASE)
    __URL_BASE_NAME = '{}/name'.format(__URL_BASE)

    __URI_TMDB = '/tmdb'
    __URI_MOVIE = '/movie'
    __URI_MOVIE_TRIVIA = '/{}/trivias'
    __URI_MOVIE_TECHNICALS = '/{}/technicals'
    __URI_MOVIE_QUOTES = '/{}/quotes'
    __URI_MOVIE_PHOTOS = '/{}/photos'
    __URI_MOVIE_LOCATIONS = '/{}/locations'
    __URI_MOVIE_LANGUAGES = '/{}/languages'
    __URI_MOVIE_KEYWORDS = '/{}/keywords'
    __URI_MOVIE_GOOFS = '/{}/goofs'
    __URI_MOVIE_GENRES = '/{}/genres'
    __URI_MOVIE_COUNTRIES = '/{}/countries'
    __URI_MOVIE_BUSINESS = '/{}/business'
    __URI_MOVIE_AWARDS = '/{}/awards'
    __URI_MOVIE_AKAS = '/{}/akas'
    __URI_MOVIE_ACTORS = '/{}/actors'
    __URI_MOVIE_COMING_SOON = '/coming-soon/{}'
    __URI_MOVIE_SIMILAR_MOVIES = '/{}/similar-movies'
    __URI_MOVIE_SEARCH = '/search'
    __URI_MOVIE_CREW = '/{}/crew'
    __URI_SERIE_SEASONS = '/{}/season'
    __URI_SERIE_SEASON = '/{}/season/{}'
    __URI_SERIE_SEASON_YEAR = '/{}/season/year/{}'
    __URI_EPISODE = '/{}/season/{}/episode/{}'
    __URI_EPISODE_YEAR = '/{}/season/year/{}/episode/{}'
    __URI_ALL_IN_ONE = '/all-in-one'

    __URI_NAME_ALTERNATIVE = '/{}/alternative'
    __URI_NAME_FILMOGRAPHIES = '/{}/filmographies'
    __URI_NAME_NICKNAMES = '/{}/nicknames'
    __URI_NAME_SALARIES = '/{}/salaries'
    __URI_NAME_MARRIAGES = '/{}/marriages'
    __URI_NAME_TRADEMARKS = '/{}/trade-marks'
    __URI_NAME_QUOTES = '/{}/quotes'
    __URI_NAME_TRIVIA = '/{}/trivias'
    __URI_NAME_PHOTOS = '/{}/photos'
    __URI_NAME_SEARCH = '/search'

    def __init__(self, token, log_level=logging.INFO):
        self.token = token

        logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    def __build_result(self, url, **query_params):
        movie_result = []

        headers = {'X-API-KEY': self.token}

        req = PreparedRequest()
        req.prepare_url(url, query_params)

        logging.info('Calling to url %s', req.url)

        response_url = requests.get(req.url, headers=headers)
        response_url.encoding = 'utf-8'
        response_json = json.loads(response_url.text)

        if response_url.status_code == 200:
            data = response_json['data']
            if isinstance(data, dict):
                movie = json.loads(json.dumps(data), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                movie_result.append(movie)
            else:
                for result_data in data:
                    movie = json.loads(json.dumps(result_data), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                    movie_result.append(movie)
        else:
            code = response_json['code'] if 'code' in response_json else response_json['status']
            message = response_json['error']
            logging.error("Request error %d: %s", code, message)
            raise ResponseException(code, message)

        total = response_json['total'] if 'total' in response_json else None
        page = response_json['page'] if 'page' in response_json else None

        response_data = ResponseData(data=movie_result, code=response_json['code'], total=total, page=page,
                                     regs=response_json['regs'])

        return response_data

    def movie_search(self, title, year: Optional[int] = None, type: Optional[str] = None, exact: Optional[bool] = None,
                     page: Optional[int] = None):
        search_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_SEARCH}'

        if not title:
            raise MandatoryParameterException('Title parameter is mandatory')

        return self.__build_result(search_url, title=title, year=year, type=type, exact=exact, page=page)

    def movie(self, imdb_id):
        imdb_url = f'{self.__URL_BASE_MOVIE}/{imdb_id}'
        return self.__build_result(imdb_url)

    def movie_trivia(self, imdb_id, page: Optional[int] = None):
        trivia_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_TRIVIA.format(imdb_id)}'
        return self.__build_result(trivia_url, page=page)

    def technicals(self, imdb_id):
        technicals_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_TECHNICALS.format(imdb_id)}'
        return self.__build_result(technicals_url)

    def similar_movies(self, imdb_id, page: Optional[int] = None):
        similar_movies_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_SIMILAR_MOVIES.format(imdb_id)}'
        return self.__build_result(similar_movies_url, page=page)

    def crew(self, imdb_id, type: Optional[str] = None, page: Optional[int] = None):
        crew_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_CREW.format(imdb_id)}'
        return self.__build_result(crew_url, type=type, page=page)

    def seasons(self, imdb_id, page: Optional[int] = None):
        season_url = f'{self.__URL_BASE_MOVIE}{self.__URI_SERIE_SEASONS.format(imdb_id)}'
        return self.__build_result(season_url, page=page)

    def season(self, imdb_id, season, page: Optional[int] = None):
        season_url = f'{self.__URL_BASE_MOVIE}{self.__URI_SERIE_SEASON.format(imdb_id, season)}'
        return self.__build_result(season_url, page=page)

    def season_year(self, imdb_id, year):
        season_url = f'{self.__URL_BASE_MOVIE}{self.__URI_SERIE_SEASON_YEAR.format(imdb_id, year)}'
        return self.__build_result(season_url)

    def episode(self, imdb_id, season, episode, language=None, source='tmdb'):
        episode_uri = self.__URI_EPISODE.format(imdb_id, season, episode)
        source_uri = ''
        if source == 'tmdb':
            source_uri = self.__URI_TMDB

        episode_url = f'{self.__URL_BASE}{source_uri}{self.__URI_MOVIE}{episode_uri}'

        return self.__build_result(episode_url, language=language)

    def episode_year(self, imdb_id, year, episode, page: Optional[int] = None):
        episode_url = f'{self.__URL_BASE_MOVIE}{self.__URI_EPISODE_YEAR.format(imdb_id, year, episode)}'
        return self.__build_result(episode_url, page=page)

    def movie_quotes(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_QUOTES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def movie_photos(self, imdb_id, page: Optional[int] = None):
        photos_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_PHOTOS.format(imdb_id)}'
        return self.__build_result(photos_url, page=page)

    def locations(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_LOCATIONS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def languages(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_LANGUAGES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def keywords(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_KEYWORDS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def goofs(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_GOOFS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def genres(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_GENRES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def countries(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_COUNTRIES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def business(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_BUSINESS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def awards(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_AWARDS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def aka(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_AKAS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def actors(self, imdb_id: str, main: Optional[bool] = None, page: Optional[int] = None):
        actor_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_ACTORS.format(imdb_id)}'
        args = {}

        if main:
            args['main'] = main

        if page:
            args['page'] = page

        return self.__build_result(actor_url, main=main, page=page)

    def coming_soon(self, date: str, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_MOVIE}{self.__URI_MOVIE_COMING_SOON.format(date)}'
        return self.__build_result(quotes_url, page=page)

    def movie_all_in_one(self, args: dict):
        aio_url = f'{self.__URL_BASE_MOVIE}{self.__URI_ALL_IN_ONE}'
        return self.__build_result(aio_url, **args)

    def name(self, imdb_id):
        imdb_url = f'{self.__URL_BASE_NAME}/{imdb_id}'
        return self.__build_result(imdb_url)

    def alternative(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_ALTERNATIVE.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def filmographies(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_FILMOGRAPHIES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def nicknames(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_NICKNAMES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def salaries(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_SALARIES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def marriages(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_MARRIAGES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def trademarks(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_TRADEMARKS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def name_quotes(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_QUOTES.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def name_trivia(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_TRIVIA.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def name_photos(self, imdb_id, page: Optional[int] = None):
        quotes_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_PHOTOS.format(imdb_id)}'
        return self.__build_result(quotes_url, page=page)

    def name_search(self, name, exact: Optional[bool] = None, page: Optional[int] = None):
        search_url = f'{self.__URL_BASE_NAME}{self.__URI_NAME_SEARCH}'

        if not name:
            raise MandatoryParameterException('Name parameter is mandatory')

        return self.__build_result(search_url, name=name, exact=exact, page=page)

    def name_all_in_one(self, args: dict):
        aio_url = f'{self.__URL_BASE_NAME}{self.__URI_ALL_IN_ONE}'
        return self.__build_result(aio_url, **args)

