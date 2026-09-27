import os
import datetime
import pytz
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configure Bot Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set your target Channel ID and local Timezone
CHANNEL_ID = 123456789012345678  # Replace with your target channel ID (int)
TIMEZONE = "America/New_York"     # Replace with your local timezone (e.g., "America/Los_Angeles")

scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))

async def create_officer_poll():
    """Generates and sends the availability poll for the following day."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        return

    # Calculate tomorrow's date
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    tomorrow = now + datetime.timedelta(days=1)
    
    # Format date as MM/DD/YYYY without leading zeros (e.g., 9/28/2026)
    date_str = f"{tomorrow.month}/{tomorrow.day}/{tomorrow.year}"
    poll_question = f"Officer Availability: {date_str}"

    # Construct the Discord Native Poll
    poll = discord.Poll(
        question=poll_question,
        duration=datetime.timedelta(hours=24) # Poll lasts 24 hours
    )
    
    # Add response options
    poll.add_answer(text="Yes")
    poll.add_answer(text="No")
    poll.add_answer(text="Maybe")

    try:
        await channel.send(poll=poll)
        print(f"Successfully sent poll: '{poll_question}' to channel {CHANNEL_ID}")
    except Exception as e:
        print(f"Failed to send poll: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    
    # Schedule the job for Mon, Wed, Fri at 09:00 AM local time
    # day_of_week: mon, wed, fri
    scheduler.add_job(
        create_officer_poll, 
        trigger="cron", 
        day_of_week="mon,wed,fri", 
        hour=9, 
        minute=0
    )
    
    if not scheduler.running:
        scheduler.start()
        print("Scheduler initialized.")

# Place your Discord Bot Token here or load via environment variable
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

if __name__ == "__main__":
    bot.run(BOT_TOKEN)