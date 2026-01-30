#!/usr/bin/env python3
"""
GitHub Follower Sync Tool
Automatically follows back your followers and unfollows those who unfollowed you.
"""

import os
import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURATION ====================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "TheLastKhan")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Safety Settings
MAX_ACTIONS_PER_RUN = 10  # Maximum follow/unfollow actions per run
ACTION_DELAY_MIN = 2  # Minimum seconds between actions
ACTION_DELAY_MAX = 5  # Maximum seconds between actions

# File Paths
DATA_DIR = Path(__file__).parent / "data"
WHITELIST_FILE = DATA_DIR / "whitelist.txt"
BLACKLIST_FILE = DATA_DIR / "blacklist.txt"
HISTORY_FILE = DATA_DIR / "history.json"

# ==================== GITHUB API ====================

GITHUB_API_BASE = "https://api.github.com"

def get_headers():
    """Get headers for GitHub API requests."""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Follower-Sync"
    }

def get_all_pages(url):
    """Fetch all pages from a paginated GitHub API endpoint."""
    users = []
    page = 1
    per_page = 100
    
    while True:
        response = requests.get(
            f"{url}?page={page}&per_page={per_page}",
            headers=get_headers()
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        if not data:
            break
        
        users.extend([user["login"] for user in data])
        
        if len(data) < per_page:
            break
        
        page += 1
        time.sleep(0.5)  # Small delay between pages
    
    return users

def get_followers():
    """Get list of users who follow you."""
    url = f"{GITHUB_API_BASE}/users/{GITHUB_USERNAME}/followers"
    return get_all_pages(url)

def get_following():
    """Get list of users you follow."""
    url = f"{GITHUB_API_BASE}/users/{GITHUB_USERNAME}/following"
    return get_all_pages(url)

def follow_user(username):
    """Follow a user."""
    url = f"{GITHUB_API_BASE}/user/following/{username}"
    response = requests.put(url, headers=get_headers())
    return response.status_code == 204

def unfollow_user(username):
    """Unfollow a user."""
    url = f"{GITHUB_API_BASE}/user/following/{username}"
    response = requests.delete(url, headers=get_headers())
    return response.status_code == 204

# ==================== FILE OPERATIONS ====================

def load_list_file(filepath):
    """Load a list of usernames from a file."""
    if not filepath.exists():
        return set()
    
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip() and not line.startswith("#"))

def load_history():
    """Load action history from JSON file."""
    if not HISTORY_FILE.exists():
        return {"follows": [], "unfollows": [], "last_run": None}
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history):
    """Save action history to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# ==================== TELEGRAM ====================

def send_telegram_message(message):
    """Send a message via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured, skipping notification")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def format_telegram_report(followed, unfollowed, stats):
    """Format a nice Telegram report message."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🔄 <b>GitHub Follower Sync Report</b>\n"
    message += f"📅 {now}\n\n"
    
    message += f"📊 <b>Stats:</b>\n"
    message += f"  • Followers: {stats['followers']}\n"
    message += f"  • Following: {stats['following']}\n\n"
    
    if followed:
        message += f"✅ <b>Followed Back ({len(followed)}):</b>\n"
        for user in followed[:10]:  # Limit to 10 to avoid long messages
            message += f"  • @{user}\n"
        if len(followed) > 10:
            message += f"  ... and {len(followed) - 10} more\n"
        message += "\n"
    
    if unfollowed:
        message += f"❌ <b>Unfollowed ({len(unfollowed)}):</b>\n"
        for user in unfollowed[:10]:
            message += f"  • @{user}\n"
        if len(unfollowed) > 10:
            message += f"  ... and {len(unfollowed) - 10} more\n"
        message += "\n"
    
    if not followed and not unfollowed:
        message += "✨ No changes needed - everything is in sync!"
    
    return message

# ==================== MAIN LOGIC ====================

def sync_followers():
    """Main sync logic."""
    print("=" * 50)
    print("🚀 GitHub Follower Sync - Starting...")
    print(f"👤 User: {GITHUB_USERNAME}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Validate token
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable not set!")
        return
    
    # Load whitelist and blacklist
    whitelist = load_list_file(WHITELIST_FILE)
    blacklist = load_list_file(BLACKLIST_FILE)
    
    print(f"📋 Whitelist: {len(whitelist)} users")
    print(f"🚫 Blacklist: {len(blacklist)} users")
    
    # Get current followers and following
    print("\n📥 Fetching followers...")
    followers = get_followers()
    print(f"   Found {len(followers)} followers")
    
    print("📤 Fetching following...")
    following = get_following()
    print(f"   Found {len(following)} following")
    
    # Convert to sets for easy comparison
    followers_set = set(f.lower() for f in followers)
    following_set = set(f.lower() for f in following)
    
    # Find who to follow (followers that I'm not following back)
    to_follow = []
    for user in followers:
        user_lower = user.lower()
        if user_lower not in following_set and user_lower not in blacklist:
            to_follow.append(user)
    
    # Find who to unfollow (following but they're not following back, not in whitelist)
    to_unfollow = []
    for user in following:
        user_lower = user.lower()
        if user_lower not in followers_set and user_lower not in whitelist:
            to_unfollow.append(user)
    
    print(f"\n🔍 Analysis:")
    print(f"   • Need to follow back: {len(to_follow)}")
    print(f"   • Need to unfollow: {len(to_unfollow)}")
    
    # Perform actions with limits
    followed = []
    unfollowed = []
    action_count = 0
    
    # Follow back
    print("\n✅ Following back...")
    for user in to_follow:
        if action_count >= MAX_ACTIONS_PER_RUN:
            print(f"   ⚠️ Reached max actions limit ({MAX_ACTIONS_PER_RUN})")
            break
        
        delay = random.uniform(ACTION_DELAY_MIN, ACTION_DELAY_MAX)
        time.sleep(delay)
        
        if follow_user(user):
            print(f"   ✓ Followed: {user}")
            followed.append(user)
            action_count += 1
        else:
            print(f"   ✗ Failed to follow: {user}")
    
    # Unfollow
    print("\n❌ Unfollowing...")
    for user in to_unfollow:
        if action_count >= MAX_ACTIONS_PER_RUN:
            print(f"   ⚠️ Reached max actions limit ({MAX_ACTIONS_PER_RUN})")
            break
        
        delay = random.uniform(ACTION_DELAY_MIN, ACTION_DELAY_MAX)
        time.sleep(delay)
        
        if unfollow_user(user):
            print(f"   ✓ Unfollowed: {user}")
            unfollowed.append(user)
            action_count += 1
        else:
            print(f"   ✗ Failed to unfollow: {user}")
    
    # Update history
    history = load_history()
    now = datetime.now().isoformat()
    
    for user in followed:
        history["follows"].append({"user": user, "timestamp": now})
    for user in unfollowed:
        history["unfollows"].append({"user": user, "timestamp": now})
    history["last_run"] = now
    
    # Keep only last 1000 entries
    history["follows"] = history["follows"][-1000:]
    history["unfollows"] = history["unfollows"][-1000:]
    
    save_history(history)
    
    # Send Telegram notification with UPDATED stats (after actions)
    final_followers = len(followers)  # Followers count doesn't change from our actions
    final_following = len(following) + len(followed) - len(unfollowed)  # Adjusted count
    stats = {"followers": final_followers, "following": final_following}
    
    if followed or unfollowed:
        message = format_telegram_report(followed, unfollowed, stats)
        send_telegram_message(message)
    else:
        # Optional: Send "no changes" message (comment out if too noisy)
        # message = format_telegram_report([], [], stats)
        # send_telegram_message(message)
        pass
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   • Followed: {len(followed)}")
    print(f"   • Unfollowed: {len(unfollowed)}")
    print("✅ Sync complete!")
    print("=" * 50)

if __name__ == "__main__":
    sync_followers()
