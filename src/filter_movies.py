import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_movies(
    genre=None,
    min_runtime=None,
    max_runtime=None,
    start_year=None,
    end_year=None,
    title_type="movie",  # default to movie
    limit=10
):
    conn = sqlite3.connect("movies.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if title_type:
        query += " AND titleType = ?"
        params.append(title_type)

    if genre:
        query += " AND genres LIKE ?"
        params.append(f"%{genre}%")
    if min_runtime:
        query += " AND runtimeMinutes >= ?"
        params.append(min_runtime)
    if max_runtime:
        query += " AND runtimeMinutes <= ?"
        params.append(max_runtime)
    if start_year:
        query += " AND startYear >= ?"
        params.append(str(start_year))
    if end_year:
        query += " AND startYear <= ?"
        params.append(str(end_year))

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]





if __name__ == "__main__":
    # get old movies over 3 hours
    res = get_movies(genre = None, min_runtime = 180, start_year=  1980, end_year= 1982, limit = 1)
    print(res)