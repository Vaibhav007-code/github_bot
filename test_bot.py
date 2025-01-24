import praw
import time

# Configure with your blueBot credentials
reddit = praw.Reddit(
    client_id="eMwI_lv2OXe76DTUMNCMqA",          
    client_secret="yLEV02ts7O0jA9kv3WzfRkC_aFZ4mw",      
    user_agent="script:blueBot:v1.0 (by /u/darkblue4567)",  
    username="darkblue4567",     
    password="reddit789"      
)

def test_authentication():
    print("Testing authentication...")
    try:
        print(f"Authenticated as: {reddit.user.me()}")
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return False

def test_read_access():
    print("\nTesting read access...")
    try:
        for submission in reddit.subreddit("test").hot(limit=1):
            print(f"Successfully read post: {submission.title}")
        return True
    except Exception as e:
        print(f"Read access failed: {str(e)}")
        return False

def test_basic_functionality():
    print("\nRunning basic functionality tests...")
    try:
        # Test subreddit access
        subreddit = reddit.subreddit("test")
        print(f"Accessed subreddit: {subreddit.display_name}")
        
        # Test user info
        username = reddit.user.me().name
        print(f"Got user info for: {username}")
        return True
    except Exception as e:
        print(f"Basic functionality test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Reddit Bot tests...")
    
    # Test authentication first
    if not test_authentication():
        print("Authentication failed. Please check your credentials.")
        exit(1)
        
    # Continue with other tests
    test_read_access()
    test_basic_functionality()
    
    print("\nAll tests completed!") 