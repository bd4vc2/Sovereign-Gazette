import discord
import os
import feedparser
import requests
from datetime import datetime

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330

# Expanded Press Wires (Added Nintendo Life & Space.com)
FEEDS = {
    "front_page": "https://www.ign.com/rss/articles/news",
    "hangar": "https://www.gamespot.com/feeds/news/",
    "circuit": "https://www.pcgamer.com/rss/",
    "audio_anime": "https://www.stereogum.com/feed/",
    "nintendo": "https://www.nintendolife.com/feeds/latest",  # Added direct Nintendo wire
    "space": "https://www.space.com/feeds/all"               # Added direct Space wire
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
    """Scans press wires for matching beats. Falls back to top story if clear."""
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return None, False
        
    for entry in feed.entries[:15]:
        title_lower = entry.title.lower()
        summary_lower = entry.get('summary', '').lower()
        if any(keyword in title_lower or keyword in summary_lower for keyword in MY_INTERESTS):
            return entry, True
            
    return feed.entries[0], False

def get_tanque_verde_weather():
    """Fetches real-time weather data for Tanque Verde, AZ via open API."""
    try:
        # Lat/Lon coordinates for Tanque Verde, AZ
        url = "https://api.open-meteo.com/v1/forecast?latitude=32.25&longitude=-110.73&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
        res = requests.get(url).json()
        temp = int(res['current']['temperature_2m'])
        code = res['current']['weather_code']
        
        # Translate simple weather condition codes into vintage newspaper print terms
        conditions = "Fair Skies"
        if code in [1, 2, 3]: conditions = "Partly Cloudy"
        elif code in [45, 48]: conditions = "Overcast Fog"
        elif code in [51, 53, 55, 61, 63, 65]: conditions = "Desert Showers"
        elif code in [95, 96, 99]: conditions = "Localized Thunderstorms"
            
        return f"🌡️ {temp}°F • {conditions}"
    except Exception:
        return "📡 *Weather telegraph lines disconnected.*"

def calculate_gta_countdown():
    """Calculates exactly how close we are to GTA 6 target launch window."""
    target_date = datetime(2026, 11, 1)  # Target: November 1, 2026
    now = datetime.now()
    delta = target_date - now
    if delta.days > 0:
        return f"⏳ {delta.days} DAYS UNTIL GRAND THEFT AUTO VI EXPECTED LAUNCH"
    return "🔥 GRAND THEFT AUTO VI LAUNCH PERIOD ACTIVE"

class DispatchBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        try:
            print("Printing expanded morning edition...")
            
            # Read all 6 wire services
            story_1, hit_1 = scout_wire_service(FEEDS["front_page"])
            story_2, hit_2 = scout_wire_service(FEEDS["hangar"])
            story_3, hit_3 = scout_wire_service(FEEDS["circuit"])
            
            story_4, hit_4 = scout_wire_service(FEEDS["audio_anime"])
            if not story_4:
                crunchy = feedparser.parse("https://www.crunchyroll.com/news/rss")
                if crunchy.entries: story_4, hit_4 = scout_wire_service("https://www.crunchyroll.com/news/rss")

            story_5, hit_5 = scout_wire_service(FEEDS["nintendo"])
            story_6, hit_6 = scout_wire_service(FEEDS["space"])

            # Local metadata
            weather_report = get_tanque_verde_weather()
            gta_ticker = calculate_gta_countdown()

            # Dynamic Edition Flag
            has_scoop = any([hit_1, hit_2, hit_3, hit_4, hit_5, hit_6])
            paper_title = "📰 THE METROPOLIS DISPATCH  [SPECIAL EDITION]" if has_scoop else "📰 THE METROPOLIS DISPATCH"
            current_date = datetime.now().strftime("%B %d, %Y").upper()

            # Format Master Embed Layout
            embed = discord.Embed(
                title=paper_title,
                description=f"**CITY EDITION • {current_date} • PRICE: FREE**\n" + "═" * 32,
                color=0x34495e  # Deep Inkwell Grey
            )
            
            # Sub-header bar for Weather
            embed.add_field(name="📍 TANQUE VERDE WIRE", value=f"*{weather_report}*", inline=False)
            embed.add_field(name="═" * 32, value="**TODAY'S TOP CHRONICLES**", inline=False)
            
            # 1. FRONT PAGE DESK
            prefix = "◆ **BREAKING:** " if hit_1 else "▫️ "
            val = f"{prefix}[{story_1.title}]({story_1.link})" if story_1 else "▫️ *Press wires quiet.*"
            embed.add_field(name="LEAD CHRONICLE", value=val, inline=False)
            
            # 2. NINTENDO DISPATCH (New!)
            prefix = "◆ **BREAKING:** " if hit_5 else "▫️ "
            val = f"{prefix}[{story_5.title}]({story_5.link})" if story_5 else "▫️ *No Nintendo dispatches.*"
            embed.add_field(name="NINTENDO INTELLIGENCE", value=val, inline=False)
            
            # 3. SPACE & HANGAR
            # If the specific space wire has a matching topic, prioritize it here!
            chosen_hangar = story_6 if hit_6 else story_2
            chosen_hit = hit_6 if hit_6 else hit_2
            prefix = "◆ **BREAKING:** " if chosen_hit else "▫️ "
            val = f"{prefix}[{chosen_hangar.title}]({chosen_hangar.link})" if chosen_hangar else "▫️ *Frontier bands silent.*"
            embed.add_field(name="THE HANGAR & FRONTIER", value=val, inline=False)
            
            # 4. TECH CIRCUIT
            prefix = "◆ **BREAKING:** " if hit_3 else "▫️ "
            val = f"{prefix}[{story_3.title}]({story_3.link})" if story_3 else "▫️ *Silicon tracks quiet.*"
            embed.add_field(name="THE TECH CIRCUIT", value=val, inline=False)
            
            # 5. AUDIO & AMUSEMENTS
            prefix = "◆ **BREAKING:** " if hit_4 else "▫️ "
            val = f"{prefix}[{story_4.title}]({story_4.link})" if story_4 else "▫️ *Acoustic signals clear.*"
            embed.add_field(name="AMUSEMENTS & AUDIO", value=val, inline=False)

            # Bottom ticker columns
            embed.add_field(name="═" * 32, value=f"🎰 **ROCKSTAR MARKET TICKER**\n`{gta_ticker}`", inline=False)
            embed.set_footer(text="Published daily via GitHub Automation Services.")
        
            # Send DM
            user = await self.fetch_user(MY_USER_ID)
            dm_channel = user.dm_channel or await user.create_dm()
            await dm_channel.send(content="🗞️ **The morning paper has arrived.**", embed=embed)
            print("Dispatch printed and delivered successfully.")
            
        except Exception as e:
            print(f"Printing press error: {e}")
            
        finally:
            await self.close()

intents = discord.Intents.default()
intents.members = True 

client = DispatchBot(intents=intents)
client.run(TOKEN)
