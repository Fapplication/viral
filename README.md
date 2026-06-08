# 🤖 Viral Referral Telegram Bot
# ቦት ማዘጋጃ መመሪያ

A viral growth bot for Telegram with referral tracking, leaderboard,
rewards, and Google Sheets as database.

---

## 📁 Files
```
viral-bot/
├── bot.py           ← Main bot logic
├── sheets.py        ← Google Sheets database
├── config.py        ← Your settings (edit this first!)
├── requirements.txt ← Python packages
├── railway.toml     ← Hosting config
└── credentials.json ← Google service account (you create this)
```

---

## 🚀 SETUP GUIDE (Step by Step)

---

### STEP 1: Create Your Telegram Bot

1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Choose a name: e.g. `My Group Bot`
4. Choose a username: e.g. `mygroupinvite_bot`
5. Copy the **Bot Token** → paste in `config.py` as `BOT_TOKEN`

---

### STEP 2: Get Your Telegram User ID (Admin ID)

1. Open Telegram → search **@userinfobot**
2. Send `/start`
3. Copy your **Id** number → paste in `config.py` as `ADMIN_ID`

---

### STEP 3: Get Your Group ID

1. Add your bot to your group as **Admin**
2. Send any message in the group
3. Open this URL in browser (replace TOKEN):
   `https://api.telegram.org/botTOKEN/getUpdates`
4. Find `"chat":{"id":` — copy the negative number e.g. `-1001234567890`
5. Paste in `config.py` as `GROUP_ID`

---

### STEP 4: Set Up Google Sheets

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **Credentials → Create Credentials → Service Account**
5. Name it anything → Create
6. Click the service account → **Keys → Add Key → JSON**
7. Download the JSON file → rename it to `credentials.json`
8. Place it in the `viral-bot/` folder

9. Open your Google Sheet
10. Click **Share** → paste the service account email (from the JSON file, field `client_email`)
11. Give it **Editor** access

12. Copy your Sheet ID from the URL:
    `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
13. Paste in `config.py` as `SPREADSHEET_ID`

---

### STEP 5: Edit config.py

Open `config.py` and fill in:
```python
BOT_TOKEN         = "123456:ABCdef..."      # From BotFather
ADMIN_ID          = 987654321               # Your Telegram ID
GROUP_ID          = -1001234567890          # Your group ID
GROUP_NAME        = "Your Group Name"
GROUP_INVITE_LINK = "https://t.me/+XXXXX"  # Your group invite link
SPREADSHEET_ID    = "1BxiMVs0XRA5..."      # Your Sheet ID
```

---

### STEP 6: Deploy to Railway (Free Hosting)

1. Go to https://railway.app → Sign up with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Upload your `viral-bot` folder to a GitHub repo first
4. Connect Railway to that repo
5. Railway auto-detects Python and installs requirements
6. Click **Deploy**

OR run locally:
```bash
pip install -r requirements.txt
python bot.py
```

---

## ✨ Bot Features

| Feature | Description |
|---|---|
| 🔗 Referral links | Each user gets unique invite link |
| 📊 Stats | Users see their referrals, points, rank |
| 🏆 Leaderboard | Top 10 inviters displayed |
| 🎁 Rewards | Unlock prizes at 5/10/25/50/100/250 referrals |
| 📩 Claim | Users request rewards → admin notified |
| 📢 Broadcast | Admin sends message to ALL users |
| 🌍 Bilingual | English + Amharic |
| 📋 Google Sheets | All data stored automatically |

---

## 📢 Admin Commands

| Command | Action |
|---|---|
| `/adminstats` | See total users, referrals, today's joins |
| `/broadcast Hello!` | Send message to all bot users |

---

## 🎯 How Viral Growth Works

```
You → share bot link
  → Friend A starts bot → gets group invite
    → Friend A shares their own link
      → Friend B starts bot → gets group invite
        → chain continues...
```

Every user automatically becomes a promoter because they
want to earn points and rewards!
