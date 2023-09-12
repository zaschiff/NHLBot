import discord
import requests
import settings

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from discord.ext import commands, tasks

teams = {
    "BOS": "Boston Bruins",
    "BUF": "Buffalo Sabres",
    "DET": "Detroit Red Wings",
    "MON": "Montreal Canadiens",
    "OTT": "Ottawa Senators",
    "TB":  "Tampa Bay Lightning",
    "TOR": "Toronto Maple Leafs",
    "FLA": "Florida Panthers",
    "CAR": "Carolina Hurricanes",
    "NJ":  "New Jersey Devils",
    "NYI": "New York Islanders",
    "NYR": "New York Rangers",
    "PHI": "Philidelphia Flyers",
    "PIT": "Pittsburgh Penguins",
    "WAS": "Washington Capitals",
    "CBJ": "Columbus Blue Jackets",
    "CHI": "Chicago Blackhaweks",
    "DAL": "Dallas Stars",
    "COL": "Colorado Avalanche",
    "STL": "St. Louis Blues",
    "NAS": "Nashville Predators",
    "WPG": "Winnipeg Jets",
    "MIN": "Minnesota Wild",
    "CGY": "Calgary Flames",
    "EDM": "Edmonton Oilers",
    "LA":  "Los Angeles Kings",
    "SJ":  "San Jose Sharks",
    "VAN": "Vancouver Canucks",
    "ARI": "Arizona Coyotes",
    "ANA": "Anaheim Ducks",
    "VEG": "Vegas Golden Knights",
    "SEA": "Seattle Kraken"
    }
old_news = {}
intents = discord.Intents.all()
dbNewsBot = commands.Bot(command_prefix="!", intents=intents)

def run():
    intents = discord.Intents.all()
    dbNewsBot = commands.Bot(command_prefix="!", intents=intents)

    @dbNewsBot.event
    async def on_ready():
        print("bot is active")
        sendInjuryInfo.start()
        sendNewsInfo.start()


    @tasks.loop(hours=1)
    async def sendInjuryInfo():
        injury_feed = "https://api.sportsdata.io/v3/nhl/projections/json/InjuredPlayers?key=24e501c1395c4852b2d5c414d567a329"
        req = requests.get(injury_feed)
        injury_result= req.json()

        injury_list = discord.Embed(
            title="Injury List",
            description="Current NHL injury List",
            color=discord.Color.brand_red()
        )

        if not injury_result == []:
            for player in injury_result:
                name, info = injured_player_format(player)
                injury_list.add_field(name=name, value=info, inline=False)
        else:
            injury_list.add_field(name="Nothing new...", value="", inline=False)

        await sendEmmbed("injury-list", injury_list)

    @tasks.loop(hours=1)
    async def sendNewsInfo():
        global old_news
        news_embed = discord.Embed(
            title="Current News",
            description="Current NHL News Articles",
            color = discord.Color.green()
        )

        stop_day = date.today() - timedelta(days=3)

        current_news_articles = getNews()

        article_count = 0

        for key_o in old_news.keys():
            for key_n in current_news_articles.keys():
                if key_o == key_n:
                    article_count += 1

        if article_count >= len(current_news_articles):
            news_embed.add_field(name="Nothing new...", value="", inline=False)
            await sendEmmbed('hockey-news', news_embed)
        else:
            for title, info in current_news_articles.items():
                if info['date'] > stop_day:
                    news_embed.add_field(name=title, value=info['url'], inline=False)
            await sendEmmbed('hockey-news', news_embed)
        
        old_news =  current_news_articles


        
    async def sendEmmbed(channel_name: str, card: discord.Embed):
        # channels = dbNewsBot.guilds[0].channels

        for guild in dbNewsBot.guilds:
            for channel in guild.channels:
                if channel.name == channel_name:
                        await channel.send(embed=card)
        

    def injured_player_format(player):

        name = player["FirstName"]+ " " +player["LastName"]
        
        info = f'''
            Status:        {player["Status"]}
            Team:          {teams[player["Team"]]}
            Position:      {player["Position"]}
        '''
        return name, info

    def getNews():
        primary_url = 'https://www.thescore.com/nhl/news'
        news_article = {}

        res = requests.get(primary_url)
        scoreSoup = BeautifulSoup(res.text, 'html.parser')

        for div in scoreSoup.find_all('div', class_='jsx-1435942676'):
            for a in div.find_all('a', href=True):
                title = div.find(class_='jsx-403783000 title')
                
                linkSplit = a['href'].split('/')
                for i in range(len(linkSplit)-1):
                    if linkSplit[i] == '':
                        linkSplit.pop(i)
                
                if len(linkSplit) > 2 and linkSplit[1] == 'news':
                    time_info = div.find_all('div', class_='info')[0].find_all('time')
                
                if len(linkSplit) > 2 and linkSplit[1] == 'news':
                    news_article[title.text] = {'url': primary_url + a['href'], 'date': datetime.fromisoformat(time_info[0]['datetime']).date()}
        
        return news_article
    
    dbNewsBot.run(settings.DISCORD_API_SECRET)

if __name__ == "__main__":
    run()


# API URLS***********************************************************
# injured_player_url = "https://api.sportsdata.io/v3/nhl/projections/json/InjuredPlayers?key=24e501c1395c4852b2d5c414d567a329"
# news_feed = f"https://api.sportsdata.io/v3/nhl/scores/json/NewsByDate/{today_str}?key=24e501c1395c4852b2d5c414d567a329"
# team_feed = "https://api.sportsdata.io/v3/nhl/scores/json/AllTeams?key=24e501c1395c4852b2d5c414d567a329"
#********************************************************************