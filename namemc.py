'''
LOW BUDGET TRELLO:

DONE:
 - !check -- check the availility of a certain name

THINGS TO DO:
 - !list -- get the names with a max length
 - !history -- get history of people with a certain name
 - !remind -- set up reminder for when a specific name becomes available
'''

# bot.py
import os
import random
import requests
from bs4 import BeautifulSoup

from discord.ext import commands
from dotenv import load_dotenv
import dateutil.parser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

url = 'https://namemc.com/search?q='
url2 = 'https://namemc.com/minecraft-names?sort=asc&length_op=le&length=%s&lang=&searches=%s'

format = '''NAME                     SEARCHES/MONTH
DATE OF AVAILIBILITY
--------------------------------------'''

names = []
urls = []

bot = commands.Bot(command_prefix='!')

def get_name_status(name):
    request = requests.get(url + name).text
    soup = BeautifulSoup(request, 'html.parser')

    if 'availability-time' in request:
        for time in soup.find_all('time'):
            if time['id'] == 'availability-time':
                d = dateutil.parser.parse(time['datetime'])
                formatted = d.strftime('%m/%d/%y, %H:%M:%S')

                for searches in soup.find_all('div', class_='tabular'):
                    second = searches.contents[0]

                return f'Time of Availability: {formatted}, Searches: {second}'
    else:
        for tag in soup.find_all('meta'):
            if 'name="description"' in str(tag):
                return tag['content']

def get_names(maxlength, search):
    request = requests.get(url2 % (maxlength, search)).text
    soup = BeautifulSoup(request, 'html.parser')

    table = soup.find_all('div', class_='card-body p-0')[0]
    for tag in table.find_all('div', class_='row no-gutters py-1 px-3 border-top'):
        x = []
        for tag2 in tag:
            if tag2 != '\n':
                if str(tag2.contents)[:2] == '<a':
                    print('hkljfdshglk')
                    contents = tag2.contents
                    x.append(str(contents)[contents.index('>'):-5])
                else:
                    x.append(tag2.contents)
        print(x)
        print()

# !history <name>
def name_history(name):
    global names, urls
    format = 'Naming history:\n'

    request = requests.get('https://namemc.com/search?q=' + name).text
    soup = BeautifulSoup(request, 'html.parser')

    names = soup.find_all('h3', class_='mb-0')
    urls = soup.find_all('div', class_='card-header py-0')

    if not names:
        return format + 'Nobody has ever had this name!'

    for index, name in enumerate(names):
        format += f'{index+1}. {name.contents[0]}'

        if index != len(names) - 1:
            format += '\n'

    format += '\n\nUse !select <number> to select a specific person'

    return format

# !select <number>
def select(number):
    try:
        tag = urls[int(number) - 1]
    except:
        return 'Invalid number!'

    format = f'History for {names[int(number) - 1].contents[0]}:\n'

    subtag = tag.findChildren('a', recursive=False)[0]
    link = subtag['href']

    request = requests.get('https://namemc.com' + link).text
    soup = BeautifulSoup(request, 'html.parser')

    people = soup.find_all('div', class_='col order-lg-1 col-lg-4 text-nowrap')
    times = soup.find_all('time')

    knames = []
    thimes = []

    for person in people:
        knames.append(person.findChildren('a', recursive=False)[0].contents[0])

    for time in times:
        thimes.append(time.contents[0])

    for index, kname in enumerate(knames):
        if index != len(knames) - 1:
            format += f'{kname} -- {dateutil.parser.parse(thimes[index]).strftime("%m/%d/%y, %H:%M:%S")}\n'
        else:
            format += f'{kname} -- Unknown (account creation)\n'

    return format

@bot.command(name='check', help='Checks availability of name')
async def available(ctx, name):
    resp = get_name_status(name)
    await ctx.send(resp)

@bot.command(name='list', help='Lists names with specified max length and popularity')
async def list_em(ctx, maxlength, search):
    resp = get_names(maxlength, search)
    await ctx.send(resp)

@bot.command(name='history', help='Returns the naming history of a certain name')
async def history(ctx, name):
    resp = name_history(name)
    await ctx.send(resp)

@bot.command(name='select', help='In response to !history, tells the history of a specific user you selected')
async def personjfhklfdsjhls(ctx, number):
    resp = select(number)
    await ctx.send(resp)

bot.run(TOKEN)
