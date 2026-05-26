import discord
import os
import feedparser
import requests
import json
import random
from datetime import datetime, timedelta, timezone

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330

FEEDS = {
    "front_page": "https://feeds.feedburner.com/ign/news",       
    "hangar": "https://spaceflightnow.com/feed/",                 
    "tech_radar": "https://www.pcgamer.com/rss/",                 
    "tech_crunch": "https://techcrunch.com/feed/",                
    "nintendo": "https://www.nintendolife.com/feeds/latest",      
    "space": "https://www.nasa.gov/feeds/news-releases.rss" # Restored operational link
}

MY_INTERESTS = [
    "nintendo", "switch", "zelda", "mario", "metroid", "pokemon", "yoshi",
    "ksp", "kerbal", "space", "nasa", "spacex", "orbit", "rocket",
    "rockstar", "gta", "grand theft auto", "red dead", "rdr", "marston", "take-two",
    "rise against", "linkin park", "chester bennington", "from zero",
    "project zomboid", "zomboid", "subnautica", "unknown worlds",
    "jojo", "bizarre adventure", "jojo's", "anime", "manga", "crunchyroll",
    "rtx", "nvidia", "amd", "intel", "cpu", "gpu", "ai", "hardware"
]

MOD_FEEDS = {
    "Project Zomboid (Hydrocraft)": "https://steamcommunity.com/sharedfiles/cyberdeck_placeholder_zomboid/rss",
    "KSP (ReStock Engine Mods)": "https://steamcommunity.com/sharedfiles/cyberdeck_placeholder_ksp/rss"
}

CYBER_QUOTES = [
    "\"The past is gone and the future is not yet here, so we must live in the moment.\" — Hachiman Hikigaya",
    "\"The sky above the port was the color of television, tuned to a dead channel.\" — William Gibson",
    "\"Fly me to the moon, let me play among the stars...\" — Bart Howard",
    "\"If you aren't disappointed better than anyone else, you can't be a true cynic.\" — Hachiman Hikigaya",
    "\"There is no friction in a vacuum, but the launch pad is always burning.\"",
    "\"RAPIER engines at 100%. Structural stability is an illusion.\""
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

def check_mod_radar():
    updates = []
    for mod_name, url in MOD_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                updates.append(f"▫️ {mod_name}: Up to date.")
            else:
                updates.append(f"▫️ {mod_name}: Operational, no new patches.")
        except Exception:
            updates.append(f"▫️ {mod_name}: Standing by.")
    return "\n".join(updates) if updates else "▫️ *Mod tracking satellites dark.*"

def fetch_frontier_memoir():
    try:
        url = "https://history.muffinlabs.com/date"
        res = requests.get(url, timeout=4).json()
        event = res['data']['Events'][0]
        year = event['year']
        text = event['text']
        return f"📜 *ON THIS DAY IN {year}:*\n\"{text}\""
    except Exception:
        return "📜 *FRONTIER MEMOIR:*\n\"On this day, the telegraph operators logged standard orbital transfers without structural exceptions.\""

def get_tanque_verde_weather():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=32.25&longitude=-110.73"
            "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto"
        )
        res = requests.get(url, timeout=5).json()
        
        current_temp = int(res['current']['temperature_2m'])
        humidity = res['current']['relative_humidity_2m']
        wind = int(res['current']['wind_speed_10m'])
        code = res['current']['weather_code']
        
        high_temp = int(res['daily']['temperature_2m_max'][0])
        low_temp = int(res['daily']['temperature_2m_min'][0])
        
        conditions = "Fair Skies"
        if code in [1, 2, 3]: conditions = "Partly Cloudy"
        elif code in [45, 48]: conditions = "Overcast Desert Fog"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81]: conditions = "Desert Flash Showers"
        elif code in [95, 96, 99]: conditions = "Sonoran Thunderstorm"
        
        report = (
            f"🌵 **CURRENT CONDITIONS:**\n"
            f"▫️ *Temperature:* {current_temp}°F ({conditions})\n"
            f"▫️ *Thermal Bounds:* High {high_temp}°F / Low {low_temp}°F\n"
            f"▫️ *Atmosphere:* {humidity}% Humidity • Winds at {wind} MPH"
        )
        return report
    except Exception:
        return "📡 *Weather telegraph lines disconnected.*"

def get_home_station_telemetry():
    repo = os.getenv('GITHUB_REPOSITORY', 'Sovereign-Deck')
    run_id = os.getenv('GITHUB_RUN_NUMBER', 'LOCAL')
    sha = os.getenv('GITHUB_SHA', '0000000')[:7]
    
    status_path = "fleet_status.json"
    if os.path.exists(status_path):
        try:
            with open(status_path, "r") as f:
                data = json.load(f)
            return (
                f"🖥️ **DECK CONFIGURATION: ONLINE**\n"
                f"▫️ *Machine:* {data.get('hostname', 'HANNA-DESKTOP')}\n"
                f"▫️ *Action Build:* `#{run_id}` (sha: `{sha}`)\n"
                f"▫️ *Storage Load:* {data.get('disk_used', 'Unknown')}% used"
            )
        except Exception:
            pass
    return (
        f"🖥️ **HOME STATION TELEMETRY**\n"
        f"▫️ *Node:* HANNA-DESKTOP (Standby Core)\n"
        f"▫️ *GitHub Deployment:* `{repo}` Build `#{run_id}` [`{sha}`]"
    )

def fetch_project_logs():
    """Generates an ongoing log report of personal workspace environments."""
    return (
        "🛠️ **WORKSPACE ENVIRONMENT STACK**\n"
        "▫️ *Roblox Studio Moding:* F3X precise vector plugins operational.\n"
        "▫️ *Discord Bot Architecture:* Async network layers functional."
    )

def calculate_gta_countdown(current_local_time):
    # Strip the timezone info from current_local_time to make it naive,
    # or make the target aware. Replacing target works perfectly:
    target_date = datetime(2026, 11, 1, tzinfo=current_local_time.tzinfo)  
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

    return (
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

class DispatchBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            story_1, hit_1 = scout_wire_service(FEEDS["front_page"])
            story_2, hit_2 = scout_wire_service(FEEDS["hangar"])
            story_3, hit_3 = scout_wire_service(FEEDS["nintendo"])
            story_4, hit_4 = scout_wire_service(FEEDS["space"])
            
            tech_pc, hit_pc = scout_wire_service(FEEDS["tech_radar"])
            tech_tc, hit_tc = scout_wire_service(FEEDS["tech_crunch"])

            mst_now = datetime.now(timezone.utc) - timedelta(hours=7)
            weather_report = get_tanque_verde_weather()
            gta_ticker = calculate_gta_countdown(mst_now)
            summer_agenda = generate_daily_agenda(mst_now)
            mod_status = check_mod_radar()
            memoir = fetch_frontier_memoir()
            station_telemetry = get_home_station_telemetry()
            project_telemetry = fetch_project_logs()
            terminal_thought = random.choice(CYBER_QUOTES)

            hour = mst_now.hour
            if hour < 12:
                greeting, edition_label = "🗞️ **The morning paper has arrived.**", "MORNING EDITION"
            elif hour < 17:
                greeting, edition_label = "🗞️ **The afternoon edition is hot off the press.**", "AFTERNOON EDITION"
            else:
                greeting, edition_label = "🗞️ **The evening bulletin has been delivered.**", "EVENING BULLETIN"

            has_scoop = any([hit_1, hit_2, hit_3, hit_4, hit_pc, hit_tc])
            paper_title = "📰 THE METROPOLIS DISPATCH  [SPECIAL EDITION]" if has_scoop else "📰 THE METROPOLIS DISPATCH"
            current_date = mst_now.strftime("%B %d, %Y").upper()

            embed = discord.Embed(
                title=paper_title,
                description=f"**{edition_label} • {current_date} • PRICE: FREE**\n" + "═" * 32,
                color=0x34495e
            )
            
            embed.add_field(name="📍 TANQUE VERDE WIRE", value=weather_report, inline=False)
            embed.add_field(name="🛰️ REGIONAL INTEL", value=f"{station_telemetry}", inline=False)
            embed.add_field(name="💻 WORKSPACE MATRIX", value=f"{project_telemetry}", inline=False)
            embed.add_field(name="📜 FRONTIER MEMOIR", value=memoir, inline=False)
            embed.add_field(name="📟 TERMINAL THOUGHT LOG", value=f"*{terminal_thought}*", inline=False)
            
            embed.add_field(name="═" * 32, value="⚡ **TECH & RSS SILICON BREAKTHROUGHS**", inline=False)
            prefix_pc = "◆ **HOTWIRE:** " if hit_pc else "▫️ "
            prefix_tc = "◆ **HOTWIRE:** " if hit_tc else "▫️ "
            embed.add_field(name="PC Gaming & Rig Upgrades", value=f"{prefix_pc}[{tech_pc.title}]({tech_pc.link})" if tech_pc else "▫️ *Telegraph down.*", inline=False)
            embed.add_field(name="TechCrunch Silicon Intel", value=f"{prefix_tc}[{tech_tc.title}]({tech_tc.link})" if tech_tc else "▫️ *Telegraph down.*", inline=False)
            
            embed.add_field(name="═" * 32, value="📝 **DAILY SUMMER ROUTINE & AGENDA**", inline=False)
            embed.add_field(name="TODAY'S REQUIREMENTS", value=summer_agenda, inline=False)
            
            embed.add_field(name="📦 GAME MOD RADAR TRACKING", value=mod_status, inline=False)
            
            embed.add_field(name="═" * 32, value="**TODAY'S TOP CHRONICLES**", inline=False)
            
            scoop_count = 0
            for name, data in [("LEAD CHRONICLE", (story_1, hit_1)), 
                               ("NINTENDO INTELLIGENCE", (story_3, hit_3)), 
                               ("THE HANGAR & AEROSPACE", (story_4 if hit_4 else story_2, hit_4 if hit_4 else hit_2))]:
                story, hit = data
                if hit: scoop_count += 1
                prefix = "◆ **BREAKING:** " if hit else "▫️ "
                val = f"{prefix}[{story.title}]({story.link})" if story else "▫️ *Telegraph wire down.*"
                embed.add_field(name=name, value=val, inline=False)

            total_scoops = scoop_count + (1 if hit_pc else 0) + (1 if hit_tc else 0)
            if total_scoops > 0:
                embed.add_field(name="🚨 METROPOLIS WIRE ALERTS", value=f"`⚠️ PROXIMITY TELEGRAPH DETECTED {total_scoops} HIGH-PRIORITY STORIES IN YOUR FIELDS OF INTEREST.`", inline=False)

            embed.add_field(name="═" * 32, value=f"🎰 **ROCKSTAR MARKET TICKER**\n\n`{gta_ticker}`", inline=False)
            embed.set_footer(text="Published daily via GitHub Automation Services.")
        
            user = await self.fetch_user(MY_USER_ID)
            dm_channel = user.dm_channel or await user.create_dm()
            await dm_channel.send(content=greeting, embed=embed)
            print("Dispatch delivered successfully.")
            
        except Exception as e:
            print(f"Printing press error: {e}")
        finally:
            await self.close()

intents = discord.Intents.default()
intents.dm_messages = True

client = DispatchBot(intents=intents)
client.run(TOKEN)
