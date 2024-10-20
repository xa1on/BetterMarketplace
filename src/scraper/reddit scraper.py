"""from YARS.src.yars.utils import display_results, download_image
from YARS.src.yars.yars import YARS

miner = YARS()

while True:
    subreddit_posts = miner.fetch_subreddit_posts("mechmarket", limit=50, category="new")
    display_results(subreddit_posts, "mechmarket SUBREDDIT New Posts")"""

from YARS.src.yars.utils import display_results, download_image
from YARS.src.yars.yars import YARS
import time

# Initialize the YARS miner
miner = YARS()

# Set to store the IDs of scraped posts
scraped_post_ids = set()

last_scraped_timestamp = None

total_limit = 1000
batch_size = 50

def fetch_and_display_batch(start_index):
    subreddit_posts = miner.fetch_subreddit_posts("mechmarket", limit=batch_size, category="new")

    if not subreddit_posts:
        print("No new posts found.")
        return False

    for post in subreddit_posts:
        post_id = post.get('post_id')
        post_timestamp = post.get('created_utc')

        if post_id is None or post_timestamp is None:
            print("Post ID or timestamp not found. Skipping post.")
            continue

        if post_id in scraped_post_ids:
            print("Reached a previously scraped post. Stopping...")
            return False

        scraped_post_ids.add(post_id)

        last_scraped_timestamp = post_timestamp

    display_results(subreddit_posts, f"mechmarket SUBREDDIT New Posts (Batch {start_index + 1})")

    return True

start_index = 0
while start_index * batch_size < total_limit:
    if not fetch_and_display_batch(start_index):
        break
    user_input = input("Do you want to search for more posts? (yes/no): ").strip().lower()

    if user_input != "yes":
        print("Stopping the search. Goodbye!")
        break

    start_index += 1
    print(f"Fetching batch {start_index + 1}...")

    time.sleep(2)