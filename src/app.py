from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import requests
from filter_movies import get_movies
from scraper import scrape_info, generate_sentiment
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    genre = data.get("genre")
    min_runtime = data.get("min_runtime")
    max_runtime = data.get("max_runtime")
    start_year = data.get("start_year")
    end_year = data.get("end_year")
    title_type = data.get("title_type", "movie")
    limit = data.get("limit", 10)

    filtered_movies = get_movies(
        genre=genre,
        min_runtime=min_runtime,
        max_runtime=max_runtime,
        start_year=start_year,
        end_year=end_year,
        title_type=title_type,
        limit=limit
    )

    results = []
    for movie in filtered_movies:
        scraped_data = scrape_info(movie['tconst'])
        
        # call llm:
        
        reviews = [r['node']['text']['originalText']['plainText'] for r in scraped_data[1]]
        pro_con = generate_sentiment(reviews)
        # create movie obj
        movie = {
            "title" : movie["primaryTitle"],
            "imdb" : movie["averageRating"],
            "num_votes": movie["numVotes"],
            "year":movie["startYear"],
            "pros":pro_con["pros"],
            "cons":pro_con["cons"]
        }
        results.append(movie)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
