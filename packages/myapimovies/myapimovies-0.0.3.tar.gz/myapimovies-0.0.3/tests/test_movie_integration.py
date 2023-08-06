import logging
import unittest

from myapimovies import MyApiMovies

MY_API_MOVIES_TOKEN = '00000000-0000-0000-0000-000000000000'


class TestMovie(unittest.TestCase):

    SEARCH_NAME = 'The Barenaked Ladies'
    IMDB_ID_HOUSE_OF_DRAGON = 'tt11198330'
    IMDB_ID_MAURY = 'tt0120986'
    IMDB_ID_BREAKING_BAD = 'tt0903747'
    IMDB_ID_THE_BIG_BANG_THEORY = 'tt0898266'
    IMDB_ID_AVENGERS_ENDGAME = 'tt4154796'

    IMDB_ID_JIM_PARSONS = 'nm1433588'
    IMDB_ID_KALEY_CUOCO = 'nm0192505'
    IMDB_ID_VIGGO_MORTENSEN = 'nm0001557'

    @classmethod
    def setUpClass(cls):
        super(TestMovie, cls).setUpClass()
        cls.client = MyApiMovies(token=MY_API_MOVIES_TOKEN)

    def test_search_movie(self):
        title = 'Yesterday'
        year = 2019

        response = self.client.movie_search(title=title, year=year)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('tt8735566', first_result.imdbId)
        self.assertEqual('20190125', first_result.releaseDate)
        self.assertEqual(title, first_result.title)
        self.assertEqual('M', first_result.type)
        self.assertEqual(year, int(first_result.year))

    def test_search_russian_movie(self):
        title = 'Союз спасения'
        exact = True

        response = self.client.movie_search(title=title, exact=exact)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('tt8769146', first_result.imdbId)
        self.assertEqual('20191226', first_result.releaseDate)
        self.assertEqual('136 min', first_result.runtime)
        self.assertEqual('Soyuz spaseniya', first_result.title)
        self.assertEqual('M', first_result.type)
        self.assertEqual(2019, int(first_result.year))

    def test_movie(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.movie(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(imdb_id, first_result.imdbId)
        self.assertEqual('https://www.imdb.com/title/tt4154796/', first_result.imdbUrl)
        self.assertTrue(first_result.metascore)
        self.assertTrue(first_result.plot)
        self.assertTrue(first_result.posterUrl)
        self.assertEqual('PG-13', first_result.rated)
        self.assertTrue(first_result.rating)
        self.assertEqual('20190426', first_result.releaseDate)
        self.assertEqual('181', first_result.runtime)
        self.assertTrue(first_result.simplePlot)
        self.assertEqual('Avengers: Endgame', first_result.title)
        self.assertEqual('M', first_result.type)
        self.assertTrue(first_result.votes)
        self.assertEqual('2019', first_result.year)

    def test_movie_trivia(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.movie_trivia(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(20, len(data))

    def test_technicals(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.technicals(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)

        cameras = first_result.cameras
        camera = [x for x in cameras if x == 'Arri Alexa 65 IMAX, Panavision Sphero 65 and Ultra Panatar Lenses']
        self.assertTrue(camera[0])

        cinematographic_processes = first_result.cinematographicProcesses
        process = [x for x in cinematographic_processes if x == 'ARRIRAW (6.5K) (source format)']
        self.assertGreaterEqual(4, len(cinematographic_processes))
        self.assertTrue(process[0])

        colors = first_result.colors
        color = [x for x in colors if x == 'Color (ACES)']
        self.assertLessEqual(1, len(cinematographic_processes))
        self.assertTrue(color[0])

        formats = first_result.filmFormat
        film_format = [x for x in formats if x == 'D-Cinema (also 3-D version)']
        self.assertGreaterEqual(1, len(formats))
        self.assertTrue(film_format[0])

        laboratory = first_result.laboratory
        lab = [x for x in laboratory if x == 'Company 3, Los Angeles (CA), USA (digital intermediate)']
        self.assertGreaterEqual(3, len(laboratory))
        self.assertTrue(lab[0])

        negative_format = first_result.negativeFormat
        negative = [x for x in negative_format if x == 'Codex']
        self.assertGreaterEqual(1, len(negative_format))
        self.assertTrue(negative[0])

        aspect_ratio = first_result.aspectRatio
        aspect = [x for x in aspect_ratio if x == '1.90 : 1 (IMAX version)']
        self.assertLessEqual(1, len(aspect_ratio))
        self.assertTrue(aspect[0])

        runtime = first_result.runtime
        duration = [x for x in runtime if x == '3 hr 1 min (181 min)']
        self.assertGreaterEqual(1, len(runtime))
        self.assertTrue(duration[0])

        sound_mix = first_result.soundMix
        sound = [x for x in sound_mix if x == 'Dolby Atmos']
        self.assertGreaterEqual(9, len(sound_mix))
        self.assertTrue(sound[0])

    def test_movie_quotes(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.movie_quotes(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(20, len(data))

    def test_similar_movies(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.similar_movies(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertGreaterEqual(13, len(data))
        self.assertEqual('tt4154756', first_result.imdbId)
        self.assertEqual('Avengers: Infinity War', first_result.title)

    def test_crew(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.crew(imdb_id=imdb_id)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertLessEqual(2830, total)
        self.assertEqual(20, len(data))

    def test_crew_director(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.crew(imdb_id=imdb_id, type='DIRECTOR')
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertEqual(2, total)

        director_1 = [x for x in data if x.name.imdbId == 'nm0751648'][0].name
        director_2 = [x for x in data if x.name.imdbId == 'nm0751577'][0].name

        self.assertEqual('Joe Russo', director_1.name)
        self.assertEqual('Joseph Vincent Russo', director_1.birthname)
        self.assertEqual('1971-07-08', director_1.birthdate)
        self.assertEqual('Cleveland, Ohio, USA', director_1.placeOfBirth)

        self.assertEqual('Anthony Russo', director_2.name)
        self.assertEqual('Anthony J. Russo', director_2.birthname)
        self.assertEqual('1970-02-03', director_2.birthdate)
        self.assertEqual('Cleveland, Ohio, USA', director_2.placeOfBirth)

    def test_crew_visual_effects(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.crew(imdb_id=imdb_id, type='VISUAL_EFFECTS')
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertLessEqual(total, 2122)

        visual_effects_1 = [x for x in data if x.name.imdbId == 'nm1598727'][0].name
        visual_effects_2 = [x for x in data if x.name.imdbId == 'nm2274754'][0].name

        self.assertEqual('Jen Underdahl', visual_effects_1.name)
        self.assertEqual('Beverly Abbott', visual_effects_2.name)

    def test_crew_visual_effects_page2(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME
        page = 2

        response = self.client.crew(imdb_id=imdb_id, type='VISUAL_EFFECTS', page=page)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertLessEqual(total, 2122)

        visual_effects_1 = [x for x in data if x.name.imdbId == 'nm8239412'][0].name
        visual_effects_2 = [x for x in data if x.name.imdbId == 'nm8345749'][0].name

        self.assertEqual('Lydia Aguilar', visual_effects_1.name)

        self.assertEqual('Wakeel Ahmad', visual_effects_2.name)
        self.assertEqual('Wakeel Ahmad Bhat', visual_effects_2.birthname)
        self.assertEqual('1988-05-15', visual_effects_2.birthdate)
        self.assertEqual('Anantnag Srinagar India', visual_effects_2.placeOfBirth)

    def test_locations(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.locations(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertGreaterEqual(12, len(data))
        self.assertEqual('Durham Cathedral, The College, Durham, County Durham, England, UK', first_result.location)
        self.assertEqual('Thor Meets His Mother In Asgard', first_result.remarks)

    def test_languages(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.languages(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(4, len(data))

    def test_keywords(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.keywords(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(5, len(data))

    def test_goofs(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.goofs(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(9, len(data))

    def test_genres(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.genres(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(3, len(data))

    def test_countries(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.countries(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertEqual(1, len(data))

    def test_business(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.business(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(4, len(data))

        self.assertTrue(first_result.money)
        self.assertTrue(first_result.type)

    def test_awards(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.awards(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(20, len(data))

        filtered_award = [x for x in data if x.award ==
                          'Academy of Science Fiction, Fantasy & Horror Films, USA 2019'][0]
        self.assertTrue(2, len(filtered_award.awards))

        filtered_award_category = [x for x in filtered_award.awards if x.titleAwardOutcome == 'Nominee Saturn Award'][0]
        self.assertTrue(8, len(filtered_award_category.awardsCategories))

        filtered_award_name = [x for x in filtered_award_category.awardsCategories if x.category == 'Best Actor'][0]
        self.assertTrue(1, len(filtered_award_name.awardsNames))

        name = filtered_award_name.awardsNames[0].name
        self.assertEqual('1981-06-13', name.birthdate)
        self.assertEqual('Christopher Robert Evans', name.birthname)
        self.assertEqual('nm0262635', name.imdbId)
        self.assertEqual('Chris Evans', name.name)
        self.assertEqual('Boston, Massachusetts, USA', name.placeOfBirth)

    def test_aka(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.aka(imdb_id=imdb_id)
        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(len(data), 20)

        aka_award = [x for x in data if x.country.country == 'Germany'][0]
        self.assertEqual('Avengers: Endgame', aka_award.title)

    def test_actors(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.actors(imdb_id=imdb_id)
        code = response.code
        total = response.total
        page = response.page
        data = response.data

        self.assertEqual(200, code)
        self.assertLessEqual(160, total)
        self.assertGreaterEqual(1, page)
        self.assertGreaterEqual(20, len(data))

        self.__validate_robert_downey_jr(data)

    def test_actors_page_2(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME
        page = 2

        response = self.client.actors(imdb_id=imdb_id, page=page)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertLessEqual(160, total)
        self.assertGreaterEqual(page, response.page)
        self.assertGreaterEqual(20, len(data))

        actor = [x for x in data if x.character == 'Loki'][0]

        # self.assertEqual(actor.characterUrl, 'https://www.imdb.com/title/tt4154796/characters/nm1089991')
        self.assertEqual(actor.main, False)

        name = actor.name

        self.assertEqual('1981-02-09', name.birthdate)
        self.assertEqual('Thomas William Hiddleston', name.birthname)
        self.assertEqual('nm1089991', name.imdbId)
        self.assertEqual('Tom Hiddleston', name.name)
        self.assertEqual('Westminster, London, England, UK', name.placeOfBirth)

    def test_main_actors(self):
        imdb_id = self.IMDB_ID_AVENGERS_ENDGAME

        response = self.client.actors(imdb_id=imdb_id, main=True)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(18, total)
        self.assertGreaterEqual(18, len(data))

        self.__validate_robert_downey_jr(data)

    def test_coming_soon(self):
        date = '2023-05'

        response = self.client.coming_soon(date=date)
        code = response.code
        data = response.data
        regs = response.regs
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertGreaterEqual(20, regs)

        self.assertEqual(first_result.date, date)
        self.assertTrue(first_result.movie.imdbId)
        self.assertTrue(first_result.movie.imdbUrl)
        self.assertTrue(first_result.movie.posterUrl)
        self.assertTrue(first_result.movie.releaseDate)
        self.assertTrue(first_result.movie.runtime)
        self.assertTrue(first_result.movie.title)
        self.assertEqual('M', first_result.movie.type)
        self.assertEqual('2023', first_result.movie.year)

    def test_seasons(self):
        imdb_id = self.IMDB_ID_BREAKING_BAD
        response = self.client.seasons(imdb_id=imdb_id)

        code = response.code
        data = response.data

        self.assertEqual(200, code)
        self.assertEqual(5, len(data))

        season_start_year = 2008
        season_start = 1
        for season in data:
            self.assertEqual(season_start, season.numSeason)
            self.assertEqual(season_start_year, season.year)
            season_start_year += 1
            season_start += 1

    def test_season(self):
        imdb_id = self.IMDB_ID_HOUSE_OF_DRAGON
        response = self.client.season(imdb_id=imdb_id, season=1)

        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(1, first_result.numSeason)
        self.assertEqual(10, len(first_result.episodes))

        first_episode = first_result.episodes[0]

        self.assertEqual('20220821', first_episode.date)
        self.assertEqual(1, first_episode.episode)
        self.assertEqual('tt11198334', first_episode.imdbId)
        self.assertTrue(first_episode.plot)
        self.assertTrue(first_episode.posterUrl)
        self.assertEqual('The Heirs of the Dragon', first_episode.title)

    def test_season_year(self):
        imdb_id = self.IMDB_ID_MAURY
        year = 1991
        response = self.client.season_year(imdb_id=imdb_id, year=year)

        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(first_result.year, year)
        self.assertEqual(48, len(first_result.episodes))

        first_episode = first_result.episodes[0]

        self.assertEqual('19910101', first_episode.date)
        self.assertEqual(0, first_episode.episode)
        self.assertEqual('tt13116390', first_episode.imdbId)
        self.assertTrue(first_episode.posterUrl)
        self.assertEqual('Episode #1.0', first_episode.title)

    def test_episode(self):
        imdb_id = self.IMDB_ID_HOUSE_OF_DRAGON
        response = self.client.episode(imdb_id=imdb_id, season=1, episode=1)

        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('2022-08-21', first_result.date)
        self.assertEqual(1, first_result.episode)
        self.assertEqual('tt11198334', first_result.imdbId)
        self.assertTrue(first_result.plot)
        self.assertTrue(first_result.posterUrl)
        self.assertEqual('The Heirs of the Dragon', first_result.title)

    def test_episode_es(self):
        imdb_id = self.IMDB_ID_HOUSE_OF_DRAGON
        response = self.client.episode(imdb_id=imdb_id, season=1, episode=1, language='es')

        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('2022-08-21', first_result.date)
        self.assertEqual(1, first_result.episode)
        self.assertEqual('tt11198334', first_result.imdbId)
        self.assertEqual('Viserys prepara un torneo para celebrar el nacimiento de su segundo hijo. Rhaenyra le '
                         'da la bienvenida a su tío Daemon cuando vuelve a la Fortaleza Roja.', first_result.plot)
        self.assertTrue(first_result.posterUrl)
        self.assertEqual('Los herederos del Dragón', first_result.title)

    def test_episode_year(self):
        imdb_id = self.IMDB_ID_MAURY
        year = 1991
        episode = -1
        response = self.client.episode_year(imdb_id=imdb_id, year=year, episode=episode)

        code = response.code
        data = response.data
        total = response.total
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(38, total)
        self.assertEqual('19910109', first_result.date)
        self.assertEqual(episode, first_result.episode)
        self.assertEqual('tt1332266', first_result.imdbId)
        self.assertEqual('Day by day, Maury and his producers invite guests to the show. The audience participates '
                         'and put questions to the guests.', first_result.plot)
        self.assertTrue(first_result.posterUrl)
        self.assertEqual('Kimberly Bergalis', first_result.title)

    def test_movie_photos(self):
        imdb_id = self.IMDB_ID_THE_BIG_BANG_THEORY
        response = self.client.movie_photos(imdb_id=imdb_id)

        code = response.code
        data = response.data
        total = response.total
        page = response.page
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(3673, total)
        self.assertEqual(1, page)
        self.assertEqual('2015 CBS', first_result.copyright)
        self.assertEqual('/mediaviewer/rm1000013568', first_result.galleryUri)
        self.assertEqual(622, first_result.height)
        self.assertEqual('https://m.media-amazon.com/images/M/MV5BMTY1ODMwMzUwOV5BMl5BanBnXkFtZTgwODc5NTA5MzE@._V1_'
                         '.jpg', first_result.imageUrl)
        self.assertEqual('rm1000013568', first_result.imdbId)
        self.assertEqual('Mayim Bialik and Kaley Cuoco in The Big Bang Theory (2007)', first_result.photoCaption)
        self.assertEqual('Mayim Bialik and Kaley Cuoco in The Big Bang Theory (2007)', first_result.title)
        self.assertEqual(800, first_result.width)

        first_name = first_result.names[0]

        self.assertEqual('nm0080524', first_name.imdbId)
        self.assertEqual('Mayim Bialik', first_name.name)

        first_title = first_result.titles[0]

        self.assertEqual('tt0898266', first_title.imdbId)
        self.assertEqual('The Big Bang Theory', first_title.title)

    def test_movie_all_in_one(self):
        args = {
            'imdbId': 'tt0133093',
            'actors': 'main==true;page==1',
            'akas': ''
        }

        response = self.client.movie_all_in_one(args=args)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)

        actors_first_result = first_result.actors.data[0]
        aka_first_result = first_result.akas.data[0]
        movie_first_result = first_result.movie.data

        self.assertEqual('Neo', actors_first_result.character)
        self.assertTrue(actors_first_result.characterUrl)
        self.assertEqual(True, actors_first_result.main)

        bio_first_actor = actors_first_result.name

        self.assertEqual('nm0000206', bio_first_actor.imdbId)
        self.assertEqual('Keanu Reeves', bio_first_actor.name)
        self.assertEqual('Keanu Charles Reeves', bio_first_actor.birthname)
        self.assertEqual('1964-09-02', bio_first_actor.birthdate)
        self.assertEqual('Beirut, Lebanon', bio_first_actor.placeOfBirth)

        self.assertEqual('Matrix', aka_first_result.title)
        self.assertEqual('Argentina', aka_first_result.country.country)

        self.assertEqual('tt0133093', movie_first_result.imdbId)
        self.assertEqual('https://www.imdb.com/title/tt0133093/', movie_first_result.imdbUrl)
        self.assertEqual('73', movie_first_result.metascore)
        self.assertTrue(movie_first_result.plot)
        self.assertTrue(movie_first_result.posterUrl)
        self.assertTrue(movie_first_result.rated)
        self.assertTrue(movie_first_result.rating)
        self.assertEqual('19990611', movie_first_result.releaseDate)
        self.assertEqual('136', movie_first_result.runtime)
        self.assertTrue(movie_first_result.simplePlot)
        self.assertEqual('The Matrix', movie_first_result.title)
        self.assertEqual('M', movie_first_result.type)
        self.assertTrue(movie_first_result.votes)
        self.assertEqual('1999', movie_first_result.year)

    def test_name(self):
        imdb_id = self.IMDB_ID_JIM_PARSONS

        response = self.client.name(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.__validate_jim_parsons(imdb_id, first_result)

    def test_alternative_name(self):
        imdb_id = self.IMDB_ID_KALEY_CUOCO

        response = self.client.alternative(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('Kaley Cuoco-Sweeting', first_result.alternateName)

    def test_filmographies(self):
        imdb_id = self.IMDB_ID_KALEY_CUOCO

        response = self.client.filmographies(imdb_id=imdb_id)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('Actress', first_result.section)

        actress_section = first_result.filmographiesNames[0]
        self.assertEqual('tt7569576', actress_section.imdbId)
        self.assertEqual('The Flight Attendant', actress_section.title)
        self.assertEqual('2018', actress_section.year)
        self.assertEqual('(TV Movie)', actress_section.filmographiesNamesRemarks[0].remark)

    def test_nicknames(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.nicknames(imdb_id=imdb_id)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(3, total)
        self.assertEqual('Vig', data[0].nickname)
        self.assertEqual('Guido', data[1].nickname)
        self.assertEqual('Cuervo', data[2].nickname)

    def test_salaries(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.salaries(imdb_id=imdb_id)
        code = response.code
        total = response.total
        first_result = response.data[0]

        self.assertEqual(200, code)
        self.assertGreaterEqual(3, total)
        self.assertEqual('tt0317648', first_result.imdbId)
        self.assertEqual('$2,000,000', first_result.salary)
        self.assertEqual('Hidalgo', first_result.title)
        self.assertEqual('2004', first_result.year)

    def test_marriages(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.marriages(imdb_id=imdb_id)
        code = response.code
        total = response.total
        first_result = response.data[0]

        self.assertEqual(200, code)
        self.assertGreaterEqual(3, total)
        self.assertEqual('1 child', first_result.childrens)
        self.assertEqual('July 8, 1987', first_result.dateFrom)
        self.assertEqual('March 13, 1998', first_result.dateTo)
        self.assertEqual('nm0148923', first_result.imdbId)
        self.assertEqual('Exene Cervenka', first_result.name)
        self.assertEqual('divorced', first_result.status)

    def test_trademarks(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.trademarks(imdb_id=imdb_id)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(6, total)
        self.assertEqual('Cleft chin', data[0].tradeMark)
        self.assertEqual('Quiet, methodical style of speaking.', data[1].tradeMark)
        self.assertEqual('Often plays rugged but reluctant heroes', data[2].tradeMark)
        self.assertEqual('Frequently cast by David Cronenberg', data[3].tradeMark)
        self.assertEqual('Relaxed naturalistic acting style', data[4].tradeMark)
        self.assertEqual('Soft mellow voice', data[5].tradeMark)

    def test_name_quotes(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.name_quotes(imdb_id=imdb_id)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(29, total)
        self.assertEqual('On the role of an actor in film: "It comes down to the fact that you supply the blue, and '
                         'they supply the other colors and mix them with your blue, and maybe there\'s some blue left '
                         'in the painting and maybe there isn\'t. Maybe there wasn\'t supposed to be any there in the '
                         'first place. So have some fun and make a good blue and walk away."', data[0].quote)
        self.assertEqual('I don\'t plan [my career]; I wait and hope the right thing will find me.', data[1].quote)
        self.assertEqual('Photography, painting or poetry those are just extensions of me, how I perceive things, '
                         'they are my way of communicating.', data[2].quote)
        self.assertEqual('I\'m the one who said yes to these movies, and now I\'m having to pay the price for it. '
                         'I mean if I had my druthers, I wouldn\'t do any movies anymore, frankly.', data[3].quote)

    def test_name_trivia(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN

        response = self.client.name_trivia(imdb_id=imdb_id)
        code = response.code
        total = response.total
        data = response.data

        self.assertEqual(200, code)
        self.assertGreaterEqual(79, total)
        self.assertEqual('He is the ex-husband of Exene Cervenka, the singer of the punk band X.', data[0].trivia)
        self.assertEqual('Had a book of poetry printed before he was known. The title: "Ten Last Night."',
                         data[1].trivia)
        self.assertEqual('Speaks fluent English, Spanish, Danish, and French, but he also speaks yet not fluently '
                         'Catalan, Swedish and Norwegian.', data[2].trivia)
        self.assertEqual('Became a father for the 1st time at age 29 when his [now ex] wife Exene Cervenka gave birth '
                         'to their son Henry Mortensen on January 28, 1988.', data[3].trivia)

    def test_name_photos(self):
        imdb_id = self.IMDB_ID_VIGGO_MORTENSEN
        response = self.client.name_photos(imdb_id=imdb_id)

        code = response.code
        data = response.data
        total = response.total
        page = response.page
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual(665, total)
        self.assertEqual(1, page)
        self.assertEqual('/mediaviewer/rm1005330944', first_result.galleryUri)
        self.assertEqual(672, first_result.height)
        self.assertEqual('https://m.media-amazon.com/images/M/MV5BNmEwOWQ2ZDQtNDUyYS00MTkzLWI0MTUtMjY0YmYyMmJjZTNm'
                         'XkEyXkFqcGdeQXVyMjUyNDk2ODc@._V1_.jpg', first_result.imageUrl)
        self.assertEqual('rm1005330944', first_result.imdbId)
        self.assertEqual('Julianne Moore and Viggo Mortensen in Psycho (1998)', first_result.photoCaption)
        self.assertEqual('Julianne Moore and Viggo Mortensen in Psycho (1998)', first_result.title)
        self.assertEqual(1000, first_result.width)

        first_name = first_result.names[0]

        self.assertEqual('nm0000194', first_name.imdbId)
        self.assertEqual('Julianne Moore', first_name.name)

        first_title = first_result.titles[0]

        self.assertEqual('tt0155975', first_title.imdbId)
        self.assertEqual('Psycho', first_title.title)

    def test_search_name(self):
        name = self.SEARCH_NAME

        response = self.client.name_search(name=name)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)
        self.assertEqual('Actor', first_result.actorActress)
        self.assertEqual('Barenaked Ladies is a Canadian rock band that was formed by Ed Robertson & Steven Page in '
                         'Scarborough, Ontario. In 1989, the Creeggan brothers (Jim Creeggan and Andy Creeggan) '
                         'joined, followed by Tyler Stewart in 1990. Andy left the group in 1995, citing musical '
                         'differences as the cause, and was replaced by Kevin Hearn. Steven Page left the band in '
                         '2009, reducing the group to a quartet.', first_result.biography)
        self.assertEqual('nm1327375', first_result.imdbId)
        self.assertEqual('https://www.imdb.com/name/nm1327375', first_result.imdbUrl)
        self.assertEqual('Barenaked Ladies', first_result.name)
        self.assertEqual('https://m.media-amazon.com/images/S/sash/9FayPGLPcrscMjU.png', first_result.photoUrl)
        self.assertEqual('Barenaked Ladies', first_result.uniqueName)

    def test_name_all_in_one(self):
        args = {
            'imdbId': self.IMDB_ID_JIM_PARSONS,
            'alternative': ''
        }

        response = self.client.name_all_in_one(args=args)
        code = response.code
        data = response.data
        first_result = data[0]

        self.assertEqual(200, code)

        alternative_not_found = first_result.alternative
        name_first_result = first_result.name.data

        self.assertEqual(200, code)
        self.__validate_jim_parsons(self.IMDB_ID_JIM_PARSONS, name_first_result)

        self.assertEqual(404, alternative_not_found.code)
        self.assertEqual('Alternate names not found', alternative_not_found.error)

    def __validate_robert_downey_jr(self, data):
        actor = [x for x in data if x.character == 'Tony Stark'][0]

        self.assertEqual('https://www.imdb.com/title/tt4154796/characters/nm0000375', actor.characterUrl)
        self.assertEqual(True, actor.main)

        name = actor.name

        self.assertEqual('1965-04-04', name.birthdate)
        self.assertEqual('Robert John Downey Jr', name.birthname)
        self.assertEqual('nm0000375', name.imdbId)
        self.assertEqual('Robert Downey Jr.', name.name)
        self.assertEqual('Manhattan, New York City, New York, USA', name.placeOfBirth)

    def __validate_jim_parsons(self, imdb_id, first_result):
        self.assertEqual(imdb_id, first_result.imdbId)
        self.assertEqual('Actor', first_result.actorActress)
        self.assertEqual('Having grown up in Houston, and its northern suburb of Spring, he made his first stage '
                         'appearance in a school play at the age of 6. Parsons then went on to study theater at the '
                         'University of Houston. From there he won a place on a two-year Masters course in classical '
                         'theater at the University of San Diego/The Old Globe Theater, graduating in 2001. He moved '
                         'to New York, working in Off-Broadway productions, appearing in TV commercials and in one '
                         'episode of Ed (2000) before landing a recurring role in Judging Amy (1999) in 2004. He was '
                         'propelled to international fame and acclaim three years later when he starred as Sheldon in '
                         'the award-winning sitcom, The Big Bang Theory (2007).', first_result.biography)
        self.assertEqual('6\' 1¼" (1.86 m)', first_result.height)
        self.assertEqual('https://www.imdb.com/name/nm1433588/', first_result.imdbUrl)
        self.assertTrue('https://m.media-amazon.com/images/M/MV5BMTg1MTkxODgzMF5BMl5BanBnXkFtZTgwMjExMjgyNzM@.'
                        '_V1_UX214_CR0,0,214,317_AL_.jpg', first_result.photoUrl)
        self.assertTrue('Top 5000', first_result.starMeter)
        self.assertTrue('Aries', first_result.starSign)
        self.assertTrue('Jim Parsons (II)', first_result.uniqueName)
        self.assertTrue('James Joseph Parsons', first_result.birthname)
        self.assertTrue('1973-03-24', first_result.birthdate)
        self.assertTrue('Houston, Texas, USA', first_result.placeOfBirth)


if __name__ == '__main__':
    unittest.main()
