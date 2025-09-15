import sqlite3
import pandas as pd

basics = pd.read_csv(
    "tsv_data/title.basics.tsv",
    sep="\t",
    dtype=str,
    na_values="\\N",
    on_bad_lines='skip'   # skip malformed lines
)
ratings = pd.read_csv(
    "tsv_data/title.ratings.tsv",
    sep="\t",
    dtype=str,
    na_values="\\N",
    on_bad_lines='skip'   # skip malformed lines
)

movies = pd.merge(basics, ratings, on='tconst', how='left')

movies['runtimeMinutes'] = pd.to_numeric(movies['runtimeMinutes'], errors='coerce')
movies['averageRating'] = pd.to_numeric(movies['averageRating'], errors='coerce')
movies['numVotes'] = pd.to_numeric(movies['numVotes'], errors='coerce')

conn = sqlite3.connect("movies.db")
movies.to_sql("movies", conn, if_exists="replace", index=False)
conn.close()