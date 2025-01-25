from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedditMobileBot:
    def __init__(self):
        # Appium server settings
        self.appium_server = "http://localhost:4723"
        
        # Device capabilities
        self.capabilities = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "browserName": "Chrome",  # We'll use Chrome browser
            "noReset": True,  # Don't reset app state
            "newCommandTimeout": 3600,
            "chromedriverExecutable": "./chromedriver",  # Will be downloaded automatically
        }
        
        # Reddit credentials
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        
        self.driver = None
        self.wait = None

    def connect_to_device(self):
        """Connect to the mobile device"""
        try:
            print("Connecting to mobile device...")
            self.driver = webdriver.Remote(self.appium_server, self.capabilities)
            self.wait = WebDriverWait(self.driver, 20)
            print("Successfully connected to device")
            return True
        except Exception as e:
            print(f"Error connecting to device: {str(e)}")
            return False

    def login_to_reddit(self):
        """Login to Reddit mobile website"""
        try:
            print("Logging into Reddit...")
            self.driver.get("https://www.reddit.com/login")
            
            # Wait for and fill username
            username_field = self.wait.until(
                EC.presence_of_element_located((MobileBy.NAME, "username"))
            )
            username_field.send_keys(self.username)
            
            # Fill password
            password_field = self.driver.find_element(MobileBy.NAME, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(MobileBy.XPATH, "//button[contains(text(), 'Log In')]")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            print("Successfully logged into Reddit")
            return True
        except Exception as e:
            print(f"Error logging into Reddit: {str(e)}")
            return False

    def create_post(self, subreddit, title, content):
        """Create a new post on Reddit"""
        try:
            print(f"Creating post in r/{subreddit}...")
            self.driver.get(f"https://www.reddit.com/r/{subreddit}/submit")
            
            # Wait for and click post type (text post)
            post_type = self.wait.until(
                EC.presence_of_element_located((MobileBy.XPATH, "//button[contains(text(), 'Post')]"))
            )
            post_type.click()
            
            # Fill title
            title_field = self.wait.until(
                EC.presence_of_element_located((MobileBy.XPATH, "//textarea[@placeholder='Title']"))
            )
            title_field.send_keys(title)
            
            # Fill content
            content_field = self.driver.find_element(MobileBy.XPATH, "//div[@role='textbox']")
            content_field.send_keys(content)
            
            # Click post button
            post_button = self.driver.find_element(MobileBy.XPATH, "//button[contains(text(), 'Post')]")
            post_button.click()
            
            print("Post created successfully")
            return True
        except Exception as e:
            print(f"Error creating post: {str(e)}")
            return False

    def add_comment(self, post_url, comment_text):
        """Add a comment to a post"""
        try:
            print("Adding comment...")
            self.driver.get(post_url)
            
            # Wait for and click comment field
            comment_field = self.wait.until(
                EC.presence_of_element_located((MobileBy.XPATH, "//div[@role='textbox']"))
            )
            comment_field.click()
            comment_field.send_keys(comment_text)
            
            # Click comment button
            comment_button = self.driver.find_element(MobileBy.XPATH, "//button[contains(text(), 'Comment')]")
            comment_button.click()
            
            print("Comment added successfully")
            return True
        except Exception as e:
            print(f"Error adding comment: {str(e)}")
            return False

    def send_message(self, username, subject, message):
        """Send a direct message to a user"""
        try:
            print(f"Sending message to u/{username}...")
            self.driver.get(f"https://www.reddit.com/message/compose/?to={username}")
            
            # Fill subject
            subject_field = self.wait.until(
                EC.presence_of_element_located((MobileBy.NAME, "subject"))
            )
            subject_field.send_keys(subject)
            
            # Fill message
            message_field = self.driver.find_element(MobileBy.NAME, "message")
            message_field.send_keys(message)
            
            # Click send button
            send_button = self.driver.find_element(MobileBy.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            
            print("Message sent successfully")
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

    def close(self):
        """Close the Appium session"""
        if self.driver:
            self.driver.quit()

def main():
    bot = RedditMobileBot()
    
    try:
        # Connect to device
        if not bot.connect_to_device():
            print("Failed to connect to device")
            return
        
        # Login to Reddit
        if not bot.login_to_reddit():
            print("Failed to login to Reddit")
            return
        
        # Example usage
        # Create a post
        bot.create_post(
            "test",
            "Test Post from Mobile Bot",
            "This is a test post created using Appium mobile automation!"
        )
        
        # Add a comment
        bot.add_comment(
            "https://www.reddit.com/r/test/comments/example",
            "This is a test comment from mobile!"
        )
        
        # Send a message
        bot.send_message(
            "example_user",
            "Test Message",
            "This is a test message sent from mobile automation!"
        )
        
    finally:
        bot.close()

if __name__ == "__main__":
    main() 