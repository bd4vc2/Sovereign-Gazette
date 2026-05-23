import discord
import os
import feedparser

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330

# Live RSS feeds for gaming sites
FEEDS = {
    "front_page": "https://corp.ign.com/feeds",          # IGN Main Feed
    "the_hangar": "https://www.gamespot.com/feeds/news/", # GameSpot News
    "the_circuit": "https://www.pcgamer.com/rss/"         # PC Gamer Feed
}

class GazetteBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        try:
            # 1. Automatically fetch live news from the RSS feeds
            print("Fetching live news feeds...")
            ign_feed = feedparser.parse(FEEDS["front_page"])
            gamespot_feed = feedparser.parse(FEEDS["the_hangar"])
            pcgamer_feed = feedparser.parse(FEEDS["the_circuit"])

            # Extract the top entry from each feed (with safety fallback if a site is down)
            front_page_story = ign_feed.entries[0] if ign_feed.entries else None
            the_hangar_story = gamespot_feed.entries[0] if gamespot_feed.entries else None
            the_circuit_story = pcgamer_feed.entries[0] if pcgamer_feed.entries else None

            # 2. Format Embed
            embed = discord.Embed(title="THE VELOSOVEREIGN GAZETTE", color=0x2ecc71)
            
            # Populate FRONT PAGE (IGN)
            if front_page_story:
                embed.add_field(
                    name="📰 FRONT PAGE", 
                    value=f"[{front_page_story.title}]({front_page_story.link})", 
                    inline=False
                )
            
            # Populate THE HANGAR (GameSpot)
            if the_hangar_story:
                embed.add_field(
                    name="🚀 THE HANGAR", 
                    value=f"[{the_hangar_story.title}]({the_hangar_story.link})", 
                    inline=False
                )
            
            # Populate THE CIRCUIT (PC Gamer)
            if the_circuit_story:
                embed.add_field(
                    name="🏎️ THE CIRCUIT", 
                    value=f"[{the_circuit_story.title}]({the_circuit_story.link})", 
                    inline=False
                )
        
            # 3. Send DM
            user = await self.fetch_user(MY_USER_ID)
            await user.send(content="🔔 **Sovereign Briefing Delivered.**", embed=embed)
            print("Gazette delivered successfully!")
            
        except Exception as e:
            print(f"An error occurred during execution: {e}")
            
        finally:
            # 4. Shut down (Task Complete)
            print("Shutting down bot...")
            await self.close()

# Ensure intents are handled
intents = discord.Intents.default()
intents.members = True 

client = GazetteBot(intents=intents)
client.run(TOKEN)
