import discord
import os
import feedparser
import requests
from datetime import datetime

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

def calculate_gta_countdown():
    target_date = datetime(2026, 11, 1)  # Target: November 2026
    delta = target_date - datetime.now()
    return f"⏳ {delta.days} DAYS UNTIL GRAND THEFT AUTO VI EXPECTED LAUNCH" if delta.days > 0 else "🔥 GTA VI ACTIVE"

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

            weather_report = get_tanque_verde_weather()
            gta_ticker = calculate_gta_countdown()

            has_scoop = any([hit_1, hit_2, hit_3, hit_4, hit_5, hit_6])
            paper_title = "📰 THE METROPOLIS DISPATCH  [SPECIAL EDITION]" if has_scoop else "📰 THE METROPOLIS DISPATCH"
            current_date = datetime.now().strftime("%B %d, %Y").upper()

            embed = discord.Embed(
                title=paper_title,
                description=f"**CITY EDITION • {current_date} • PRICE: FREE**\n" + "═" * 32,
                color=0x34495e
            )
            
            embed.add_field(name="📍 TANQUE VERDE WIRE", value=f"*{weather_report}*", inline=False)
            embed.add_field(name="═" * 32, value="**TODAY'S TOP CHRONICLES**", inline=False)
            
            for name, data in [("LEAD CHRONICLE", (story_1, hit_1)), ("NINTENDO INTELLIGENCE", (story_5, hit_5)), 
                               ("THE HANGAR & FRONTIER", (story_6 if hit_6 else story_2, hit_6 if hit_6 else hit_2)),
                               ("THE TECH CIRCUIT", (story_3, hit_3)), ("AMUSEMENTS & AUDIO", (story_4, hit_4))]:
                story, hit = data
                prefix = "◆ **BREAKING:** " if hit else "▫️ "
                val = f"{prefix}[{story.title}]({story.link})" if story else "▫️ *Telegraph wire down.*"
                embed.add_field(name=name, value=val, inline=False)

            embed.add_field(name="═" * 32, value=f"🎰 **ROCKSTAR MARKET TICKER**\n\n`{gta_ticker}`", inline=False)
            embed.set_footer(text="Published daily via GitHub Automation Services.")
        
            user = await self.fetch_user(MY_USER_ID)
            dm_channel = user.dm_channel or await user.create_dm()
            await dm_channel.send(content="🗞️ **The morning paper has arrived.**", embed=embed)
            print("Dispatch delivered successfully.")
            
        except Exception as e:
            print(f"Printing press error: {e}")
        finally:
            await self.close()

intents = discord.Intents.default()
intents.members = True 

client = DispatchBot(intents=intents)
client.run(TOKEN)
