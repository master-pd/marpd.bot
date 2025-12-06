# 🎭 MAR PD Bot - Ultimate Telegram Bot

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-3.0.0-red)

## 📸 Preview
![MAR PD Bot](https://img.shields.io/badge/MAR-PD%20Bot-FF6B35)

## ✨ Features
- 🤖 **AI Learning System** - Learns from conversations
- 🎮 **Gaming System** - Points, Levels, Leaderboards
- 👑 **Admin Control** - Owner + Group Admin Panel
- 📊 **Analytics** - User & Group Statistics
- 📸 **Media Support** - Profile & Media Handling
- ⚡ **Real-time** - Live Updates & Notifications

## 🚀 Quick Deployment

### Termux (Android)
```bash
# Install Python
pkg install python git -y

# Clone Repository
git clone https://github.com/master-pd/marpd.bot.git
cd marpd.bot

# Install Requirements
pip install -r requirements.txt

# Configure Bot
cp .env.example .env
nano .env  # Add your tokens

# Run Bot
python bot.py
