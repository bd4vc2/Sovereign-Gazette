import discord
import os
import requests

# --- CONFIG ---
TOKEN = os.getenv('BOT_TOKEN')
MY_USER_ID = 1474235994789380330
# Using the raw URL ensures we always get the plain text
GIST_URL = "https://gist.githubusercontent.com/bd4vc2/dbd9213712fbf3467acb4e3d0c2b2b3a/raw/5cc2b1fc84b64fa67e618c3bb0a3cb7c8053054b/news.txt"

class GazetteBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        try:
            # 1. Fetch news from Gist
            response = requests.get(GIST_URL)
            response.raise_for_status() # Crashes gracefully if Gist is down
            content = response.text.strip()
            
            # 2. Format Embed
            parts = content.split('|')
            embed = discord.Embed(title="THE VELOSOVEREIGN GAZETTE", color=0x2ecc71)
            sections = ["📰 FRONT PAGE", "🚀 THE HANGAR", "🏎️ THE CIRCUIT"]
            
            for i, part in enumerate(parts):
                if i < len(sections):
                    embed.add_field(name=sections[i], value=part.strip(), inline=False)
            
            # 3. Send DM
            user = await self.fetch_user(MY_USER_ID)
            await user.send(content="🔔 **Sovereign Briefing Delivered.**", embed=embed)
            print("Gazette delivered successfully!")
            
        except Exception as e:
            print(f"An error occurred during execution: {e}")
            
        finally:
            # 4. Shut down (Task Complete) - wrapped in finally so it always exits
            print("Shutting down bot...")
            await self.close()

# FIX: We need to explicitly allow the bot to see server members / user profiles
intents = discord.Intents.default()
intents.members = True 

client = GazetteBot(intents=intents)
client.run(TOKEN)
