from get_user_reviews import *
from genre_book_recommender import *
from collections import OrderedDict

class SimpleLRUCache:
    def __init__(self, maxsize=10):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)  
            return self.cache[key]
        return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)  
        self.cache[key] = value

# Step 2: Initialize the cache
cache = SimpleLRUCache(maxsize=10)

def get_user_reviews_from_cache(user_id):
    """ Retrieves review info while handling caching"""
    
    cached = cache.get(user_id)
    if cached is not None:
        print(f"Returning {user_id} reviews from cache: {user_id}")
        return cached
    
    print(f"Fetching {user_id} data from web")
    user_reviews = get_reviews_from_user_url(user_id)
    cache.set(user_id, user_reviews)
    
    return user_reviews


if __name__ == "__main__":
    user1 = '155041466-jamie-ren'
    
    # Load user reviews from the web
    user_reviews_dicts = get_user_reviews_from_cache(user1)
    user_reviews = pd.DataFrame(user_reviews_dicts)
    
    print(user_reviews)
    # Generate recs from reviews
    recommended_books, neighbors = recommend_books_by_user_genre_reading_pattern_similarity(user_reviews, novelty_factor = 10)
    
    print("Book recs")
    print(recommended_books)
    print()

    print("Neighboring users")
    print(neighbors)
    


# if __name__ == "__main__":
#     user1 = '155041466-jamie-ren'
#     user3 = "19600954-manisha-patro"
#     user2 = '47437118-namrata-sampat'

#     # First time: real request
#     html1 = get_user_reviews_from_cache(user1)
#     print(f"Length 1: {len(html1)}")

#     # Cached
#     html2 = get_user_reviews_from_cache(user1)
#     print(f"Length 1: {len(html2)}")

#     # Another URL
#     html3 = get_user_reviews_from_cache(user2)
#     print(f"Length 2: {len(html3)}")

#     # Again the first one
#     html4 = get_user_reviews_from_cache(user3)
#     print(f"Length 3: {len(html4)}")

#     # print(cache.get(user1))
#     print("Items in cache", len(cache.cache))



