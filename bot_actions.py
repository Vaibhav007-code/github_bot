import praw
import time

# Use the same successful configuration
reddit = praw.Reddit(
    client_id="eMwI_lv2OXe76DTUMNCMqA",          
    client_secret="yLEV02ts7O0jA9kv3WzfRkC_aFZ4mw",      
    user_agent="script:blueBot:v1.0 (by /u/darkblue4567)",  
    username="darkblue4567",     
    password="reddit789"      
)

def make_post(subreddit_name="test", title="", content=""):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        post = subreddit.submit(
            title=title or "Test Post from blueBot",
            selftext=content or "This is a test post created by my Python bot!"
        )
        print(f"Post created successfully! URL: {post.url}")
        return post
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return None

def add_comment(post, comment_text=""):
    try:
        comment = post.reply(comment_text or "This is a test comment from blueBot!")
        print(f"Comment added successfully! URL: {comment.permalink}")
        return comment
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        return None

def send_message(username, subject, message):
    try:
        reddit.redditor(username).message(subject, message)
        print(f"Message sent successfully to {username}")
        return True
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

def monitor_subreddit(subreddit_name, keyword=None, duration=60):
    """Monitor a subreddit for new posts containing specific keywords"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Monitoring r/{subreddit_name} for {duration} seconds...")
        
        end_time = time.time() + duration
        for submission in subreddit.stream.submissions():
            if time.time() > end_time:
                break
                
            if keyword is None or keyword.lower() in submission.title.lower():
                print(f"\nFound matching post: {submission.title}")
                print(f"URL: {submission.url}")
                
                # Auto-upvote matching posts
                submission.upvote()
                print("Post upvoted!")
                
                # Add a comment
                add_comment(submission, f"Great post about {keyword}!")
                
            time.sleep(2)  # Avoid rate limiting
            
    except Exception as e:
        print(f"Error monitoring subreddit: {str(e)}")

if __name__ == "__main__":
    print("Starting enhanced bot actions...")
    
    # 1. Create a custom post
    post = make_post(
        subreddit_name="test",
        title="Advanced Bot Test Post",
        content="Testing advanced features of our Reddit bot!"
    )
    
    if post:
        # 2. Add a custom comment
        time.sleep(2)
        comment = add_comment(post, "This is a custom comment with more details!")
        
        # 3. Send a DM (replace with target username)
        time.sleep(2)
        send_message("darkblue4567", "Bot Test", "Hello! This is a test message from your bot.")
        
        # 4. Monitor subreddit for specific keywords
        print("\nStarting subreddit monitoring...")
        monitor_subreddit("test", keyword="python", duration=30)  # Monitor for 30 seconds
    
    print("\nAll enhanced actions completed!") 