import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ChatMemberHandler
)
from sheets import Sheets
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Sheets()

# ─── HELPERS ────────────────────────────────────────────────
def ref_link(bot_username, user_id):
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

def progress_bar(current, goal, length=10):
    filled = int(length * current / max(goal, 1))
    return "🟩" * filled + "⬜" * (length - filled)

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ─── /start ─────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referrer_id = None

    # Parse referral
    if args and args[0].startswith("ref_"):
        try:
            referrer_id = int(args[0].split("_")[1])
            if referrer_id == user.id:
                referrer_id = None
        except:
            referrer_id = None

    # Register user
    is_new = db.register_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        referrer_id=referrer_id
    )

    # Credit referrer if new user
    if is_new and referrer_id:
        points = db.add_referral(referrer_id, user.id, user.full_name)
        total = db.get_user(referrer_id)
        if total:
            try:
                bot_user = await context.bot.get_me()
                referrer_link = ref_link(bot_user.username, referrer_id)
                referrer_data = db.get_user(referrer_id)
                refs = int(referrer_data.get("Referrals", 0))
                pts  = int(referrer_data.get("Points", 0))

                # Milestone messages
                milestone_msg = ""
                if refs in [5, 10, 25, 50, 100]:
                    milestone_msg = f"\n\n🎉 *Milestone reached: {refs} referrals!*\nእንኳን ደስ አለዎ!"

                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        f"🎊 *New referral!*  አዲስ ሰው ተቀላቀለ!\n\n"
                        f"👤 *{user.full_name}* joined using your link\n"
                        f"⭐ You earned *{POINTS_PER_REFERRAL} points*\n"
                        f"📊 Total: *{refs} referrals* | *{pts} points*"
                        f"{milestone_msg}"
                    ),
                    parse_mode="Markdown"
                )
            except:
                pass

    bot_user = await context.bot.get_me()
    my_link = ref_link(bot_user.username, user.id)
    user_data = db.get_user(user.id)
    refs = int(user_data.get("Referrals", 0)) if user_data else 0
    pts  = int(user_data.get("Points", 0))    if user_data else 0

    keyboard = [
        [InlineKeyboardButton("📊 My Stats | ስታቲስቲካዬ", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard | ደረጃ ዝርዝር", callback_data="leaderboard")],
        [InlineKeyboardButton("🎁 Rewards | ሽልማቶች", callback_data="rewards")],
        [InlineKeyboardButton("🔗 My Invite Link | የጋበዣ ሊንክ", callback_data="mylink")],
        [InlineKeyboardButton("➕ Join Our Group | ቡድናችንን ተቀላቀሉ", url=GROUP_INVITE_LINK)],
    ]

    welcome = (
        f"👋 *Welcome, {user.full_name}!*\n"
        f"እንኳን ደህና መጡ!\n\n"
        f"🤖 I am the official invite bot for:\n"
        f"*{GROUP_NAME}*\n\n"
        f"📌 *How it works | እንዴት ይሰራል:*\n"
        f"1️⃣ Join our group ቡድናችንን ይቀላቀሉ\n"
        f"2️⃣ Share your invite link ሊንኩን ያጋሩ\n"
        f"3️⃣ Earn points & rewards ነጥቦች ያግኙ\n\n"
        f"🔗 *Your invite link:*\n`{my_link}`\n\n"
        f"📊 *Your stats:* {refs} referrals | {pts} points"
    )

    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── STATS ──────────────────────────────────────────────────
async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    bot_user = await context.bot.get_me()
    my_link = ref_link(bot_user.username, user.id)
    data = db.get_user(user.id)

    if not data:
        await query.edit_message_text("❌ User not found. Send /start first.")
        return

    refs   = int(data.get("Referrals", 0))
    pts    = int(data.get("Points", 0))
    joined = data.get("JoinedAt", "—")

    # Progress to next reward
    next_goal = next((r["refs"] for r in REWARDS if r["refs"] > refs), None)
    progress  = progress_bar(refs, next_goal) if next_goal else "🏆 MAX LEVEL"
    next_txt  = f"{progress} {refs}/{next_goal}" if next_goal else "🏆 All rewards unlocked!"

    # Check rank
    rank = db.get_rank(user.id)

    text = (
        f"📊 *Your Statistics | ስታቲስቲካዎ*\n\n"
        f"👤 *Name:* {user.full_name}\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"📅 *Joined:* {joined}\n\n"
        f"👥 *Referrals:* {refs}\n"
        f"⭐ *Points:* {pts}\n"
        f"🏅 *Rank:* #{rank}\n\n"
        f"📈 *Next reward progress:*\n{next_txt}\n\n"
        f"🔗 *Your link:*\n`{my_link}`\n\n"
        f"_Share this link to earn more points!_\n"
        f"_ይህን ሊንክ ያጋሩና ተጨማሪ ነጥቦች ያግኙ!_"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back | ተመለስ", callback_data="back_main")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))

# ─── LEADERBOARD ─────────────────────────────────────────────
async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    top = db.get_leaderboard(10)
    user_id = query.from_user.id
    rank = db.get_rank(user_id)

    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["🏆 *Top Inviters Leaderboard*\n🏆 *ምርጥ ሰዎች ደረጃ*\n"]

    for i, row in enumerate(top):
        name = row.get("FullName", "Unknown")[:20]
        refs = row.get("Referrals", 0)
        pts  = row.get("Points", 0)
        you  = " ← You" if str(row.get("UserID")) == str(user_id) else ""
        lines.append(f"{medals[i]} *{i+1}. {name}*{you}\n   👥 {refs} referrals | ⭐ {pts} pts")

    lines.append(f"\n📍 *Your rank: #{rank}*")

    keyboard = [[InlineKeyboardButton("🔙 Back | ተመለስ", callback_data="back_main")]]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── REWARDS ─────────────────────────────────────────────────
async def rewards_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = db.get_user(query.from_user.id)
    refs = int(data.get("Referrals", 0)) if data else 0

    lines = ["🎁 *Reward Tiers | የሽልማት ደረጃዎች*\n"]
    for r in REWARDS:
        done = "✅" if refs >= r["refs"] else "🔒"
        lines.append(
            f"{done} *{r['refs']} referrals* → {r['reward_en']}\n"
            f"   {r['reward_am']}\n"
        )

    lines.append(f"\n👥 *Your referrals: {refs}*")
    lines.append("_Keep sharing to unlock rewards!_\n_ሽልማቶቹን ለመሰናዶ ያጋሩ!_")

    keyboard = [
        [InlineKeyboardButton("📩 Claim Reward | ሽልማት ጠይቅ", callback_data="claim")],
        [InlineKeyboardButton("🔙 Back | ተመለስ", callback_data="back_main")]
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── CLAIM ───────────────────────────────────────────────────
async def claim_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = db.get_user(user.id)
    refs = int(data.get("Referrals", 0)) if data else 0
    claimed = data.get("Claimed", "").split(",") if data else []

    earned = [r for r in REWARDS if refs >= r["refs"] and str(r["refs"]) not in claimed]

    if not earned:
        await query.answer("No new rewards to claim yet! | እስካሁን ሽልማት የለም!", show_alert=True)
        return

    reward = earned[-1]  # Claim highest unlocked
    db.mark_claimed(user.id, reward["refs"])

    # Notify admin
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🎁 *REWARD CLAIM REQUEST*\n\n"
                f"👤 Name: {user.full_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📱 Username: @{user.username or 'N/A'}\n"
                f"👥 Referrals: {refs}\n"
                f"🏆 Reward: {reward['reward_en']}\n"
                f"💰 Level: {reward['refs']} referrals"
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    await query.edit_message_text(
        f"✅ *Reward Claimed! | ሽልማት ተጠየቀ!*\n\n"
        f"🏆 *{reward['reward_en']}*\n"
        f"{reward['reward_am']}\n\n"
        f"📩 Your request has been sent to the admin.\n"
        f"ጥያቄዎ ለአስተዳዳሪ ተልኳል።\n\n"
        f"⏳ You will be contacted within 24 hours.\n"
        f"በ24 ሰዓት ውስጥ ይደረስዎታል።",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back | ተመለስ", callback_data="back_main")
        ]])
    )

# ─── MY LINK ─────────────────────────────────────────────────
async def mylink_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bot_user = await context.bot.get_me()
    link = ref_link(bot_user.username, query.from_user.id)

    text = (
        f"🔗 *Your Personal Invite Link*\n"
        f"🔗 *የግልዎ የጋበዣ ሊንክ*\n\n"
        f"`{link}`\n\n"
        f"📋 *Copy and share this link!*\n"
        f"ይህን ሊንክ ቅዱና ያጋሩ!\n\n"
        f"💬 *Suggested message | የሚጠቁም መልዕክት:*\n"
        f"_\"Join {GROUP_NAME}! Click: {link}\"_\n\n"
        f"⭐ Each person who joins = *{POINTS_PER_REFERRAL} points*\n"
        f"ሊንኩን ጠቅ ያደርጉ = *{POINTS_PER_REFERRAL} ነጥብ*"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back | ተመለስ", callback_data="back_main")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))

# ─── BACK TO MAIN ────────────────────────────────────────────
async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    bot_user = await context.bot.get_me()
    my_link = ref_link(bot_user.username, user.id)
    data = db.get_user(user.id)
    refs = int(data.get("Referrals", 0)) if data else 0
    pts  = int(data.get("Points", 0))    if data else 0

    keyboard = [
        [InlineKeyboardButton("📊 My Stats | ስታቲስቲካዬ", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard | ደረጃ ዝርዝር", callback_data="leaderboard")],
        [InlineKeyboardButton("🎁 Rewards | ሽልማቶች", callback_data="rewards")],
        [InlineKeyboardButton("🔗 My Invite Link | የጋበዣ ሊንክ", callback_data="mylink")],
        [InlineKeyboardButton("➕ Join Our Group | ቡድናችንን ተቀላቀሉ", url=GROUP_INVITE_LINK)],
    ]

    await query.edit_message_text(
        f"🏠 *Main Menu | ዋና ምናሌ*\n\n"
        f"👥 *Referrals:* {refs} | ⭐ *Points:* {pts}\n\n"
        f"🔗 `{my_link}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── NEW MEMBER JOINED GROUP ─────────────────────────────────
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        bot_user = await context.bot.get_me()
        data = db.get_user(member.id)
        referrer_id = data.get("ReferrerID") if data else None

        referrer_note = ""
        if referrer_id:
            rdata = db.get_user(int(referrer_id))
            if rdata:
                referrer_note = f"\n👤 Invited by: *{rdata.get('FullName', '?')}*"

        await update.message.reply_text(
            f"🎉 Welcome *{member.full_name}*!\n"
            f"እንኳን ደህና መጡ!\n"
            f"{referrer_note}\n\n"
            f"💰 Want to earn rewards? Start the bot:\n"
            f"ሽልማቶች ለማግኘት ቦቱን ይጀምሩ:\n"
            f"👉 @{bot_user.username}",
            parse_mode="Markdown"
        )

# ─── ADMIN BROADCAST ─────────────────────────────────────────
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only | ለአስተዳዳሪ ብቻ")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast Your message here\n"
            "ፍቀድ: /broadcast መልዕክትዎን እዚህ ያስገቡ"
        )
        return

    msg = " ".join(context.args)
    users = db.get_all_users()
    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(f"📤 Sending to {len(users)} users...")

    for u in users:
        try:
            await context.bot.send_message(
                chat_id=int(u["UserID"]),
                text=f"📢 *Announcement | ማስታወቂያ*\n\n{msg}",
                parse_mode="Markdown"
            )
            sent += 1
            await asyncio.sleep(0.05)  # Rate limit
        except:
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast complete!\n"
        f"📤 Sent: {sent}\n❌ Failed: {failed}"
    )

# ─── ADMIN STATS ─────────────────────────────────────────────
async def adminstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = db.get_all_users()
    total = len(users)
    total_refs = sum(int(u.get("Referrals", 0)) for u in users)
    today = datetime.now().strftime("%Y-%m-%d")
    today_new = sum(1 for u in users if u.get("JoinedAt", "").startswith(today))

    await update.message.reply_text(
        f"📊 *Admin Dashboard*\n\n"
        f"👥 Total Users: *{total}*\n"
        f"🆕 Joined Today: *{today_new}*\n"
        f"🔗 Total Referrals: *{total_refs}*\n"
        f"📅 Date: {today}",
        parse_mode="Markdown"
    )

# ─── MAIN ────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("adminstats", adminstats))
    app.add_handler(CallbackQueryHandler(stats_handler,       pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(leaderboard_handler, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(rewards_handler,     pattern="^rewards$"))
    app.add_handler(CallbackQueryHandler(claim_handler,       pattern="^claim$"))
    app.add_handler(CallbackQueryHandler(mylink_handler,      pattern="^mylink$"))
    app.add_handler(CallbackQueryHandler(back_main,           pattern="^back_main$"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    logger.info("🤖 Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
