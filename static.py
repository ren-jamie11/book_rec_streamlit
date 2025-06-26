import pickle

headers_list = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
    },
]

with open("data/book_titles.pkl", "rb") as f:
    book_list = pickle.load(f)

with open("data/user_ids.pkl", "rb") as f:
    user_ids = pickle.load(f)

genres = ['Art',
 'Biography',
 'Business',
 'Chick Lit',
 "Children's",
 'Christian',
 'Classics',
 'Comics',
 'Contemporary',
 'Cookbooks',
 'Crime',
 'Ebooks',
 'Fantasy',
 'Fiction',
 'Gay and Lesbian',
 'Graphic Novels',
 'Historical Fiction',
 'History',
 'Horror',
 'Humor and Comedy',
 'Manga',
 'Memoir',
 'Music',
 'Mystery',
 'Nonfiction',
 'Paranormal',
 'Philosophy',
 'Poetry',
 'Psychology',
 'Religion',
 'Romance',
 'Science',
 'Science Fiction',
 'Self Help',
 'Suspense',
 'Spirituality',
 'Sports',
 'Thriller',
 'Travel',
 'Young Adult']

fiction_genres = [
 'Classics',
 'Contemporary',
 'Fantasy',
 'Historical Fiction',
 'Horror',
 'Mystery',
 'Romance',
 'Science Fiction',
 'Young Adult']

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

lex_genre_dict = {'Classics': 25, 
 'Contemporary': 7, 
 'Fantasy': 17, 
 'Historical Fiction': 7, 
 'Horror': 2, 
 'Mystery': 2, 
 'Romance': 7, 
 'Science Fiction': 15, 
 'Young Adult': 5,
 'Art': 2, 
 'Biography': 12, 
 'Business': 23, 
 'History': 12, 
 'Music': 0, 
 'Philosophy': 38, 
 'Psychology': 35, 
 'Science': 2, 
 'Self Help': 35}

suki_dict ={
"Classics":6,
"Contemporary":50,
"Fantasy":34,
"Historical Fiction":20,
"Horror":6,
"Mystery":20,
"Romance":50,
"Science Fiction":2,
"Young Adult":45,
"Art":0,
"Biography":0,
"Business":0,
"History":0,
"Music":0,
"Philosophy":0,
"Psychology":0,
"Science":0,
"Self Help":0,
}


bobby_dict = {
"Classics":1,
"Contemporary":7,
"Fantasy":4,
"Historical Fiction":6,
"Horror":0,
"Mystery":0,
"Romance":4,
"Science Fiction":3,
"Young Adult":3,
"Art":0,
"Biography":21,
"Business":28,
"History":42,
"Music":0,
"Philosophy":15,
"Psychology":24,
"Science":46,
"Self Help":13
}


beth_harmon_dict = { 
    "Classics": 20,           # She's chess-obsessed and often reads older texts
    "Contemporary": 45,       # Her internal world is very modern/emotional
    "Fantasy": 15,            # The ceiling chessboard is her personal fantasy realm
    "Historical Fiction": 30, # Set in the 60s; period themes matter
    "Horror": 10,             # Her addiction and trauma add a psychological edge
    "Mystery": 40,            # She’s enigmatic and surrounded by personal mystery
    "Romance": 25,            # Romance exists, but it’s complicated and backgrounded
    "Science Fiction": 5,     # Not a strong connection
    "Young Adult": 40,        # Coming-of-age journey with intense self-discovery
    "Art": 10,                # Chess is her art; she’s elegant and expressive
    "Biography": 35,          # She *is* a character you'd read a biography about
    "Business": 5,            # Minimal relevance, but she does think tactically
    "History": 20,            # Contextually relevant, especially Cold War tension
    "Music": 10,              # Music accompanies her internal mood
    "Philosophy": 25,         # She questions identity, purpose, genius
    "Psychology": 45,         # Huge theme: trauma, addiction, orphanhood
    "Science": 5,             # Light relevance, more analytical than scientific
    "Self Help": 10,          # There’s an underlying theme of personal growth
}


profiles = {
    "Lex Fridman: Scientist": "Deeply curious... always asking the big questions in life.",
    "Suki: Avatar": "Cute and fearsome heroine from the Kyoshi island",
    "Bobby Axelrod: Billions": "A ruthlessly calculating Wall Street fund manager",
    "Beth Harmon: Queen's Gambit": "A chess prodigy with a brilliant but troubled mind"
}

# Corresponding image paths (replace with actual paths later)
profile_images = {
    "Lex Fridman: Scientist": "images/lex.png",
    "Suki: Avatar": "images/suki.png",
    "Bobby Axelrod: Billions": "images/bobby.png",
    "Beth Harmon: Queen's Gambit": "images/beth2.png"
}

profile_dicts ={
    "Lex Fridman: Scientist": lex_genre_dict,
    "Suki: Avatar": suki_dict,
    "Bobby Axelrod: Billions": bobby_dict,
    "Beth Harmon: Queen's Gambit": beth_harmon_dict
}

empty_genre_dict = {g:0 for g in fiction_genres + nonfiction_genres}


# https://www.figma.com/design/ZVbuiFyNCDhtM2fq9sC0T1/Untitled?node-id=1001-3&p=f&t=BVHCCbNdfkEDx1vc-0


rec_df_cols = ['title',
 'author',
 'published',
 'score',
 'rating',
 'count',
 'novelty',
 'goodreads rating',
 'ratings']


neighbor_df_cols = ['user_id',
        'name', 
        'genre similarity', 
        'review samples']