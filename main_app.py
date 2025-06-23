import streamlit as st
import os

from get_user_reviews import *
from main_genre_book_recommender import *
from user_review_cache_class import UserReviewCache
from concurrent.futures import ThreadPoolExecutor

@st.cache_data
def interface_loader(file_paths):
    def load_file(path):
        s = time.time()
        file_name = os.path.basename(path)
        df = pd.read_parquet(path)
        e = time.time()
        print(f"Time for {file_name}: {(e-s):.1f} seconds")
        return file_name, df

    data_dict = {}
    with ThreadPoolExecutor() as executor:
        results = executor.map(load_file, file_paths)
        for name, df in results:
            data_dict[name] = df
    return data_dict

file_paths = ["data/all_books_final.parquet",
              "data/users_data.parquet",
              "data/genre_labels.parquet",
              "data/all_labeled_reviews.parquet",
              "data/compact_user_genre_pct.parquet",
              "data/main_user_item_matrix.parquet"]

st.set_page_config(page_title="User Reviews", layout="wide")
col1, col2, col3, col4, col5 = st.columns([2, .5, 2, .5, 6]) 

def genre_subtext(title):
    st.write("")
    st.write("")
    st.write(f"**{title}**")


with col1:
    st.write("")
    st.subheader("📚 Your genres")
    genre_subtext("Fiction")

    # Fiction 
    classics = st.slider("Classics", 0, 100, key="Classics")
    contemporary = st.slider("Contemporary", 0, 100, key="Contemporary")
    fantasy = st.slider("Fantasy", 0, 100, key="Fantasy")
    historical_fiction = st.slider("Historical fiction", 0, 100, key="Historical Fiction")
    horror = st.slider("Horror", 0, 100, key="Horror")
    mystery = st.slider("Mystery", 0, 100, key="Mystery")
    romance = st.slider("Romance", 0, 100, key="Romance")
    science_fiction = st.slider("Science fiction", 0, 100, key="Science Fiction")
    young_adult = st.slider("Young adult", 0, 100, key="Young Adult")

with col3:
    st.subheader("")
    genre_subtext("Nonfiction")

    # Fiction 
    art = st.slider("Art", 0, 100, key="Art")
    biography = st.slider("Biography", 0, 100, key="Biography")
    business = st.slider("Business", 0, 100, key="Business")
    history = st.slider("History", 0, 100, key="History")
    music = st.slider("Music", 0, 100, key="Music")
    philosophy = st.slider("Philosophy", 0, 100, key="Philosophy")
    psychology = st.slider("Psychology", 0, 100, key="Psychology")
    science = st.slider("Science", 0, 100, key="Science")
    self_help = st.slider("Self help", 0, 100, key="Self Help")

nonfiction_genres = [
 'Art',
 'Biography',
 'Business',
 'History',
 'Music',
 'Philosophy',
 'Psychology',
 'Science',
 'Self Help']

fiction_values = [st.session_state[g]/100 for g in fiction_genres]
nonfiction_values = [st.session_state[g]/100 for g in nonfiction_genres]

def set_sliders(genre_values_dict: dict):
    for k,v in genre_values_dict.items():
        st.session_state[k] = v
    return


def load_user_reviews_button(user_id, genre_labels, fiction_genres, nonfiction_genres):
    if user_id.strip() == "":
            st.error("Please enter a valid user ID.")
    else:
        with st.spinner("Loading user reviews..."):
            st.session_state.user_reviews = get_user_reviews_from_cache(user_id)
        
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = get_user_genre_counts_and_pcts(st.session_state.user_reviews, 
                                                                                                                    genre_labels)

        user_fiction_values_dict = retrieve_genre_values_from_df(st.session_state.user_genre_stats_main, fiction_genres)
        user_nonfiction_values_dict = retrieve_genre_values_from_df(st.session_state.user_genre_stats_main, nonfiction_genres)

        set_sliders(user_fiction_values_dict)
        set_sliders(user_nonfiction_values_dict)

with col5:
    # MOVE LOAD USER REVIEWS HERE
    # SIDE BAR SHOULD BE PICK YOUR PERSONALITY

    # --- Streamlit UI ---
    st.sidebar.title("🔍 Load User Reviews")
    user_id = st.sidebar.text_input("Enter User ID")

    def get_user_reviews_from_cache(user_id):
        cached = cache.get(user_id)
        if cached is not None:
            # st.info(f"Returning cached data for user: {user_id}")
            return cached
        
        # st.warning(f"Fetching fresh data for user: {user_id}")
        user_reviews_dicts = get_reviews_from_user_url(user_id)
        user_reviews = pd.DataFrame(user_reviews_dicts)
        cache.set(user_id, user_reviews)
        return user_reviews

    if "data_dict" not in st.session_state:
        start_time = time.time()    
        st.session_state.data_dict = interface_loader(file_paths)
        end_time = time.time()
        st.write(f"Loaded dfs in {  (end_time-start_time)  } seconds")

    data_dict = st.session_state.data_dict

    all_books = data_dict["all_books_final.parquet"]
    all_books_ratings = all_books[['title', 'rating', 'num_ratings']]
    books_author_date = all_books[['title', 'author', 'publish_date']]
    books_author_date = books_author_date.set_index('title')

    users_data = data_dict["users_data.parquet"]
    genre_labels = data_dict["genre_labels.parquet"]
    all_labeled_reviews = data_dict["all_labeled_reviews.parquet"]
    compact_user_genre_pct = data_dict["compact_user_genre_pct.parquet"]
    main_user_item_matrix = data_dict["main_user_item_matrix.parquet"]

    if "user_genre_counts" not in st.session_state:
        st.session_state.user_genre_counts, st.session_state.user_genre_pct = get_user_genre_counts(data_dict["all_labeled_reviews.parquet"])

    user_genre_counts, user_genre_pct = st.session_state.user_genre_counts, st.session_state.user_genre_pct

    # --- Persist cache between reruns ---
    if "cache" not in st.session_state:
        st.session_state.cache = UserReviewCache(maxsize=10)

    cache = st.session_state.cache

    if 'user_reviews' not in st.session_state:
        st.session_state.user_reviews = pd.DataFrame()

    if "user_genre_stats_main" not in st.session_state:
        # SUPER IMPORTANT: WILL BE CONNECTED TO SLIDERS!!! 
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = pd.DataFrame(), pd.DataFrame()

    load_user_kwargs = {
        "user_id": user_id, 
        "genre_labels": genre_labels,
        "fiction_genres": fiction_genres, 
        "nonfiction_genres": nonfiction_genres
    }

    load_button = st.sidebar.button("Load", on_click = load_user_reviews_button, kwargs = load_user_kwargs)

    st.title("📚 Book recs for you")
    recommend_button = st.button("Get recommendations")
    hide_read = st.checkbox("Hide Books Already Read", value=True, key="hide_read")

    # Toggle switch for novelty mode
    on = st.toggle("Mode", key='novelty_mode')

    # Mapping from mode name to novelty factor
    mode_to_novelty = {
        "Classic": 0.1,
        "Surprise Me": 1
    }

    if on:
        mode = "Surprise Me"
    else:
        mode = "Classic"

    novelty_factor = mode_to_novelty[mode]

    # Show confirmation
    st.write(f"Mode: **{mode}**")

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None

    if recommend_button:
        if st.session_state.user_reviews.empty:
            st.error("No user reviews loaded. Please load reviews first.")
        else:
            
            # Load st.session_state.user_genre_stats_main first
            st.session_state.user_genre_stats_main = adjust_genre_values(st.session_state.user_genre_stats_main,
                                                                         fiction_genres + nonfiction_genres,
                                                                         fiction_values + nonfiction_values
                                                                         )



            st.session_state.recommendations, neighbors = recommend_books_by_custom_genre_pct(st.session_state.user_genre_stats_main, novelty_factor = novelty_factor,
                                                                    rating_emphasis = 8, user_reviews = st.session_state.user_reviews,
                                                                    user_genre_counts = user_genre_counts, other_users_genre_pct = compact_user_genre_pct,
                                                                    user_item_matrix = main_user_item_matrix, users_data = users_data, 
                                                                    book_ratings = all_books_ratings, metadata = books_author_date, hide_read=st.session_state.hide_read)

            

    # Display (persistent across slider moves)
    if st.session_state.recommendations is not None:
        # st.subheader("Top recommendations for you")
        result= st.session_state.recommendations.head(50)
        st.dataframe(result.head(50), width=1200)
        st.write(st.session_state.user_genre_stats_main)




"""
To fix:

- Think about UI experience (personalities, top users, format heading) (in sidebar)
- take away score column at the very end
- Examine why some user_ids won't load

- Set recs df to width 5 but allow scroll up to 10

- How to normalize values from toggle to final vector (if needed...set realistic limits)
- Set to max 50! (If loaded data is >50...cap at 50.)
- Make sure recs only show those with score > 50


- Explore personality prototypes:
- 68699718-rain


- Connect to database (goodreads users who have used my app!)

"""