# ============================================================
# config.py — Edit these values before running
# ============================================================

# ── Bot Settings ─────────────────────────────────────────────
BOT_TOKEN   = "8510325271:AAHcnyFvpYxN_kXIipLMg42RF298HfNiDLQ"        # From @BotFather
ADMIN_ID    =                # Your Telegram user ID (get from @userinfobot)

# ── Group/Channel ────────────────────────────────────────────
GROUP_ID          = -1001234567890    # Your group/channel ID (negative number)
GROUP_NAME        = "ozone2024"   # Your group display name
GROUP_INVITE_LINK = "https://t.me/ozone2024"  # Your group invite link

# ── Points ───────────────────────────────────────────────────
POINTS_PER_REFERRAL = 10             # Points earned per referral

# ── Google Sheets ────────────────────────────────────────────
SHEET_CREDENTIALS = "credentials.json"   # Google service account JSON file
SPREADSHEET_ID    = "YOUR_GOOGLE_SHEET_ID"  # From your Google Sheet URL

# ── Reward Tiers ─────────────────────────────────────────────
# Add or edit reward levels here
REWARDS = [
    {
        "refs": 5,
        "reward_en": "🎖 Bronze Badge + Shoutout in group",
        "reward_am": "🎖 የነሐስ ባጅ + በቡድን ውስጥ ማስታወቂያ"
    },
    {
        "refs": 10,
        "reward_en": "🥈 Silver Badge + 50 ETB Mobile Recharge",
        "reward_am": "🥈 የብር ባጅ + 50 ብር ሞባይል ቻርጅ"
    },
    {
        "refs": 25,
        "reward_en": "🥇 Gold Badge + 150 ETB Mobile Recharge",
        "reward_am": "🥇 የወርቅ ባጅ + 150 ብር ሞባይል ቻርጅ"
    },
    {
        "refs": 50,
        "reward_en": "💎 Diamond Badge + 500 ETB Cash Prize",
        "reward_am": "💎 የዳይሞንድ ባጅ + 500 ብር የጥሬ ገንዘብ ሽልማት"
    },
    {
        "refs": 100,
        "reward_en": "👑 VIP Status + 1000 ETB Cash Prize + Exclusive Content",
        "reward_am": "👑 VIP ደረጃ + 1000 ብር ሽልማት + ልዩ ይዘት"
    },
    {
        "refs": 250,
        "reward_en": "🏆 LEGEND Badge + 3000 ETB Cash Prize + Admin Role",
        "reward_am": "🏆 አፈ ታሪክ ባጅ + 3000 ብር + አስተዳዳሪ ሚና"
    },
]
