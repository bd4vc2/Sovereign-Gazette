import discord
import os
import feedparser
from datetime import datetime

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330

FEEDS = {
    "front_page": "https://www.ign.com/rss/articles/news",
    "hangar": "https://www.gamespot.com/feeds/news/",
    "circuit": "https://www.pcgamer.com/rss/",
    "audio_anime": "https://www.stereogum.com/feed/"
}

MY_INTERESTS = [
    "nintendo", "switch", "zelda", "mario", "metroid", "pokemon", "yoshi",
    "ksp", "kerbal", "space", "nasa", "spacex", "orbit",
    "rockstar", "gta", "grand theft auto", "red dead", "rdr", "marston", "take-two",
    "rise against", "linkin park", "chester bennington", "from zero",
    "project zomboid", "zomboid", "subnautica", "unknown worlds",
    "jojo", "bizarre adventure", "jojo's", "anime", "manga", "crunchyroll"
]

def scout_wire_service(feed_url):
    """Scans the press wires for matching beats. Falls back to top story if clear."""
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return None, False
        
    for entry in feed.entries[:15]:
        title_lower = entry.title.lower()
        summary_lower = entry.get('summary', '').lower()
        if any(keyword in title_lower or keyword in summary_lower for keyword in MY_INTERESTS):
            return entry, True
            
    return feed.entries[0], False

class DispatchBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        try:
            print("Printing morning edition...")
            
            # Read the wires
            story_1, hit_1 = scout_wire_service(FEEDS["front_page"])
            story_2, hit_2 = scout_wire_service(FEEDS["hangar"])
            story_3, hit_3 = scout_wire_service(FEEDS["circuit"])
            
            story_4, hit_4 = scout_wire_service(FEEDS["audio_anime"])
            if not story_4:
                crunchy = feedparser.parse("https://www.crunchyroll.com/news/rss")
                if crunchy.entries:
                    story_4, hit_4 = scout_wire_service("https://www.crunchyroll.com/news/rss")

            # Determine Edition Status
            has_scoop = any([hit_1, hit_2, hit_3, hit_4])
            paper_title = "📰 THE METROPOLIS DISPATCH  [SPECIAL EDITION]" if has_scoop else "📰 THE METROPOLIS DISPATCH"
            paper_color = 0x34495e  # Deep Inkwell Grey
            
            current_date = datetime.now().strftime("%B %d, %Y").upper()

            # Format Newspaper Layout
            embed = discord.Embed(
                title=paper_title,
                description=f"**CITY EDITION • {current_date} • PRICE: FREE**\n" + "═" * 32,
                color=paper_color
            )
            
            # 1. FRONT PAGE DESK
            prefix = "◆ **BREAKING:** " if hit_1 else "▫️ "
            val = f"{prefix}[{story_1.title}]({story_1.link})" if story_1 else "▫️ *Press wires quiet on the front page.*"
            embed.add_field(name="LEAD CHRONICLE", value=val, inline=False)
            
            # 2. THE HANGAR DESK
            prefix = "◆ **BREAKING:** " if hit_2 else "▫️ "
            val = f"{prefix}[{story_2.title}]({story_2.link})" if story_2 else "▫️ *No updates from the hangar desk.*"
            embed.add_field(name="THE HANGAR & FRONTIER", value=val, inline=False)
            
            # 3. THE CIRCUIT DESK
            prefix = "◆ **BREAKING:** " if hit_3 else "▫️ "
            val = f"{prefix}[{story_3.title}]({story_3.link})" if story_3 else "▫️ *Silicon wires report no changes.*"
            embed.add_field(name="THE TECH CIRCUIT", value=val, inline=False)
            
            # 4. AUDIO & ENTERTAINMENT DESK
            prefix = "◆ **BREAKING:** " if hit_4 else "▫️ "
            val = f"{prefix}[{story_4.title}]({story_4.link})" if story_4 else "▫️ *Amusements and broadcasts quiet.*"
            embed.add_field(name="AMUSEMENTS & AUDIO", value=val, inline=False)

            embed.add_field(name="═" * 32, value="*Late deliveries reported to local distributors.*", inline=False)
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
