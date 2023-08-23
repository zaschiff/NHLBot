import requests
import json
from datetime import datetime, timedelta
import discord
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
# date format
# 


# API URLS***********************************************************
# injured_player_url = "https://api.sportsdata.io/v3/nhl/projections/json/InjuredPlayers?key=24e501c1395c4852b2d5c414d567a329"
# news_feed = f"https://api.sportsdata.io/v3/nhl/scores/json/NewsByDate/{today_str}?key=24e501c1395c4852b2d5c414d567a329"
# team_feed = "https://api.sportsdata.io/v3/nhl/scores/json/AllTeams?key=24e501c1395c4852b2d5c414d567a329"
#********************************************************************

# TESTING DATA PULLS and INFORMATION GATHERING***********************
# req = requests.get(news_feed)
# with open("news_info.json", 'w') as f:
#     json.dump(req.json(), f)
#********************************************************************

intents = discord.Intents.all()
dbNewsBot = commands.Bot(command_prefix="!", intents=intents)

@dbNewsBot.event
async def on_ready():
    print("bot is active")
    sendInjuryInfo.start()
    sendNewsInfo.start()

# change this to 2 hours when implementing the API Call
@tasks.loop(hours=2)
async def sendInjuryInfo():
    # replace this with API Call
    # with open("injured_test.json", 'r')  as i:
    #     players_info = json.load(i)
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
        injury_list.add_field(name="Nothing New", value="", inline=False)

    await sendEmmbed("injury-list", injury_list)

# change this to 2 hours when implementing api
@tasks.loop(hours=2)
async def sendNewsInfo():
    # replace with api call
    # with open("news_info.json", 'r') as n:
    #     news_list = json.load(n)
    today_str = datetime.strftime(datetime.today(), "%Y-%b-%d").upper()
    news_feed = f"https://api.sportsdata.io/v3/nhl/scores/json/NewsByDate/{today_str}?key=24e501c1395c4852b2d5c414d567a329"
    req = requests.get(news_feed)
    news_results = req.json()
        
    news_articles = discord.Embed(
        title="Recent News",
        description="Current League updates",
        color=discord.Color.yellow()
    )

    if not news_results == []:
        for article in news_results:
            title, content, url, date_written = news_article_format(article)
            news_articles.add_field(name=title, value="\n"+date_written+"\n"+content+"\n\n" + url, inline=False)
    else:
        news_articles.add_field(name=f"No New Hockey News for Today ({today_str}).", value="", inline=False)

    await sendEmmbed("hockey-news", news_articles)


    
async def sendEmmbed(channel_name: str, card: discord.Embed):
    channels = dbNewsBot.guilds[0].channels

    for channel in channels:
        if channel.name == channel_name:
                await channel.send(embed=card)
     

def injured_player_format(player):

    name = player["FirstName"]+player["LastName"]
    
    info = f'''
        Status:        {player["Status"]}
        Team:          {teams[player["Team"]]}
        Position:      {player["Position"]}
    '''
    return name, info

def news_article_format(article):
    title = article['Title']
    content = article['Content'][0:50]+"..."
    url=article['Url']

    unformatted_date = article['Updated'][:10].split("-")
    date_updated = "-".join([unformatted_date[1], unformatted_date[2], unformatted_date[0]])

    return title, content, url, date_updated
    
dbNewsBot.run('')    