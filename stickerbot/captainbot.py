import discord
import json
from discord.ext import commands
import requests
from io import BytesIO
import difflib

from similar import is_similar

client = discord.Client()
bot = commands.Bot(command_prefix=[commands.bot.when_mentioned,'\u200b'], case_insensitive = True)
#json file for data {all : {name:[url, hash]}, filters: {filter: names}}
emojifile = 'emojis.txt_hashes.json'



#check for permission
async def checkrole(msg, roles = [603823225218138113,576027568822812692,900326932665749544]):
    if [y.id for y in msg.author.roles if y.id in roles]:
        return True
    else:
        await msg.reply(content ='nice try, no privilege')
        return False

#returns a url from json of emoji Name
def emojis(name):
    with open(emojifile) as json_file:
        data = json.load(json_file)
    data['filters']['favourites'][name] += 1
    with open(emojifile, 'w') as json_file:
        json.dump(data, json_file)
    
    return data['all'][name][0]

#list emoji page and takes filter returns an embed with emojis names as fields
def emojilist(page, filter = None):
    emojilist.page = page
    listembed = discord.Embed(title = 'Emoji List', color=0x949597)
    listembed.set_thumbnail(url ='https://cdn.discordapp.com/attachments/899467150056640546/901029776033218570/Layer_0.png')
    with open(emojifile) as json_file:
        filterlist = (json.load(json_file))

    #if favourite exctract max numbers
    if filter == 'favourites':
        elist = sorted(filterlist['filters']['favourites'].keys(), key = lambda x : filterlist['filters']['favourites'][x], reverse= True)[:25]
        
    elif filter == None:
        elist = list(filterlist['all'].keys())
        elist.sort(key = str.lower)
    else:
        elist = filterlist['filters'][filter]

    pages = -(-len(elist)//25)
    listembed.set_footer(text = '{0}/{1}'.format(page, pages) )
    for i in range((page - 1)*25,len(elist)):
            listembed.add_field(name=(elist[i]), value = '\u200b' , inline=True)
    return listembed

#get page numbers
def pages(filter = None):
    with open(emojifile) as json_file:
        filterlist = (json.load(json_file))
    if filter == None:
        
        elist = list(filterlist['all'].keys())
        elist.sort(key = str.lower)
    else:
        elist = filterlist['filters'][filter]
    return -(-len(elist)//25)

#remove name from json file and returns url
def removeemoji(name):
    with open(emojifile) as json_file:
        filterlist = (json.load(json_file))

    for filter in filterlist['filters']:
        if name in filterlist['filters'][filter]:
            if isinstance(filterlist['filters'][filter], list):
                filterlist['filters'][filter].remove(name)
            else:
                del filterlist['filters'][filter][name]
    content = filterlist['all'][name]
    del filterlist['all'][name]
    with open(emojifile, 'w') as outfile:
        json.dump(filterlist, outfile)
    return content

#adds emoji to the json file after checking the hash similarity
async def addemoji(url,message):
    if url.lower().endswith(('.png', '.gif','.webp','.jpg','.jpeg')):
        response = requests.get(url)
        imghash = is_similar(BytesIO(response.content),cutoff=9)
        view = confirm()
        if imghash[0]:
            try:
                embed = discord.Embed(title=f"this looks similar to ;{imghash[2]}, you still wanna add it?")
                embed.set_image(url = imghash[0])
                await message.reply(embed = embed,  view = view)
                await view.wait()
            except sameImageError:
                return
        msgb = await message.reply('reply to this message with the name')
        try:
            msg = await bot.wait_for('message', check = lambda i : i.reference.message_id == msgb.id)
            if not await checkrole(msg) : return
            await msgb.edit(content = 'choose emoji filter',  view = chooseFilter(msg.content.lower(),[url, imghash[1]]))
        except AttributeError:
            await msgb.edit('aborted no reply')
    else:
        await message.reply('only images and GIFs')
    
#renames emoji from file and json
async def renameemoji(message):
    name = message.content.split(' ')[-2]
    newname = message.content.split(' ')[-1]
    content = removeemoji(name)
    message.content = newname
    return await message.channel.send(content = 'choose emoji filter',  view = chooseFilter(newname, content))



#VIEWS VIEW VIEWS
# view which initialize component part of the list function
class menu(discord.ui.View):
    def __init__(self, page, filter = None):
        super().__init__(timeout=None)
        self.page = page
        self.filter = filter

    options = [
            discord.SelectOption(label='all', description='display all emotes'),
            discord.SelectOption(label='homebrew', description='our homebrewn emotes', emoji='🏠'),
            discord.SelectOption(label='internet', description='emotes from the net', emoji= '🌐' ),
            discord.SelectOption(label='favourites', description='most used emojis', emoji= '⭐' )
        ]
    @discord.ui.select(placeholder='choose filter to limit results', min_values=1, max_values=1, options=options)
    async def dropdown(self, select: discord.ui.select, interaction: discord.Interaction):
        if select.values[0] == 'all':
            self.filter = None
        else:
            self.filter = select.values[0]
        await interaction.response.edit_message(embed = emojilist(1, filter=self.filter), view = menu(1,self.filter))

    @discord.ui.button(label='prev', style=discord.ButtonStyle.grey)
    async def prev(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.page > 1:
            page = (self.page - 1)
        else:
            page = self.page
        await interaction.response.edit_message(embed = emojilist(page, filter=self.filter), view = menu(page,self.filter))
        
    @discord.ui.button(label='next', style=discord.ButtonStyle.grey)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.page < pages(self.filter) and not self.filter == 'favourites':
            page = (self.page + 1) 
        else:
            page = self.page
        await interaction.response.edit_message(embed = emojilist(page,filter=self.filter), view = menu(page,self.filter))

# a view that adds name to json dict from a list
class chooseFilter(discord.ui.View):
    def __init__(self, name, content):
        super().__init__()
        self.name = name
        self.content = content

    options = [
            discord.SelectOption(label='homebrew', description='our homebrewn emotes', emoji='🏠'),
            discord.SelectOption(label='internet', description='emotes from the net', emoji= '🌐' )
        ]
    @discord.ui.select(placeholder='Set filter', min_values=1, max_values=1, options=options)
    async def dropdown(self, select: discord.ui.select, interaction: discord.Interaction):
        with open(emojifile) as json_file:
            filterlist = (json.load(json_file))

        filterlist['all'][self.name] = self.content
        filterlist['filters']['favourites'][self.name] = 0

        if not (self.name in filterlist['filters'][select.values[0]]):
            filterlist['filters'][select.values[0]].append(self.name)
            filterlist['filters'][select.values[0]].sort(key = str.lower)
        with open(emojifile, 'w') as outfile:
            json.dump(filterlist, outfile)
        await interaction.response.edit_message(content='Completed!', view = self.clear_items())


class sameImageError(Exception):
    pass
#confirm to bypass the sameImageError or abort
class confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='YES', style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        self.stop()
    @discord.ui.button(label='NO', style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.edit(content='check the list next time', embed=None, view = self.clear_items())
        raise sameImageError

#confirm suggested  auto correction to send emoji or abort
class autocorrect(discord.ui.View):
    def __init__(self, name):
        super().__init__(timeout=None)
        self.name = name

    @discord.ui.button(label='YES', style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.edit(content=emojis(self.name), view = self.clear_items())

    @discord.ui.button(label='NO', style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        


#main events
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    message.content = message.content.lower()
    if message.author == bot.user:
            return
    
    #main command to fetch emoji
    if ";" in message.content:
        msg = message.content.split()
        for word in msg:
            if word.startswith(';'):
                name = word.strip(';')
                break
        try:
            await message.channel.send(content = emojis(name))
        except KeyError:
            with open(emojifile) as file:
                emojislist = (json.load(file))['all']
            match = difflib.get_close_matches(name, emojislist.keys(), n=1, cutoff=0.6)
            if match:
                await message.channel.send(content = f'did you mean ;{match[0]} ?', view = autocorrect(match[0]))
            else:
                await message.channel.send(content ='https://cdn.discordapp.com/attachments/901393528364621865/901616614812811274/npcmeme.png', delete_after=1)
    #checks if mentioned
    elif bot.user.mentioned_in(message):
        #list command
        if message.content.startswith('list') or message.content.endswith('list'):
            await message.channel.send(view = menu(1), embed = emojilist(1))
        #add command
        elif message.content.startswith('add') or message.content.endswith('add'):
            
            # Added this line to fetch reply content if it exists
            if message.reference:
                message = await message.channel.fetch_message(message.reference.message_id)

            if len(message.attachments) == 0:
                await message.reply(content ='no attachment included')
            else:
                for attachment in message.attachments:
                    await addemoji(attachment.url,message)     
        #remove command
        elif 'remove' in message.content.split(' '):
            if await checkrole(message):
                name = message.content.split(' ')[-1]
                try:
                    removeemoji(name)
                    await message.reply(content = 'get it outta here')
                except KeyError:
                    await message.channel.send(content ='https://cdn.discordapp.com/attachments/901393528364621865/901616614812811274/npcmeme.png', delete_after=1)
            else:
                await message.reply(content ='nice try, no privilege')
        #rename command
        elif 'rename' in message.content.split(' '):
            if await checkrole(message):
                try:
                    msg = await renameemoji(message)
                    await msg.edit(content = 'its a dumb name either way')
                except KeyError:
                    await message.channel.send(content ='https://cdn.discordapp.com/attachments/901393528364621865/901616614812811274/npcmeme.png', delete_after=1)
        #pleasantries
        elif message.content.startswith('hello') or message.content.endswith('hello'):
            await message.reply(content ='Hi!') 
        elif message.author.id == 263306098512101376:
            await message.reply(content = 'lol')
TOKEN = ""
bot.run(TOKEN)
