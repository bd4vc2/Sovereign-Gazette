import discord
import os
import feedparser
import requests
from datetime import datetime, timedelta

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330

FEEDS = {
    "front_page": "https://www.ign.com/rss/articles/news",
    "hangar": "https://www.gamespot.com/feeds/news/",
    "circuit": "https://www.pcgamer.com/rss/",
    "audio_anime": "https://www.stereogum.com/feed/",
    "nintendo": "https://www.nintendolife.com/feeds/latest",
    "space": "https://www.space.com/feeds/all"
}

MY_INTERESTS = [
    "nintendo", "switch", "zelda", "mario", "metroid", "pokemon", "yoshi",
    "ksp", "kerbal", "space", "nasa", "spacex", "orbit", "rocket",
    "rockstar", "gta", "grand theft auto", "red dead", "rdr", "marston", "take-two",
    "rise against", "linkin park", "chester bennington", "from zero",
    "project zomboid", "zomboid", "subnautica", "unknown worlds",
    "jojo", "bizarre adventure", "jojo's", "anime", "manga", "crunchyroll"
]

def scout_wire_service(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        if not feed or not feed.entries:
            return None, False
        for entry in feed.entries[:15]:
            title_lower = entry.title.lower()
            summary_lower = entry.get('summary', '').lower()
            if any(keyword in title_lower or keyword in summary_lower for keyword in MY_INTERESTS):
                return entry, True
        return feed.entries[0], False
    except Exception:
        return None, False

def get_tanque_verde_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=32.25&longitude=-110.73&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
        res = requests.get(url, timeout=5).json()
        temp = int(res['current']['temperature_2m'])
        code = res['current']['weather_code']
        conditions = "Fair Skies"
        if code in [1, 2, 3]: conditions = "Partly Cloudy"
        elif code in [45, 48]: conditions = "Overcast Fog"
        elif code in [51, 53, 55, 61, 63, 65]: conditions = "Desert Showers"
        return f"🌡️ {temp}°F • {conditions}"
    except Exception:
        return "📡 *Weather telegraph lines disconnected.*"

def calculate_gta_countdown(current_local_time):
    target_date = datetime(2026, 11, 1)  # Target: November 2026
    delta = target_date - current_local_time
    return f"⏳ {delta.days} DAYS UNTIL GRAND THEFT AUTO VI EXPECTED LAUNCH" if delta.days > 0 else "🔥 GTA VI ACTIVE"

def generate_daily_agenda(current_local_time):
    day_name = current_local_time.strftime("%A")
    
    if day_name in ["Monday", "Wednesday", "Friday"]:
        workout_text = (
            "🏋️ **SUMMER STRENGTH DAY**\n"
            "• *Warm-up (3m):* Jump rope / jacks to Rise Against\n"
            "• *Circuit (3 rounds):* 5 Incline Push-ups, 10 Squats/Lunges, 30s Plank"
        )
    else:
        workout_text = "🛋️ **RECOVERY DAY:** Rest up, stay active, let the muscles rebuild."

    agenda_str = (
        "🍏 **DAILY FUEL & NUTRIENTS**\n"
        "▫️ *Protein:* Eggs, chicken, milk, or peanut butter with meals\n"
        "▫️ *Energy:* Oats, rice, potatoes, or whole grains\n"
        "▫️ *Hydration:* Drink clear-urine levels of fresh water\n\n"
        f"{workout_text}\n\n"
        "📋 **BEFORE MIDNIGHT CHECKLIST**\n"
        "[ ] Hit the 3-Meal Rule for growth fuel\n"
        "[ ] Complete today's physical activity/rest\n"
        "[ ] Screen-free wind down 30 mins before bed\n"
        "[ ] Secure 8 to 10 hours of high-quality sleep"
    )
    return agenda_str

class DispatchBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        try:
            print("Printing expanded morning edition...")
            story_1, hit_1 = scout_wire_service(FEEDS["front_page"])
            story_2, hit_2 = scout_wire_service(FEEDS["hangar"])
            story_3, hit_3 = scout_wire_service(FEEDS["circuit"])
            story_4, hit_4 = scout_wire_service(FEEDS["audio_anime"])
            story_5, hit_5 = scout_wire_service(FEEDS["nintendo"])
            story_6, hit_6 = scout_wire_service(FEEDS["space"])

            # Adjust for Mountain Standard Time (UTC - 7) inside the runner container
            mst_now = datetime.utcnow() - timedelta(hours=7)

            weather_report = get_tanque_verde_weather()
            gta_ticker = calculate_gta_countdown(mst_now)
            summer_agenda = generate_daily_agenda(mst_now)

            # Dynamic greetings calibrated for local MST hours
            hour = mst_now.hour
            if hour < 12:
                greeting = "🗞️ **The morning paper has arrived.**"
                edition_label = "MORNING EDITION"
            elif hour < 17:
                greeting = "🗞️ **The afternoon edition is hot off the press.**"
                edition_label = "AFTERNOON EDITION"
            else:
                greeting = "🗞️ **The evening bulletin has been delivered.**"
                edition_label = "EVENING BULLETIN"

            has_scoop = any([hit_1, hit_2, hit_3, hit_4, hit_5, hit_6])
            paper_title = "📰 THE METROPOLIS DISPATCH  [SPECIAL EDITION]" if has_scoop else "📰 THE METROPOLIS DISPATCH"
            current_date = mst_now.strftime("%B %d, %Y").upper()

            embed = discord.Embed(
                title=paper_title,
                description=f"**{edition_label} • {current_date} • PRICE: FREE**\n" + "═" * 32,
                color=0x34495e
            )
            
            embed.add_field(name="📍 TANQUE VERDE WIRE", value=f"*{weather_report}*", inline=False)
            embed.add_field(name="═" * 32, value="📝 **DAILY SUMMER ROUTINE & AGENDA**", inline=False)
            embed.add_field(name="TODAY'S REQUIREMENTS", value=summer_agenda, inline=False)
            
            embed.add_field(name="═" * 32, value="**TODAY'S TOP CHRONICLES**", inline=False)
            
            scoop_count = 0
            for name, data in [("LEAD CHRONICLE", (story_1, hit_1)), ("NINTENDO INTELLIGENCE", (story_5, hit_5)), 
                               ("THE HANGAR & FRONTIER", (story_6 if hit_6 else story_2, hit_6 if hit_6 else hit_2)),
                               ("THE TECH CIRCUIT", (story_3, hit_3)), ("AMUSEMENTS & AUDIO", (story_4, hit_4))]:
                story, hit = data
                if hit:
                    scoop_count += 1
                prefix = "◆ **BREAKING:** " if hit else "▫️ "
                val = f"{prefix}[{story.title}]({story.link})" if story else "▫️ *Telegraph wire down.*"
                embed.add_field(name=name, value=val, inline=False)

            if scoop_count > 0:
                embed.add_field(name="🚨 METROPOLIS WIRE ALERTS", value=f"`⚠️ PROXIMITY TELEGRAPH DETECTED {scoop_count} HIGH-PRIORITY STORIES IN YOUR FIELDS OF INTEREST.`", inline=False)

            embed.add_field(name="═" * 32, value=f"🎰 **ROCKSTAR MARKET TICKER**\n\n`{gta_ticker}`", inline=False)
            embed.set_footer(text="Published daily via GitHub Automation Services.")
        
            user = await self.fetch_user(MY_USER_ID)
            await user.send(content=greeting, embed=embed)
            print("Dispatch delivered successfully.")
            
        except Exception as e:
            print(f"Printing press error: {e}")
        finally:
            await self.close()

# Fixed Intent handling flags for secure DM initialization
intents = discord.Intents.default()
intents.dm_messages = True

client = DispatchBot(intents=intents)
client.run(TOKEN)
