import praw
import time

# Initialize the Reddit instance
reddit = praw.Reddit(
    client_id="your-client-id",          # The string under 'personal use script'
    client_secret="your-client-secret",  # The string labeled 'secret'
    user_agent="script:MyRedditBot:v1.0 (by /u/YourUsername)",  # Format: script:BotName:Version (by /u/Username)
    username="darkblue4567",     
    password="reddit789"      
)

def create_post(subreddit_name, title, content):
    """Create a new post in a subreddit"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        post = subreddit.submit(title=title, selftext=content)
        print(f"Post created successfully: {post.url}")
        return post
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return None

def add_comment(post_url, comment_text):
    """Add a comment to a specific post"""
    try:
        submission = reddit.submission(url=post_url)
        comment = submission.reply(comment_text)
        print(f"Comment added successfully: {comment.permalink}")
        return comment
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        return None

def like_post(post_url):
    """Upvote a post"""
    try:
        submission = reddit.submission(url=post_url)
        submission.upvote()
        print("Post upvoted successfully")
    except Exception as e:
        print(f"Error upvoting post: {str(e)}")

def send_dm(username, message):
    """Send a direct message to a user"""
    try:
        reddit.redditor(username).message(
            subject="Hello!",
            message=message
        )
        print(f"Message sent successfully to {username}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def monitor_subreddit(subreddit_name, keywords=None, reply_text=None):
    """Monitor a subreddit for new posts and optionally reply to them"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Monitoring r/{subreddit_name} for new posts...")
        
        for submission in subreddit.stream.submissions():
            if keywords is None or any(keyword.lower() in submission.title.lower() for keyword in keywords):
                print(f"New post found: {submission.title}")
                
                if reply_text:
                    submission.reply(reply_text)
                    print("Reply posted")
                
                # Wait to avoid rate limiting
                time.sleep(2)
    except Exception as e:
        print(f"Error monitoring subreddit: {str(e)}")

def get_user_info(username):
    """Get information about a Reddit user"""
    try:
        user = reddit.redditor(username)
        return {
            "name": user.name,
            "karma": user.link_karma + user.comment_karma,
            "created_utc": user.created_utc,
            "is_mod": user.is_mod,
        }
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return None

# Let's add a verification test
def verify_authentication():
    """Verify that the authentication works"""
    try:
        print(f"Authenticated as: {reddit.user.me()}")
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    try:
        # First verify authentication
        if not verify_authentication():
            print("Please check your credentials and try again.")
            exit()

        # Test with a simple read operation first
        print("\nTesting read access...")
        for submission in reddit.subreddit("test").hot(limit=1):
            print(f"Successfully read post: {submission.title}")

        # Now try to create a post
        print("\nTesting post creation...")
        post = create_post(
            "test",  # Using r/test subreddit which is meant for testing
            "Test Post from Python Bot",
            "This is a test post to verify bot functionality."
        )

        if post:
            print("\nTesting comment functionality...")
            # Wait a few seconds before commenting
            time.sleep(2)
            add_comment(post.url, "This is a test comment!")
            
            print("\nTesting upvote functionality...")
            # Wait a few seconds before upvoting
            time.sleep(2)
            like_post(post.url)

        print("\nAll tests completed!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
