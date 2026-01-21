# 🔄 GitHub Follower Sync

Automatically sync your GitHub followers - follow back those who follow you, and unfollow those who don't follow back.

## ✨ Features

- ✅ **Auto Follow-Back**: Automatically follows users who follow you
- ❌ **Auto Unfollow**: Unfollows users who don't follow you back
- 📋 **Whitelist**: Protect specific users from being unfollowed
- 🚫 **Blacklist**: Block specific users from being followed
- 📱 **Telegram Notifications**: Get notified of all changes
- 🔒 **Safe & Slow**: Built-in rate limiting and action delays
- 📊 **History Tracking**: Keep track of all follow/unfollow actions
- ⏰ **Hourly Sync**: Runs automatically every hour via GitHub Actions

## 🚀 Setup

### 1. Fork or Clone This Repository

```bash
git clone https://github.com/TheLastKhan/github-follower-sync.git
cd github-follower-sync
```

### 2. Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Follower Sync"
4. Select scope: `user:follow`
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 3. Create Telegram Bot (Optional)

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the **Bot Token** you receive
4. Start a chat with your new bot
5. Get your Chat ID:
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` - that number is your Chat ID

### 4. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `GH_PAT` | Your GitHub Personal Access Token | ✅ Yes |
| `GH_USERNAME` | `TheLastKhan` | ✅ Yes |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | ❌ Optional |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | ❌ Optional |

### 5. Enable GitHub Actions

1. Go to your repository → Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. The sync will run automatically every hour

### 6. (Optional) Manual Run

You can trigger a sync manually:
1. Go to Actions → "GitHub Follower Sync"
2. Click "Run workflow" → "Run workflow"

## ⚙️ Configuration

### Whitelist (Never Unfollow)

Edit `data/whitelist.txt` to add users you never want to unfollow:

```
# Friends I want to keep following
torvalds
github
microsoft
```

### Blacklist (Never Follow)

Edit `data/blacklist.txt` to add users you never want to follow back:

```
# Spam accounts
spammer123
bot-account
```

### Safety Settings

In `main.py`, you can adjust:

```python
MAX_ACTIONS_PER_RUN = 10  # Max follow/unfollow per run
ACTION_DELAY_MIN = 2      # Min seconds between actions
ACTION_DELAY_MAX = 5      # Max seconds between actions
```

## 📊 How It Works

```
┌─────────────────────────────────────────────────────┐
│                  Every Hour                          │
├─────────────────────────────────────────────────────┤
│  1. Fetch your followers list                       │
│  2. Fetch your following list                       │
│  3. Compare the two lists                           │
│  4. Follow back new followers (not in blacklist)    │
│  5. Unfollow non-followers (not in whitelist)       │
│  6. Send Telegram notification (if configured)      │
│  7. Save action history                             │
└─────────────────────────────────────────────────────┘
```

## 🔒 Security Notes

- Your GitHub token is stored securely in GitHub Secrets
- The token is never exposed in logs or code
- Only `user:follow` scope is needed (minimal permissions)
- All actions are logged for transparency

## 📱 Telegram Notification Example

```
🔄 GitHub Follower Sync Report
📅 2026-01-19 15:45:00

📊 Stats:
  • Followers: 150
  • Following: 145

✅ Followed Back (2):
  • @newuser1
  • @newuser2

❌ Unfollowed (1):
  • @unfollower1
```

## 🛠️ Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_token"
export GITHUB_USERNAME="TheLastKhan"
export TELEGRAM_BOT_TOKEN="your_bot_token"  # Optional
export TELEGRAM_CHAT_ID="your_chat_id"      # Optional

# Run
python main.py
```

## 📄 License

MIT License - Use freely!

## ⚠️ Disclaimer

Use this tool responsibly. Excessive automated actions may violate GitHub's Terms of Service. This tool is designed to be slow and respectful of rate limits, but use at your own risk.
