# MyApiMovies API Client

This client facilitates MyApiMovies API calls. You only need a token that you can obtain by registering [here](https://www.myapimovies.com/register)

# Init the client

Initialize the class `MyApiMovies` with your token

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')
````

# Examples

## Getting movie by id

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

IMDB_ID_AVENGERS_ENDGAME = 'tt4154796'

response = client.movie(imdb_id=IMDB_ID_AVENGERS_ENDGAME)
first_result = response.data[0]

print(f'ImdbId: {first_result.imdbId}')
print(f'Title: {first_result.title}')
print(f'Year: {first_result.year}')
print(f'Poster: {first_result.posterUrl}')
````

## Search movie

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

title = 'Yesterday'
year = 2019

response = client.movie_search(title=title, year=year)
first_result = response.data[0]

print(f'ImdbId: {first_result.imdbId}')
print(f'Title: {first_result.title}')
print(f'Year: {first_result.year}')
print(f'Poster: {first_result.posterUrl}')
````

## Similar movies

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

IMDB_ID_AVENGERS_ENDGAME = 'tt4154796'

response = client.similar_movies(imdb_id=IMDB_ID_AVENGERS_ENDGAME)
first_result = response.data[0]

print(f'ImdbId: {first_result.imdbId}')
print(f'Title: {first_result.title}')
print(f'Year: {first_result.year}')
print(f'Poster: {first_result.posterUrl}')
````

## Several data at the same time about a movie

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

args = {
    'imdbId': 'tt0133093',
    'actors': 'main==true;page==1',
    'akas': ''
}

response = client.movie_all_in_one(args=args)
first_result = response.data[0]

actors_first_result = first_result.actors.data[0]

print(f'Character: {actors_first_result.character}')
print(f'Character url: {actors_first_result.characterUrl}')
print(f'Main: {actors_first_result.main}')

aka_first_result = first_result.akas.data[0]

print(f'Title: {aka_first_result.title}')
print(f'Country: {aka_first_result.country.country}')

movie_first_result = first_result.movie.data

print(f'ImdbId: {movie_first_result.imdbId}')
print(f'Title: {movie_first_result.title}')
print(f'Year: {movie_first_result.year}')
print(f'Poster: {movie_first_result.posterUrl}')
````

## Search person

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

IMDB_ID_JIM_PARSONS = 'nm1433588'

response = client.name(imdb_id=IMDB_ID_JIM_PARSONS)
first_result = response.data[0]

print(f'ImdbId: {first_result.imdbId}')
print(f'Actor: {first_result.actorActress}')
print(f'Biography: {first_result.biography}')
print(f'Photo: {first_result.photoUrl}')
````

## Several data at the same time about a person

````python
from myapimovies import MyApiMovies

client = MyApiMovies('<TOKEN>')

IMDB_ID_JIM_PARSONS = 'nm1433588'

args = {
    'imdbId': IMDB_ID_JIM_PARSONS,
    'alternative': ''
}

response = client.name_all_in_one(args=args)
first_result = response.data[0]

name_first_result = first_result.name.data

print(f'ImdbId: {name_first_result.imdbId}')
print(f'Actor: {name_first_result.actorActress}')
print(f'Biography: {name_first_result.biography}')
print(f'Photo: {name_first_result.photoUrl}')

alternative_not_found = first_result.alternative

# No alternate name
print(f'Code: {alternative_not_found.code}')
print(f'Error: {alternative_not_found.error}')
````
