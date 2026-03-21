from flask import Blueprint, render_template, request, jsonify
import requests
import os

movies_blueprint = Blueprint('movies', __name__)

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_API_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/w500'

@movies_blueprint.route('/')
def index():
    popular_movies_url = f"{TMDB_API_URL}/trending/movie/week"
    popular_tv_url = f"{TMDB_API_URL}/trending/tv/week"
    params = {'api_key': TMDB_API_KEY}
    
    movies_response = requests.get(popular_movies_url, params=params)
    popular_movies = movies_response.json().get('results', []) if movies_response.status_code == 200 else []
    for movie in popular_movies:
        movie['media_type'] = 'movie'

    tv_response = requests.get(popular_tv_url, params=params)
    popular_tv = tv_response.json().get('results', []) if tv_response.status_code == 200 else []
    for show in popular_tv:
        show['media_type'] = 'tv'

    return render_template("index.html", popular_media=popular_movies + popular_tv, image_url=TMDB_IMAGE_URL)

@movies_blueprint.route('/search')
def search():
    query = request.args.get('q')
    media_type = request.args.get('type', 'movie')
    
    popular_movies_url = f"{TMDB_API_URL}/trending/movie/week"
    popular_tv_url = f"{TMDB_API_URL}/trending/tv/week"
    params = {'api_key': TMDB_API_KEY}
    
    movies_response = requests.get(popular_movies_url, params=params)
    popular_movies = movies_response.json().get('results', []) if movies_response.status_code == 200 else []
    for movie in popular_movies:
        movie['media_type'] = 'movie'

    tv_response = requests.get(popular_tv_url, params=params)
    popular_tv = tv_response.json().get('results', []) if tv_response.status_code == 200 else []
    for show in popular_tv:
        show['media_type'] = 'tv'

    if not query:
        return render_template("index.html", error="Please enter a search query.", popular_media=popular_movies + popular_tv, image_url=TMDB_IMAGE_URL)

    search_url = f"{TMDB_API_URL}/search/{media_type}"
    params = {'api_key': TMDB_API_KEY, 'query': query}
    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        for item in results:
            item['media_type'] = media_type
        return render_template("index.html", search_results=results, query=query, media_type=media_type, image_url=TMDB_IMAGE_URL, popular_media=popular_movies + popular_tv)
    else:
        return render_template("index.html", error="Could not fetch results. Please check the API key and try again.", popular_media=popular_movies + popular_tv, image_url=TMDB_IMAGE_URL)

@movies_blueprint.route('/details/<media_type>/<int:tmdb_id>')
def details(media_type, tmdb_id):
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    external_ids_params = {'api_key': TMDB_API_KEY}

    if media_type == 'movie':
        details_url = f"{TMDB_API_URL}/movie/{tmdb_id}"
        external_ids_url = f"{TMDB_API_URL}/movie/{tmdb_id}/external_ids"
        
        details_response = requests.get(details_url, params=params)
        external_ids_response = requests.get(external_ids_url, params=external_ids_params)

        if details_response.status_code == 200 and external_ids_response.status_code == 200:
            external_ids_data = external_ids_response.json()
            imdb_id = external_ids_data.get('imdb_id')
            if imdb_id:
                return jsonify({
                    'tmdb_id': tmdb_id,
                    'imdb_id': imdb_id,
                    'media_type': 'movie'
                })

    elif media_type == 'tv':
        details_url = f"{TMDB_API_URL}/tv/{tmdb_id}"
        external_ids_url = f"{TMDB_API_URL}/tv/{tmdb_id}/external_ids"
        
        details_response = requests.get(details_url, params=params)
        external_ids_response = requests.get(external_ids_url, params=external_ids_params)
        
        if details_response.status_code == 200 and external_ids_response.status_code == 200:
            details_data = details_response.json()
            external_ids_data = external_ids_response.json()
            imdb_id = external_ids_data.get('imdb_id')
            seasons = details_data.get('seasons', [])
            # Filter out seasons with no episodes or season number 0 ("Specials")
            valid_seasons = [s for s in seasons if s.get('episode_count', 0) > 0 and s.get('season_number') != 0]

            if imdb_id:
                return jsonify({
                    'tmdb_id': tmdb_id,
                    'imdb_id': imdb_id,
                    'media_type': 'tv',
                    'seasons': valid_seasons
                })

    return jsonify({'error': 'Could not find the required information for this selection.'}), 404
