import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from script5 import find_fairest_meetup_point, get_nearby_venues, filter_and_categorise, snap_to_mrt
from script6 import parse_availability
from script7 import find_overlap 

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)   

group_data={}

def get_group(chat_id):
    if chat_id not in group_data:
        group_data[chat_id] = {
            "addresses":{},
            "availability": {}
        }
    return group_data[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to ThirdSpace.\n\n"
        "I help your group find the fairest place to meet based on everyone's location and availability.\n\n"
        "Commands:\n"
        "/address [your area] - Submit your location\n"
        "/available [your availability] - Submit when you are free\n"
        "/meetup - Find the best meetup spot and time\n"
        "/reset - Start over\n\n"
        "Example:\n"
        "/address Tampines\n"
        "/available Saturday 2pm to 6pm\n\n"
        "Once everyone has submitted, type /meetup."
    )

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    group = get_group(chat_id)

    if not context.args:
        await update.message.reply_text("Please include your address. Example: /address Tampines, Singapore")
        return

    address = " ".join(context.args) + ", Singapore"
    group["addresses"][user_name] = address

    await update.message.reply_text(
        f"✅ Got {user_name}'s address: {address}\n"
        f"📍 {len(group['addresses'])} address(es) collected so far."
    )

async def handle_availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    group = get_group(chat_id)

    if not context.args:
        await update.message.reply_text("Please include your availability. Example: /available Saturday after 2pm")
        return

    availability_text = " ".join(context.args)
    group["availability"][user_name] = availability_text

    await update.message.reply_text(
        f"✅ Got {user_name}'s availability: {availability_text}\n"
        f"🗓 {len(group['availability'])} response(s) collected so far."
    )

async def find_meetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group = get_group(chat_id)

    if len(group["addresses"]) < 2:
        await update.message.reply_text("Need at least 2 addresses. Use /address to submit yours.")
        return

    if len(group["availability"]) < 2:
        await update.message.reply_text("Need at least 2 availability responses. Use /available to submit yours.")
        return

    await update.message.reply_text("🔍 Finding the best meetup spot for your group, hang tight...")

    addresses = list(group["addresses"].values())
    best_point, variance = find_fairest_meetup_point(addresses)
    #added bottom line of code to include the snap to mrt function
    best_point = snap_to_mrt(best_point[0], best_point[1])
    venues = get_nearby_venues(best_point[0], best_point[1])
    filtered = filter_and_categorise(venues)

    all_availability = []
    for name, message in group["availability"].items():
        parsed = parse_availability(name, message)
        if not parsed["slots"]: 
            await update.message.reply_text(f"⚠️ {name}'s availability couldn't be parsed."
                                            f"Please use /available with a day included. \n"
                                            f"Example: /available Saturday 7pm to 10pm")
            return
        all_availability.append(parsed)
    
    overlap = find_overlap(all_availability)

    response = "📍 *Best meeting area found!*\n\n"

    if overlap:
        response += "*When you can all meet:*\n"
        for slot in overlap:
            response += f"  {slot['day']}: {slot['start']} to {slot['end']}\n"
    else:
        response += "❌ No overlapping availability found. Ask everyone to update with /available.\n"

    response += "\n*Venue suggestions nearby:*\n"

    if not filtered:
        response += "No venues found nearby.\n"
    else:
        from script4 import VENUE_CATEGORIES
        for category in VENUE_CATEGORIES.keys():
            category_venues = [v for v in filtered if v["category"] == category]
            if not category_venues:
                continue
            response += f"\n_{category.upper()}_\n"
            for venue in category_venues[:2]:
                free_label = "FREE" if venue["is_free"] else "PAID"
                response += f"  • {venue['name']} ({venue['rating']}⭐) | {free_label}\n"
                response += f"    {venue['address']}\n"

    await update.message.reply_text(response, parse_mode="Markdown")
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_data[chat_id] = {
        "addresses": {},
        "availability": {}
    }
    await update.message.reply_text("🔄 Reset done. Start fresh with /address.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("address", handle_address))
    app.add_handler(CommandHandler("available", handle_availability))
    app.add_handler(CommandHandler("meetup", find_meetup))
    app.add_handler(CommandHandler("reset", reset))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
