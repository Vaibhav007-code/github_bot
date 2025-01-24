# Reddit Bot Controller

A web-based Reddit bot controller built with Flask that allows you to automate various Reddit actions like posting, commenting, messaging, and monitoring subreddits.

## Features

- Create posts in any subreddit
- Add comments to existing posts
- Send direct messages to users
- Monitor subreddits for specific keywords
- Track activity statistics
- Modern, responsive UI

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Vaibhav007-code/github_bot.git
cd github_bot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a Reddit App:
- Go to https://www.reddit.com/prefs/apps
- Click "Create App" or "Create Another App"
- Fill in the details:
  - Name: YourBotName
  - Type: Script
  - Description: Your bot description
  - About URL: Can be blank
  - Redirect URI: http://localhost:8080

4. Create a `.env` file in the project root:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=script:YourBotName:v1.0
FLASK_SECRET_KEY=your_secret_key
```

5. Run the application:
```bash
python app.py
```

## Deployment

This project is configured for deployment on Vercel. The necessary configuration is included in `vercel.json`.

To deploy:
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project directory
3. Follow the prompts to deploy

## Environment Variables

Make sure to set these environment variables in your Vercel project settings:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USERNAME
- REDDIT_PASSWORD
- REDDIT_USER_AGENT
- FLASK_SECRET_KEY

## License

MIT License 