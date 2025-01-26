import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

ratings_file = "C:\\Users\\Samruddhi\\Downloads\\ml-1m\\ml-1m\\ratings.dat"
movies_file = "C:\\Users\\Samruddhi\\Downloads\\ml-1m\\ml-1m\\movies.dat"
users_file = "C:\\Users\\Samruddhi\\Downloads\\ml-1m\\ml-1m\\users.dat"

movie_details = {}
movie_genres = set()
with open(movies_file, "r", encoding="ISO-8859-1") as file:
    for line in file:
        movie_id, title, genres = line.strip().split("::")
        movie_id = int(movie_id)
        genres = genres.split("|")
        movie_details[movie_id] = {"title": title, "genres": genres}
        movie_genres.update(genres)

user_details = {}
age_groups = {
    1: "<18",
    18: "18-24",
    25: "25-34",
    35: "35-44",
    45: "45-49",
    50: "50-55",
    56: "56+",
}
with open(users_file, "r", encoding="ISO-8859-1") as file:
    for line in file:
        user_id, gender, age, occupation, _ = line.strip().split("::")
        user_id = int(user_id)
        age = int(age)
        user_details[user_id] = {"gender": gender, "age_group": age_groups[age]}

ratings = []
with open(ratings_file, "r", encoding="ISO-8859-1") as file:
    for line in file:
        user_id, movie_id, rating, _ = line.strip().split("::")
        user_id = int(user_id)
        movie_id = int(movie_id)
        rating = float(rating)
        ratings.append((user_id, movie_id, rating))

st.title("Movie Data Visualizations")
st.sidebar.title("Options")

visualization = st.sidebar.selectbox(
    "Select Visualization:",
    [
        "Distribution of Ratings by Genres and Years",
        "Popular Genres by User Demographics",
        "Heatmaps Showing Correlation Between Genres, User Activity, and Ratings",
    ],
)

if visualization == "Distribution of Ratings by Genres and Years":
    st.header("Distribution of Ratings by Genres and Years")
    genre_ratings = defaultdict(list)
    year_ratings = defaultdict(list)

    for user_id, movie_id, rating in ratings:
        if movie_id in movie_details:
            genres = movie_details[movie_id]["genres"]
            for genre in genres:
                genre_ratings[genre].append(rating)
            if "(" in movie_details[movie_id]["title"] and ")" in movie_details[movie_id]["title"]:
                year = movie_details[movie_id]["title"].split("(")[-1].replace(")", "")
                if year.isdigit():
                    year_ratings[int(year)].append(rating)

    avg_genre_ratings = {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
    genres, avg_ratings = zip(*sorted(avg_genre_ratings.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    sns.barplot(x=avg_ratings, y=genres, palette="cool")
    plt.xlabel("Average Rating")
    plt.ylabel("Genre")
    plt.title("Average Ratings by Genre")
    st.pyplot(plt)

    avg_year_ratings = {year: np.mean(ratings) for year, ratings in year_ratings.items()}
    years, avg_ratings = zip(*sorted(avg_year_ratings.items()))

    plt.figure(figsize=(10, 6))
    plt.plot(years, avg_ratings, marker="o", color="green")
    plt.xlabel("Year")
    plt.ylabel("Average Rating")
    plt.title("Average Ratings by Year")
    st.pyplot(plt)

elif visualization == "Popular Genres by User Demographics":
    st.header("Popular Genres by User Demographics")
    age_group_genres = defaultdict(lambda: defaultdict(list))

    for user_id, movie_id, rating in ratings:
        if user_id in user_details and movie_id in movie_details:
            age_group = user_details[user_id]["age_group"]
            genres = movie_details[movie_id]["genres"]
            for genre in genres:
                age_group_genres[age_group][genre].append(rating)

    age_group_avg_ratings = {
        age_group: {
            genre: np.mean(ratings)
            for genre, ratings in genres.items()
        }
        for age_group, genres in age_group_genres.items()
    }

    for age_group, genre_ratings in age_group_avg_ratings.items():
        genres = list(genre_ratings.keys())
        avg_ratings = list(genre_ratings.values())
        st.subheader(f"Age Group: {age_group}")
        plt.figure(figsize=(10, 6))
        sns.barplot(x=avg_ratings, y=genres, palette="viridis")
        plt.xlabel("Average Rating")
        plt.ylabel("Genre")
        plt.title(f"Popular Genres for Age Group: {age_group}")
        st.pyplot(plt)

elif visualization == "Heatmaps Showing Correlation Between Genres, User Activity, and Ratings":
    st.header("Heatmaps Showing Correlation Between Genres, User Activity, and Ratings")
    genre_stats = {genre: {"Total Ratings": 0, "Rating Count": 0} for genre in movie_genres}

    for user_id, movie_id, rating in ratings:
        if movie_id in movie_details:
            genres = movie_details[movie_id]["genres"]
            for genre in genres:
                genre_stats[genre]["Total Ratings"] += rating
                genre_stats[genre]["Rating Count"] += 1

    for genre, stats in genre_stats.items():
        stats["Average Rating"] = stats["Total Ratings"] / stats["Rating Count"] if stats["Rating Count"] > 0 else 0
        stats["User Activity"] = stats["Rating Count"]

    genres = list(genre_stats.keys())
    user_activity = [genre_stats[genre]["User Activity"] for genre in genres]
    total_ratings = [genre_stats[genre]["Total Ratings"] for genre in genres]
    average_ratings = [genre_stats[genre]["Average Rating"] for genre in genres]

    data_matrix = np.array([user_activity, total_ratings, average_ratings])
    correlation_matrix = np.corrcoef(data_matrix)

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        xticklabels=["User Activity", "Total Ratings", "Average Rating"],
        yticklabels=["User Activity", "Total Ratings", "Average Rating"],
        cmap="plasma",
    )
    st.pyplot(plt)