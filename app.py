from flask import Flask, render_template, request, flash, redirect, url_for
import praw
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Reddit configuration using environment variables
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),          
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),      
    user_agent=os.getenv('REDDIT_USER_AGENT', 'script:RedditBot:v1.0'),  
    username=os.getenv('REDDIT_USERNAME'),     
    password=os.getenv('REDDIT_PASSWORD'),
    check_for_async=False
)

def verify_reddit_auth():
    try:
        # Try to get the authenticated user
        user = reddit.user.me()
        if user is None:
            return False, "Authentication failed. Please check your credentials."
            
        # Get account details
        created_utc = user.created_utc
        account_age_days = (time.time() - created_utc) / (24 * 60 * 60)
        total_karma = user.link_karma + user.comment_karma
        
        warnings = []
        if account_age_days < 3:
            warnings.append(f"Account is new (age: {int(account_age_days)} days). Some actions may be restricted.")
        if total_karma < 1:
            warnings.append(f"Account has low karma (total: {total_karma}). Some actions may be restricted.")
            
        if warnings:
            return True, "Warning: " + " ".join(warnings)
            
        return True, "Authentication successful"
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'invalid_grant' in error_msg:
            return False, "Invalid username or password. Please check your credentials."
        elif 'invalid_client' in error_msg:
            return False, "Invalid client_id or client_secret. Please check your Reddit API credentials."
        elif 'rate' in error_msg:
            return False, "Rate limited by Reddit. Please wait a few minutes and try again."
        else:
            return False, f"Authentication error: {str(e)}"

class Stats:
    def __init__(self):
        self.total_actions = 0
        self.posts = 0
        self.comments = 0
        self.messages = 0
        self.recent_actions = []
        
        # Initialize with some default values since we can't use files on Vercel
        self.initialize_default_stats()
        
    def initialize_default_stats(self):
        """Initialize with default values for serverless environment"""
        self.total_actions = 0
        self.posts = 0
        self.comments = 0
        self.messages = 0
        self.recent_actions = []

    def save_stats(self):
        """In serverless environment, we just keep stats in memory"""
        # Keep only last 20 actions to prevent memory growth
        self.recent_actions = self.recent_actions[:20]
        # No file operations needed

    def load_stats(self):
        """In serverless environment, stats are kept in memory"""
        pass  # No file operations needed

stats = Stats()

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        # Verify Reddit authentication on each request
        auth_success, auth_message = verify_reddit_auth()
        
        # If authentication completely failed, show error page
        if not auth_success:
            return f"""
            <h3>Reddit Authentication Failed</h3>
            <p style="color: red;">{auth_message}</p>
            <p>Please check your Reddit API credentials in the .env file.</p>
            <p>Your current credentials:</p>
            <ul>
                <li>Client ID: {os.getenv('REDDIT_CLIENT_ID')[:5]}...</li>
                <li>Username: {os.getenv('REDDIT_USERNAME')}</li>
                <li>User Agent: {os.getenv('REDDIT_USER_AGENT')}</li>
            </ul>
            <p>Make sure:</p>
            <ol>
                <li>You've created a Reddit App at https://www.reddit.com/prefs/apps</li>
                <li>You're using the correct client_id (the string under your app name)</li>
                <li>You're using the correct client_secret</li>
                <li>Your Reddit account password is correct</li>
                <li>You're not being rate limited</li>
            </ol>
            <p>Need to update your credentials? Edit the .env file with the correct values.</p>
            """

        # If there are warnings (like low karma), show them as a flash message
        if "Warning:" in auth_message:
            flash(auth_message, 'warning')

        if not all([os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET'), 
                    os.getenv('REDDIT_USERNAME'), os.getenv('REDDIT_PASSWORD')]):
            setup_instructions = """
            <h3>Setup Instructions:</h3>
            <ol>
                <li>Create a Reddit account if you don't have one</li>
                <li>Go to https://www.reddit.com/prefs/apps</li>
                <li>Click 'Create App' or 'Create Another App'</li>
                <li>Fill in the details:
                    <ul>
                        <li>Name: YourBotName</li>
                        <li>Type: Script</li>
                        <li>Description: Your bot description</li>
                        <li>About URL: Can be blank</li>
                        <li>Redirect URI: http://localhost:8080</li>
                    </ul>
                </li>
                <li>Create a .env file in the project root with:
                    <pre>
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=script:YourBotName:v1.0
                    </pre>
                </li>
                <li>Restart the application</li>
            </ol>
            """
            return setup_instructions

        if request.method == 'POST':
            try:
                # Get form data safely
                form_data = request.form.to_dict()
                action = form_data.get('action')

                if not action:
                    raise ValueError("No action specified")

                # Validate required fields based on action
                if action == 'post':
                    required_fields = ['subreddit', 'title', 'content']
                elif action == 'comment':
                    required_fields = ['post_url', 'comment_text']
                elif action == 'message':
                    required_fields = ['username', 'subject', 'message']
                elif action == 'monitor':
                    required_fields = ['monitor_subreddit', 'keyword', 'duration']
                else:
                    raise ValueError("Invalid action specified")

                # Check for missing fields
                missing_fields = [field for field in required_fields if not form_data.get(field)]
                if missing_fields:
                    raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

                # Process the action
                if action == 'post':
                    post = make_post(
                        form_data.get('subreddit', 'test'),
                        form_data.get('title'),
                        form_data.get('content')
                    )
                    if post:
                        stats.posts += 1
                        stats.total_actions += 1
                        add_action('post', form_data, 'success')
                        flash(f'Post created successfully! URL: {post.url}', 'success')

                elif action == 'comment':
                    submission = reddit.submission(url=form_data.get('post_url'))
                    comment = add_comment(submission, form_data.get('comment_text'))
                    if comment:
                        stats.comments += 1
                        stats.total_actions += 1
                        add_action('comment', form_data, 'success')
                        flash('Comment added successfully!', 'success')

                elif action == 'message':
                    if send_message(
                        form_data.get('username'),
                        form_data.get('subject'),
                        form_data.get('message')
                    ):
                        stats.messages += 1
                        stats.total_actions += 1
                        add_action('message', form_data, 'success')
                        flash('Message sent successfully!', 'success')

                elif action == 'monitor':
                    duration = int(form_data.get('duration', 30))
                    monitor_subreddit(
                        form_data.get('monitor_subreddit'),
                        form_data.get('keyword'),
                        duration
                    )
                    stats.total_actions += 1
                    add_action('monitor', form_data, 'success')
                    flash('Monitoring completed!', 'success')

            except Exception as e:
                error_message = str(e)
                if 'received 403 HTTP response' in error_message:
                    error_message = "Reddit rejected the request. Please check your credentials and permissions."
                elif 'received 404 HTTP response' in error_message:
                    error_message = "The requested resource was not found. Please check the URL or username."
                elif 'NoneType' in error_message:
                    error_message = "Failed to process the request. Please check your input and try again."
                
                flash(f'Error: {error_message}', 'danger')
                if action:
                    add_action(action, form_data, 'failed')

            return redirect(url_for('index'))
                
        return render_template('index.html', stats=stats)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

def add_action(action_type, data, status):
    timestamp = datetime.now()  # Store as datetime object instead of string
    
    # Create detailed description based on action type
    if action_type == 'post':
        description = f"Posted to r/{data['subreddit']}"
        details = f"Title: {data['title']}\nContent: {data['content']}"
        url = data.get('url', '')
    elif action_type == 'comment':
        description = f"Added a comment"
        details = f"On post: {data['post_url']}\nComment: {data['comment']}"
        url = data['post_url']
    elif action_type == 'message':
        description = f"Sent message to u/{data['username']}"
        details = f"Subject: {data['subject']}\nMessage: {data['message']}"
        url = ''
    elif action_type == 'monitor':
        description = f"Monitored r/{data['subreddit']}"
        details = f"Keyword: '{data['keyword']}'\nDuration: {data['duration']} seconds"
        url = ''
    else:
        description = "Unknown action"
        details = str(data)
        url = ''

    stats.recent_actions.insert(0, {
        'action_type': action_type,
        'description': description,
        'details': details,
        'url': url,
        'status': status,
        'timestamp': timestamp
    })
    
    # Keep only last 20 actions
    stats.recent_actions = stats.recent_actions[:20]

def make_post(subreddit_name="test", title="", content=""):
    subreddit = reddit.subreddit(subreddit_name)
    post = subreddit.submit(
        title=title or "Test Post from blueBot",
        selftext=content or "This is a test post created by my Python bot!"
    )
    return post

def add_comment(post, comment_text=""):
    try:
        if not comment_text:
            raise ValueError("Comment text is required")
            
        # Try to get the submission first to verify it exists
        try:
            if isinstance(post, str):
                # Clean up the URL if needed
                post_url = post.strip()
                print(f"Getting submission from URL: {post_url}")
                submission = reddit.submission(url=post_url)
            else:
                submission = post
                
            # Verify we can access the submission
            print(f"Checking submission title: {submission.title}")
            
            # Check if the post is locked or archived
            if submission.locked:
                raise ValueError("This post is locked and cannot be commented on")
            if submission.archived:
                raise ValueError("This post is archived and cannot be commented on")
                
            # Add the comment with retry logic
            try:
                print("Attempting to add comment...")
                comment = submission.reply(comment_text)
                print(f"Comment added successfully: {comment.permalink}")
                return comment
            except Exception as e:
                error_msg = str(e).lower()
                if "ratelimit" in error_msg:
                    raise ValueError("Rate limit exceeded. Please wait a few minutes before trying again.")
                elif "thread_locked" in error_msg:
                    raise ValueError("Cannot comment on this post as it is locked.")
                else:
                    raise ValueError(f"Failed to add comment: {str(e)}")
        except Exception as e:
            print(f"Error accessing submission: {str(e)}")
            if "404" in str(e):
                raise ValueError("Post not found. Please check the URL.")
            elif "403" in str(e):
                raise ValueError("Access denied. The subreddit might be private or quarantined.")
            else:
                raise ValueError(f"Error accessing post: {str(e)}")
                
    except Exception as e:
        print(f"Error in add_comment: {str(e)}")
        raise ValueError(str(e))

def send_message(username, subject, message):
    try:
        # Validate inputs
        if not username or not subject or not message:
            raise ValueError("Username, subject, and message are required")
        
        # Clean the username (remove u/ if present)
        username = username.strip().replace('u/', '')
        
        print(f"Attempting to send message to {username}")
        
        # Get the redditor instance with retry logic
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                redditor = reddit.redditor(username)
                # Force a request to check if user exists
                print(f"Checking if user {username} exists...")
                redditor.id
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    print(f"Error checking user existence after {max_retries} retries: {str(e)}")
                    if "404" in str(e):
                        raise ValueError(f"User '{username}' not found")
                    raise
                print(f"Retry {retry_count}/{max_retries} checking user existence")
                time.sleep(1)  # Wait before retrying
            
        # Send message using PRAW with retry logic
        retry_count = 0
        while retry_count < max_retries:
            try:
                redditor.message(
                    subject=subject.strip(),
                    message=message.strip()
                )
                print(f"Message sent successfully to {username}")
                return True
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_msg = str(e).lower()
                    print(f"Error sending message after {max_retries} retries: {error_msg}")
                    if "forbidden" in error_msg:
                        raise ValueError(f"Unable to message u/{username}. They might have blocked messages or your account is too new.")
                    elif "invalid_grant" in error_msg:
                        raise ValueError("Reddit authentication failed. Please check your credentials.")
                    elif "restricted_to_pm" in error_msg:
                        raise ValueError(f"Cannot send message to u/{username}. They don't accept direct messages.")
                    else:
                        raise ValueError(f"Failed to send message: {str(e)}")
                print(f"Retry {retry_count}/{max_retries} sending message")
                time.sleep(1)  # Wait before retrying
                
    except Exception as e:
        print(f"Send message error: {str(e)}")
        raise ValueError(str(e))

def monitor_subreddit(subreddit_name, keyword=None, duration=60):
    subreddit = reddit.subreddit(subreddit_name)
    end_time = time.time() + duration
    
    for submission in subreddit.stream.submissions():
        if time.time() > end_time:
            break
            
        if keyword is None or keyword.lower() in submission.title.lower():
            submission.upvote()
            add_comment(submission, f"Great post about {keyword}!")
        time.sleep(2)

if __name__ == '__main__':
    app.run(debug=True) 