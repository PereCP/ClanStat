import discord
import json
import requests
import threading
from time import sleep
import asyncio

discord_token = ''

global battle, serv
battle = "https://api.battlemetrics.com"
serv = 0

global client
client = discord.Client()

class Player:
    name = ""
    ide = 0
    online = False
    def __init__(self, nm, ides):
        self.name = nm
        self.ide = ides
        self.online = True

global players, esperant, ready
players = []
esperant = False
ready = False

async def init_players():
    global players
    players = []
    params = {"include": "player"}
    r = requests.get('{0}/servers/{1}'.format(battle, serv), params=params)
    if not r.ok:
        return
    else:
        r = r.json()
        for k in r['included']:
            players.append(Player(k['attributes']['name'], k['attributes']['id']))
        await ordenarp()

async def print_players(chan, sayo, battleid):
    global players
    i = 0
    output = ""
    if (not sayo) or battleid:
        output += "```\n"
        for k in players:
            if i % 100 == 0 and i != 0:
                output += "```"
                await chan.send(output)
                output = "```"
            if sayo:
                color = ""
                if k.online:
                    color = "ONLINE"
                else:
                    color = "OFFLINE"
                if battleid:
                    color += " | ID: {}".format(k.ide)
                output += "[{0}]: {1} | {2}\n".format(i, k.name, color)
            else:
                output += "[{0}]: {1}\n".format(i, k.name)
            i += 1
        output += "```"
    else:
        on = []
        off = []
        for k in players:
            if k.online:
                on.append(k.name)
            else:
                off.append(k.name)
        if len(on) != 0:
            output += "```\n**ONLINE**\n"
            for k in on:
                output += "{}\n".format(k)
            output += "```\n"
        if len(off) != 0:
            output += "```\n**OFFLINE**\n"
            for k in off:
                output += "{}\n".format(k)
            output += "```\n"
    await chan.send(output)

async def print_status(chan):
    global players
    for k in players:
        output = "```"
        if k.online:
            output += "CSS\n {}".format(k.name)
            output += " ONLINE\n```"
        else:
            output += "diff\n {}".format(k.name)
            output += " OFFLINE\n```"
        await chan.send(output)

async def update_players(chan, manual):
    global players
    if len(players) > 20 and not manual:
        return
    for p in players:
        params = {"include": "server"}
        r = requests.get('{0}/players/{1}'.format(battle, p.ide), params=params)
        if (not r.ok) and manual:
            await chan.send("Petición de actualizar jugador {0} denegada. Razón: {1}".format(p.name, r.reason))
        elif r.ok:
            r = r.json()
            status = False
            for k in r["included"]:
                if (k["id"] == serv):
                    status = k["meta"]["online"]
                    break
            if status != p.online:
                p.online = status
                if status:
                    await chan.send("EL JUGADOR {0} AHORA ESTÁ ONLINE!".format(p.name))
                else:
                    await chan.send("EL JUGADOR {0} SE HA DESCONECTADO!".format(p.name))        
    return

async def add_manual(idn, out):
    global players, chan
    r = requests.get('{0}/players/{1}'.format(battle, idn))
    if not r.ok:
        await chan.send("Error al introducir jugador. ({})".format(r.reason))
    else:
        r = r.json()
        p = Player(r["data"]["attributes"]["name"], idn)
        p.online = True
        players.append(p)
        await ordenarp()
        if out:
            await chan.send("Jugador '{}' añadido.".format(p.name))

async def extract(s):
    global players, serv
    players = []
    sel = s[0].split(' ')
    serv = sel[1]
    print(serv)
    s = s[1:]
    for k in s:
        await add_manual(int(k), False)

async def ordenarp():
    global players
    players.sort(key=lambda player: player.name)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global chan, battle, serv, esperant, ready
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        chan = message.channel
        if message.content.startswith('$init'):
            ready = False
            s = message.content.split(' ')
            if (len(s) <= 1):
                await message.channel.send("Introduce correctamente el ID del servidor. ($init ID)")
            else:
                print(s[1])
                serv = s[1]
                r = requests.get('{}/servers/{}'.format(battle, serv))
                esperant = r.ok
                if not esperant:
                    await message.channel.send("ID de servidor no válido.")
                else:
                    await init_players()
                    await message.channel.send("LISTA JUGADORES:")
                    await print_players(message.channel, False, False)
                    await message.channel.send("Introduce los IDs separados por comas (ejemplo: $1,2,4). O '$skip' para saltarlo.")
                return
            return

        if esperant:
            if message.content != "$skip":
                global players
                defplayers = []
                st = message.content
                if (len(st) > 0):
                  st = st[1:]
                s = st.split(',')
                for k in s:
                    if int(k) >= 0 and int(k) < len(players):
                        defplayers.append(players[int(k)])
                players = defplayers
                await ordenarp()
                await message.channel.send("Jugadores seleccionados:")
                await print_players(message.channel, False, False)
            else:
                players = []
                await message.channel.send("Selección automática omitida.")
            esperant = False
            ready = True
            return


        if ready:        
            if message.content.startswith('$a'):
                await update_players(message.channel, True)
                await message.channel.send("Actualizado")
                await print_players(message.channel, True, False)

            elif message.content.startswith("$manual"):
                s = message.content.split(' ')
                await add_manual(int(s[1]), True)
            
            elif message.content.startswith("$list"):
                await message.channel.send("Jugadores seleccionados:")
                await print_players(message.channel, True, True)

            elif message.content.startswith("$borrar"):
                s = message.content.split(' ')
                if (len(s) != 2):
                    await message.channel.send("Introduce correctamente el ID del jugador a borrar. ($borrar ID).")
                else:
                    nom = players[int(s[1])].name
                    del players[int(s[1])]
                    await message.channel.send("Jugador {} borrado correctamente.".format(nom))
            
            elif message.content.startswith("$extraer"):
                output = "```\n$leer;SERV: {0};".format(serv)
                for k in players:
                    output += "{};".format(k.ide)
                output += "```\n"
                await message.channel.send(output)
                
        if message.content.startswith("$leer"):
            s = message.content.split(";")
            s = s[1:len(s)-1]
            await extract(s)
            esperant = False
            ready = True
            await message.channel.send("Configuración leída correctamente.")
                
            
    
async def updater():
    while True:
        global ready
        if ready:
            global loopprinc
            asyncio.run_coroutine_threadsafe(update_players(chan, False), loopprinc)
        sleep(30)

def proc():
    asyncio.run(updater())

global loopprinc
try:
    loopprinc = asyncio.get_event_loop()
except RuntimeError:
    loopprinc = asyncio.new_event_loop()
    asyncio.set_event_loop(loopprinc)

th = threading.Thread(target=proc)
th.start()

client.run(discord_token)