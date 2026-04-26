from apify_client import ApifyClient
import pymongo

# 1. Your Credentials
APIFY_TOKEN = "apify_token"
# Replace this with your actual MongoDB connection string!
MONGO_URI = "mongodb://localhost:27017/" 

def fetch_facebook_data():
    if APIFY_TOKEN == "YOUR_API_TOKEN_HERE":
        print("Error: Add your Apify API token!")
        return

    print("Connecting to Apify API for Facebook...")
    client = ApifyClient(APIFY_TOKEN)
    actor_id = "apify/facebook-posts-scraper" 
    
    run_input = {
        "startUrls": [{"url": "https://www.facebook.com/NASA"}],
        "resultsLimit": 50
    }

    print("Scraping... (This might take 1-2 minutes)")
    run = client.actor(actor_id).call(run_input=run_input)
    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

    print("Connecting to MongoDB...")
    try:
        # Connect to MongoDB
        mongo_client = pymongo.MongoClient(MONGO_URI)
        db = mongo_client["social_media_analytics"] # Creates database
        collection = db["posts"]                    # Creates collection
        
        # Clear old data before inserting new data so the dashboard stays fresh
        collection.delete_many({}) 
        
        # Insert the scraped data into the database
        if dataset_items:
            collection.insert_many(dataset_items)
            print(f"Success! Injected {len(dataset_items)} posts into MongoDB.")
        else:
            print("No data found to insert.")
            
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")

if __name__ == "__main__":
    fetch_facebook_data()