import pandas as pd
import ast

# Load dataset
df = pd.read_csv("imdb_data.csv")

# -------------------------------
# 🔍 Data Sanity Checks
# -------------------------------
print("Shape:", df.shape)
print("\nColumns:\n", df.columns)
print("\nMissing Values:\n", df.isnull().sum())

# Convert JSON-like columns safely
def convert_json_column(col):
    return col.apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])

json_cols = ['genres', 'cast', 'crew']
for col in json_cols:
    df[col] = convert_json_column(df[col])

# -------------------------------
# Helper functions
# -------------------------------
def get_director(crew_list):
    for person in crew_list:
        if person.get('job') == 'Director':
            return person.get('name')
    return None

def get_producer(crew_list):
    producers = [p.get('name') for p in crew_list if p.get('job') == 'Producer']
    return producers

def get_cast_names(cast_list):
    return [actor.get('name') for actor in cast_list]

# -------------------------------
# Add useful columns
# -------------------------------
df['director'] = df['crew'].apply(get_director)
df['producers'] = df['crew'].apply(get_producer)
df['cast_names'] = df['cast'].apply(get_cast_names)

# Profit & ROI
df['profit'] = df['revenue'] - df['budget']
df['roi'] = df['profit'] / df['budget']
df = df[df['budget'] > 0]  # avoid division issues

# -------------------------------
# 1️⃣ Highest Profit Movie
# -------------------------------
highest_profit_movie = df.loc[df['profit'].idxmax()]

print("\n1. Highest Profit Movie:")
print("Title:", highest_profit_movie['title'])
print("Profit:", highest_profit_movie['profit'])
print("Director:", highest_profit_movie['director'])
print("Producers:", highest_profit_movie['producers'])
print("Actors:", highest_profit_movie['cast_names'])

# -------------------------------
# 2️⃣ Language with highest average ROI
# -------------------------------
lang_roi = df.groupby('original_language')['roi'].mean().sort_values(ascending=False)

print("\n2. Language with highest average ROI:")
print(lang_roi.head(1))

# -------------------------------
# 3️⃣ Unique Genres
# -------------------------------
all_genres = set()

for genres in df['genres']:
    for g in genres:
        all_genres.add(g['name'])

print("\n3. Unique Genres:")
print(all_genres)

# -------------------------------
# 4️⃣ Top 3 Producers by Avg ROI
# -------------------------------
producer_data = []

for _, row in df.iterrows():
    for producer in row['producers']:
        producer_data.append({
            'producer': producer,
            'roi': row['roi']
        })

producer_df = pd.DataFrame(producer_data)

top_producers = producer_df.groupby('producer')['roi'].mean().sort_values(ascending=False).head(3)

print("\n4. Top 3 Producers by Avg ROI:")
print(top_producers)

# -------------------------------
# 5️⃣ Actor with most movies
# -------------------------------
actor_list = []

for _, row in df.iterrows():
    for actor in row['cast_names']:
        actor_list.append({
            'actor': actor,
            'title': row['title'],
            'genres': [g['name'] for g in row['genres']],
            'profit': row['profit']
        })

actor_df = pd.DataFrame(actor_list)

top_actor = actor_df['actor'].value_counts().idxmax()

print("\n5. Actor with most movies:", top_actor)

actor_movies = actor_df[actor_df['actor'] == top_actor]

print("\nMovies by this actor:")
print(actor_movies[['title', 'genres', 'profit']])

# -------------------------------
# 6️⃣ Top 3 Directors & their preferred actors
# -------------------------------
director_actor = []

for _, row in df.iterrows():
    director = row['director']
    for actor in row['cast_names']:
        director_actor.append({
            'director': director,
            'actor': actor
        })

director_actor_df = pd.DataFrame(director_actor)

top_directors = df['director'].value_counts().head(3).index

print("\n6. Top 3 Directors & their preferred actors:")

for director in top_directors:
    subset = director_actor_df[director_actor_df['director'] == director]
    top_actor = subset['actor'].value_counts().head(1)
    
    print(f"\nDirector: {director}")
    print("Most frequent actor:")
    print(top_actor)
