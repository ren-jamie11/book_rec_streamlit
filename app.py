import streamlit as st

from static import *
from get_user_reviews import *
from main_genre_book_recommender_sparse import *
from user_review_cache_class import UserReviewCache

from scipy.sparse import load_npz

st.set_page_config(page_title="Pocket Library", layout="wide")
fiction_sliders, col2, nonfiction_sliders, col4, col_recommend = st.columns([2, .5, 2, .5, 6]) 

# ------ Load parquet files! --------
file_paths = ["data/all_books_final.parquet",
              "data/users_data.parquet",
              "data/genre_labels.parquet",
              "data/all_labeled_reviews.parquet",
              "data/compact_user_genre_pct.parquet"]

@st.cache_data
def read_parquet(file_path):
    df = pd.read_parquet(file_path)
    return df

all_books = read_parquet("data/all_books_final.parquet")
all_books_ratings = all_books[['title', 'rating', 'num_ratings']]
books_author_date = all_books[['title', 'author', 'publish_date']]
books_author_date = books_author_date.set_index('title')

users_data = read_parquet("data/users_data.parquet")
genre_labels = read_parquet("data/genre_labels.parquet")
all_labeled_reviews = read_parquet("data/all_labeled_reviews.parquet")
compact_user_genre_pct = read_parquet("data/compact_user_genre_pct.parquet")
# ------ Finished loading parquet files --------

st.sidebar.write("")
st.sidebar.title("🔍 Load Reviews")
user_id = st.sidebar.text_input("GoodReads User ID", key = 'user_id_chatbox')

def genre_subtext(title, spaces = 2):
    """ Basic formatting/text function
        (not important)
    """
    for _ in range(spaces):
        st.write("")
    st.write(f"**{title}**")

def set_sliders(genre_values_dict: dict):
    """
    Set slider values (provided by dict)
    """
    for k,v in genre_values_dict.items():
        st.session_state[k] = v
    return

def reset_sliders(default=0):
    for g in fiction_genres:
        st.session_state[g] = default
    for g in nonfiction_genres:
        st.session_state[g] = default
    return

def check_if_sliders_zero():
    for g in fiction_genres + nonfiction_genres:
        if st.session_state[g] != 0:
            return False
    return True

# Slider values are from 0 to max_genre_pct
max_genre_pct = 50

with fiction_sliders:
    st.write("")
    st.subheader("📚 Your personality")
    st.write("")
    
    st.button(
        "Reset",
        on_click=reset_sliders,
        key="reset_sliders"
    )
    
    genre_subtext("Fiction", spaces = 1)

    # Fiction 
    classics = st.slider("Classics", 0, max_genre_pct, key="Classics")
    contemporary = st.slider("Contemporary", 0, max_genre_pct, key="Contemporary")
    fantasy = st.slider("Fantasy", 0, max_genre_pct, key="Fantasy")
    historical_fiction = st.slider("Historical fiction", 0, max_genre_pct, key="Historical Fiction")
    horror = st.slider("Horror", 0, max_genre_pct, key="Horror")
    mystery = st.slider("Mystery", 0, max_genre_pct, key="Mystery")
    romance = st.slider("Romance", 0, max_genre_pct, key="Romance")
    science_fiction = st.slider("Science fiction", 0, max_genre_pct, key="Science Fiction")
    young_adult = st.slider("Young adult", 0, max_genre_pct, key="Young Adult")

with nonfiction_sliders:
    st.subheader("")
    genre_subtext("Nonfiction", spaces = 6)

    # Nonfiction 
    art = st.slider("Art", 0, max_genre_pct, key="Art")
    biography = st.slider("Biography", 0, max_genre_pct, key="Biography")
    business = st.slider("Business", 0, max_genre_pct, key="Business")
    history = st.slider("History", 0, max_genre_pct, key="History")
    music = st.slider("Music", 0, max_genre_pct, key="Music")
    philosophy = st.slider("Philosophy", 0, max_genre_pct, key="Philosophy")
    psychology = st.slider("Psychology", 0, max_genre_pct, key="Psychology")
    science = st.slider("Science", 0, max_genre_pct, key="Science")
    self_help = st.slider("Self help", 0, max_genre_pct, key="Self Help")

fiction_values = [st.session_state[g]/100 for g in fiction_genres]
nonfiction_values = [st.session_state[g]/100 for g in nonfiction_genres]

def load_user_reviews_button(genre_labels: pd.DataFrame, 
                             fiction_genres: List[str], nonfiction_genres: List[str]):
    """
    - Loads user reviews from GoodReads website
    - Extracts 18 genre info from user
    - Set slider values to extracted values
    - Ready to be used in recommender engine

    Args:
        - user_id: The user's id
        - genre_labels: Enriches books with correct genre labels
        - fiction_genres: List[str] of fiction genres
        - nonfiction_genres: List[str] of nonfiction genres
    """
    st.session_state.sidebar_acknowledged = True
    # get what's in the chatbox
    user_id_entry = st.session_state['user_id_chatbox']
    if user_id_entry.strip() == "":
            st.error("Please enter a valid user ID.")
    else:
        # refresh recs and neighbors (before user presses 'recommend' button)
        st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)
        st.session_state.neighbors = pd.DataFrame(columns = neighbor_df_cols)

        with st.spinner("Loading user reviews..."):
            st.session_state.user_reviews = get_user_reviews_from_cache(user_id_entry)
        
        # get genre info from user's reviews
        temp_genre_counts, temp_genre_pcts = get_user_genre_counts_and_pcts(st.session_state.user_reviews, 
                                                                            genre_labels, max_value= max_genre_pct/100)

        # check if loaded successfully
        if len(temp_genre_pcts) > 0:
            st.session_state.load_user_status = True
        else:
            st.session_state.load_user_status = False

        # set sliders to user's genre values
        user_fiction_values_dict = retrieve_genre_values_from_df(temp_genre_pcts, fiction_genres)
        user_nonfiction_values_dict = retrieve_genre_values_from_df(temp_genre_pcts, nonfiction_genres)

        set_sliders(user_fiction_values_dict)
        set_sliders(user_nonfiction_values_dict)

@st.cache_data
def load_sparse_user_item_matrix(filepath = "data/user_item_sparse.npz"):
    loaded_sparse = load_npz(filepath)
    return loaded_sparse

# Sparse user item matrix
sparse_user_item_matrix = load_sparse_user_item_matrix()

with col_recommend:

    # --- Persist cache between reruns ---
    if "cache" not in st.session_state:
        st.session_state.cache = UserReviewCache(maxsize=5)

    cache = st.session_state.cache
    
    def get_user_reviews_from_cache(user_id):
        """
        Load user's review data from GoodReads url
        Stores in cache (for easier repeat retrieval)
        """
        cached = cache.get(user_id)
        if cached is not None:
            return cached
        
        user_reviews_dicts = get_reviews_from_user_url(user_id)
        user_reviews = pd.DataFrame(user_reviews_dicts)
        cache.set(user_id, user_reviews)
        return user_reviews

    # Takes up a lot of RAM!!
    if "user_genre_counts" not in st.session_state:
        st.session_state.user_genre_counts, st.session_state.user_genre_pct = get_user_genre_counts(all_labeled_reviews)

    user_genre_counts, user_genre_pct = st.session_state.user_genre_counts, st.session_state.user_genre_pct

    if 'user_reviews' not in st.session_state:
        st.session_state.user_reviews = pd.DataFrame()

    # Genre info (what recommender uses as primary input)
    if "user_genre_stats_main" not in st.session_state:
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = pd.DataFrame, pd.read_parquet("data/default_genre_when_no_load.parquet")

    if "neighbors" not in st.session_state:
        st.session_state.neighbors = pd.DataFrame()

    load_user_kwargs = {
        "genre_labels": genre_labels,
        "fiction_genres": fiction_genres, 
        "nonfiction_genres": nonfiction_genres
    }

    load_button = st.sidebar.button("Load", on_click = load_user_reviews_button, kwargs = load_user_kwargs)

    st.sidebar.caption("""Use id from your ratings page (e.g. 155041466)
                       www.goodreads.com/review/list/155041466?""")

    if "load_user_status" not in st.session_state:
        st.session_state.load_user_status = True

    if not st.session_state.load_user_status:
        # Restore to default values if can't load user data
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = pd.DataFrame, pd.read_parquet("data/default_genre_when_no_load.parquet")
        st.sidebar.warning("Could not retrieve this user's data")

    st.sidebar.divider()
    st.sidebar.subheader("Reader personality")
    st.sidebar.caption(
        "If you don't have a GoodReads ID, feel free to toggle the sliders "
        "or try out these personalities!"
    )

    selected_profile = st.sidebar.selectbox(
    "Choose a reader personality",
    list(profiles.keys())
)

    # Personality choices
    persons, captions = st.sidebar.columns([1,2])

    with persons:
        st.image(profile_images[selected_profile], width=100)

    with captions:
        st.write(f"**{selected_profile}**")
        st.caption(profiles[selected_profile])

    # See static.py for preloaded personality dicts
    load_person_button = st.sidebar.button(
            label="Try me",
            on_click=set_sliders, 
            kwargs={"genre_values_dict": profile_dicts[selected_profile]}
        )
    st.sidebar.divider()

    st.title("📚 Your books")
    st.write("")
    st.write("**Recommendations**")
    mode = st.selectbox("Mode", ["Classic", "Surprise Me"])
    container1, container2 = st.columns([3, 1])
    with container1:
        recommend_button = st.button("Get recommendations")

    with container2:
        hide_read = st.checkbox("Hide Books Already Read", value=True, key="hide_read")

    def acknowledge_sidebar():
        st.session_state.sidebar_acknowledged = True

    if "sidebar_acknowledged" not in st.session_state:
        st.session_state.sidebar_acknowledged = False

    if not st.session_state.sidebar_acknowledged:
        st.write("")
        st.write("")
        st.markdown(
            '<span style="color: navy; font-weight: bold;">'
            'Toggle sliders to get recs, '
            'or open sidebar (top left) to try out personalities!'
            '</span>',
            unsafe_allow_html=True
        )

        st.markdown('<span style="color: navy;">Zoom out (ctrl + "-") to 75% for best experience </span>', 
                    unsafe_allow_html=True)
        st.button("Got it!", on_click=acknowledge_sidebar)
        
    # Mapping from mode name to novelty factor
    mode_to_novelty = {
        "Classic": 0.1,
        "Surprise Me": 1
    }
    novelty_factor = mode_to_novelty[mode]

    st.write("")

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None

    if recommend_button:
        # Maps slider values to genre vector
        st.session_state.user_genre_stats_main = adjust_genre_values(st.session_state.user_genre_stats_main,
                                                                        fiction_genres + nonfiction_genres,
                                                                        fiction_values + nonfiction_values
                                                                        )
 
        # Gets recommendations!!
        st.session_state.recommendations, st.session_state.neighbors = recommend_books_by_custom_genre_pct(st.session_state.user_genre_stats_main, novelty_factor = novelty_factor,
                                                                rating_emphasis = 8, user_reviews = st.session_state.user_reviews,
                                                                user_genre_counts = user_genre_counts, other_users_genre_pct = compact_user_genre_pct,
                                                                sparse_user_item_matrix = sparse_user_item_matrix, users_data = users_data, 
                                                                book_ratings = all_books_ratings, metadata = books_author_date, hide_read=st.session_state.hide_read)

            
    # Display
    if st.session_state.recommendations is not None:
        result= st.session_state.recommendations.head(50)
        st.dataframe(result.head(10), height = 210)

        if check_if_sliders_zero():
            st.warning("Kind reminder to toggle genres before loading recommendations")

        neighbor_users, neighbor_books = st.columns([2.5, 1])
        with neighbor_users:
            st.write("")
            st.write("**Neighbor users**")
            st.caption(""" Recommendations are based on books highly rated by top 100 reputable GoodReads users 
                           whose reading patterns most closely match the genres you provided (on the left) """)
            st.dataframe(st.session_state.neighbors, height = 210)
            st.divider()
            st.write("*Definitions*")
            st.caption("- 'rating': Average rating given by neighbor users (more relevant/reliable than all users)")
            st.caption("- 'count': represents how many neighbor users have rated the book (out of 100)")
            st.caption("- 'novelty': Inversely related to number of people who have read this book")
            

how_it_works, _, data_description = st.columns([4.8, 0.65, 6.5]) 

with how_it_works:
    st.write("")
    st.write("")
    st.write("#### About this app")
    st.write(""" Get instantaneous high-quality book recommendations based on your unique personality!"""
             """ Recommendations are sourced from real-life Goodreads community members whose reading behaviors  """
             """ statistically match yours based on the genres you enjoy reading. """)
    
    st.divider()
    
    st.write(""" **Relevant**: Recs come from those whose reading profiles are just like yours""")
    st.write(""" **Reliable**: Recs are based on the behavior of highly active and informed readers""")
    st.write(""" **Transparent**: You know exactly who/where your recommendations are coming from""")

with data_description:
    st.write("")
    st.write("")
    st.write("")
    st.write("""*Data based on*""")
    st.caption(""" - 16,000+ books """)
    st.caption(""" - 9,500+ user profiles """)
    st.caption(""" - 475,000+ ratings""")