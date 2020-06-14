import discord, os, arrow, io
import cassiopeia as cass
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as style

import secrets

# set up time arrow global
style.use('dark_background')

def flatten_list(l):
    flat_list = [item for sublist in l for item in sublist]
    return flat_list

def get_matches(summoner_name, begintime):
    smurf = cass.get_summoner(name=summoner_name)
    
    # make riot api call (all match histories)
    matches = cass.get_match_history(summoner=smurf, begin_time=begintime)

    # get durations in seconds, calculate total in hours
    durations, champions, wins, kills, deaths = [], [], [], [], []
    for match in matches:
        # get participant object from match
        p = [p for p in match.participants if p.summoner.name == summoner_name][0]

        # add participant info to table
        durations.append(match.duration.seconds)
        champions.append(p.champion.name)
        wins.append(p.team.win)
        kills.append(p.stats.kills)
        deaths.append(p.stats.deaths)

    df = pd.DataFrame(list(zip(durations, champions, wins, kills, deaths)), columns=['durations', 'champions', 'win', 'kills', 'deaths'])
    return df

# set up riot / discord API
cass.set_riot_api_key(secrets.riot_token)
cass.set_default_region("OCE")

discord_token = secrets.discord_token
client = discord.Client()

# bot command prefix
prefix = '&karg'

# bot events

# bot is connected and ready
@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'Connected to {guild.name} (id: {guild.id})')
    print(f'{client.user} is ready to go ;)')

# bot detects new message sent
@client.event
async def on_message(message):
    # don't recurse for my own messages! also don't check any message that doesn't have the prefix
    if (not message.content.startswith(prefix) or message.author.bot):
        return
    
    
    # get the arguments
    args = message.content.split(' ')
    args.pop(0)
    yesterday = arrow.utcnow().shift(hours=-24) # update what 'yesterday' is

    # get match history data for past 24 hours
    summoner_name = args[0]
    msg = await message.channel.send(f'Getting League data for {summoner_name}...')
    matches = get_matches(summoner_name, yesterday)
    
    smurf = cass.get_summoner(name=summoner_name)
    icon_url = smurf.profile_icon.url

    # create discord embed message
    colour = 0x00b2ff
    embed = discord.Embed(colour=colour, title=f'{summoner_name} data')
    embed.set_thumbnail(url=icon_url)

    await msg.delete()

    # print raw dataframe
    if len(args) < 2 or ('raw' in args):
        embed.add_field(name='Data', value=matches.to_string(), inline=False)

    if 'champ' in args:
        # generate pie chart of champion frequencies
        pie = matches.champions.value_counts().plot(kind='pie', figsize=(20,16), fontsize=26, legend=False)
        fig = pie.get_figure()

        # save pie chart as a raw image
        fig.savefig('graph.png', transparent=True, bbox_inches='tight')
        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        # export and send that image to discord
        image = discord.File(file, filename='graph.png')
        embed.set_image(url=f'attachment://graph.png')
        await message.channel.send(file=image, embed=embed)
        plt.clf()

        # don't send anything else
        return

    if 'games' in args:
        num_matches = len(matches)
        total_duration = round(sum(matches.durations) / 3600, 2)
        
        embed.add_field(name='Matches', value=num_matches, inline=True)
        embed.add_field(name='Total time (hours)', value=total_duration, inline=True)

    await message.channel.send(embed=embed)
        
# start up the bot
client.run(discord_token)