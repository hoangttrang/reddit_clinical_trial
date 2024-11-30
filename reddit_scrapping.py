import json
import praw
import os
import time
import re
from openai import OpenAI
from scipy.spatial.distance import cosine
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()
 
# class to scrap reddit data with weighted similarity score 
class RedditScraperSIM:
    """
    Initialize the RedditScraperSIM class with API credentials and configurations.
        
        Input:
        - client_id (str): Reddit app client ID
        - client_secret (str): Reddit app client secret
        - user_agent (str): Custom user agent string
        - subreddits (list): List of subreddit names to scrape
        - defined_query (str): Query string to generate an embedding for weighted similarity
        - api_call_limit (int): Maximum API calls allowed before pausing (default: 100)
        - model (str): OpenAI embedding model to use (default: "text-embedding-3-small")
        
        Output:
        - Return post data with weighted similarity score. The weighted similarity score is calculated based on how does the post 
        text is similar to the defined query. The score is penalized for irrelevant keywords and boosted for relevant keywords.
    """
    def __init__(self, client_id, client_secret, user_agent, subreddits, defined_query, api_call_limit=100, model = "text-embedding-3-small"):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.subreddits = subreddits # list of subreddits to scrape
        self.api_call_limit = api_call_limit # the Reddit API call limit before pausing
        self.posts = []  # List to store all posts
        self.latest_id = None # Create ID for each post 
        # openai init for weighted similarity score
        self.model= model 
        self.client = OpenAI()
        self.query_embedding = self._get_embedding(defined_query)
        self.penalty_keywords = ["career", "hiring", "job", "employment", "work experience", "cv", "resume", "intern","internship", "cro", "cra" ]
        self.boost_keywords = ["patient", "participation", "recruitment", "trial", "treatment"]

# Apply embedding for the text
    def _get_embedding(self,text):
        response = self.client.embeddings.create(input=[text], model=self.model).data[0].embedding
        return response

    # cosine similarity 
    def _cosine_similarity(self, vec1, vec2):
        return 1 - cosine(vec1, vec2)
    
    def _calculate_weighted_similarity(self, post_text,):
        # remove a, an, the from text
        post_text = post_text.replace("a ", "").replace("an ", "").replace("the ", "")
        # regex to remove link
        post_text = re.sub(r'http\S+', '', post_text)
        # Compute cosine similarity
        try:
            post_embedding = self._get_embedding(post_text)
            similarity = self._cosine_similarity(post_embedding, self.query_embedding)
        except Exception as e: 
            print(e)
            print(post_text)
        
        # Penalty for irrelevant keywords
        penalty = sum(post_text.lower().count(keyword) for keyword in self.penalty_keywords) * 0.2
        boost = sum(post_text.lower().count(keyword) for keyword in self.boost_keywords) * 0.1
    
    # return the weighted similarity
        return similarity - penalty + boost

    # Extract posts from a given subreddit
    def extract_posts(self, subreddit_name):
        """Extract all posts from a SubReddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = {}
        call_count = 0  # Track the number of API calls
        print("Extracting start...")
        # Iterate through all posts using subreddit.new()
        for post in subreddit.new(limit=None):  # Fetch posts from newest to oldest
            # Load all comments
            post.comments.replace_more(limit=None)
            comments = [
                {
                    "author": comment.author.name if comment.author else "N/A",
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc,
                }
                for comment in post.comments.list()
            ]
            # Calculate the weighted score for each post 
            weighted_similarity = self._calculate_weighted_similarity(post.title + " " + post.selftext)
            
            # Add post with key as post ID
            posts[post.id] = {
                "title": post.title,
                "selftext": post.selftext,
                "author": post.author.name if post.author else "N/A",
                "weighted_similarity": weighted_similarity,
                "upvote_ratio": post.upvote_ratio,
                "created_utc": post.created_utc,
                "created_date": datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                "score": post.score,
                "url": post.url,
                "num_comments": post.num_comments,
                "subreddit": subreddit_name,
                "comments": comments,  # Add comments to the post
            }

            call_count += 1

            # Rate limiting: pause for 1 minute after reaching the API call limit
            if call_count >= self.api_call_limit:
                print(f"Reached {self.api_call_limit} API calls. Pausing for 1 minute...")
                time.sleep(65)  # Wait for 60s + 5s buffer for rate limiting
                call_count = 0  # Reset the call count

        return posts
    # main method to scrape the data
    def scrape(self):
        all_posts = {}
        
        print(f"Scrapping data: {self.subreddits} subreddits...")
        for subreddit in self.subreddits:
            print(f"Fetching posts from r/{subreddit}...")
            subreddit_posts = self.extract_posts(subreddit)
            all_posts.update(subreddit_posts)

        self.posts = all_posts
        return self.posts
    
    def save_data(self, type_of_data):
        output_file = f"{os.getcwd()}/data/{type_of_data}_data.json"
        print(f"Saving {type_of_data} data to {output_file}...")
        # if output file exists, clear the file
        if os.path.exists(output_file):
            open(output_file, "w").close()
        # Save data to JSON file
       
        if self.posts:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.posts, f, ensure_ascii=False, indent=4)
           
    
if __name__ == "__main__":
    client_id = os.environ["REDDIT_CLIENT_ID"]  # Replace with your Reddit app client ID
    client_secret = os.environ["REDDIT_CLIENT_SECRET"] # Replace with your Reddit app client secret
    user_agent = os.environ["REDDIT_USER_AGENT"]  # Replace with your custom user agent

    # Initialize the Reddit API client
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    
    query = """
    I am looking for personal experiences in clinical trials or interest in joining one.
    I am interested in learning more about the process of clinical trials and how they work, how to find and participate in clinical trials.
    medicine, research, study, trials, drug, treatment, experimental, patient, clinical, health, participation, patient recruitment
    Looking for patient recruitment
    """

    scraper = RedditScraperSIM(
        client_id= client_id , # reddit app client id
        client_secret=client_secret,  # reddit app client secret
        user_agent=user_agent, # Replace with your custom user agent
        subreddits=["clinicalresearch","clinicaltrials"],#
        defined_query = query, 
        api_call_limit=100  # API call limit before pausing
    )
    post_data = scraper.scrape()
    # save post data
    scraper.save_data("post")
