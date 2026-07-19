# This module stores data and functions associated with the "Burger King"
# feature. It allows people to put themselves in "burger king" so people
# may see when they are unable to progress.

import json
import os
import numpy as np

bkfilename = "patron_list.json"
current_burger_king_patrons = []

burger_king_messages = [
    "is waiting to order",
    "is waiting for their food",
    "is filling their drink",
    "is eating a burger",
    "is eating fries",
    "is sipping their drink",
    "is in the bathroom",
    "is sleeping on a table",
    "is sleeping in a booth",
    "is sleeping on the floor",
    "got burger king foot lettuce", # rare
    "got an onion ring in their fries", # rare
    "got a fry in their onion rings", # rare
    "is complaining to the manager", # rare
    "is staring wistfully out the window", # rare
    "is staring wistfully at a rat", # epic
    "is sipping on promethazine (they can't put down the cup)", # epic
    "is looking out the window at somebody coming in\n(doo-doo-doo-doo, doo-do-dooo-doo doo-doo-doo-doo-do-doo-doo)", # epic
    "is checking the clopen sign", # epic
    "thinks this might be a burger king for rats" # epic
]

# p_common = 0.7, p_rare = 0.2, p_epic = 0.1
burger_king_message_probs = [0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.04, 0.04, 0.04, 0.04, 0.04, 0.02, 0.02, 0.02, 0.02, 0.02]

def load_patrons_from_bk():
    global current_burger_king_patrons
    if(os.path.isfile(bkfilename)):
        with open(bkfilename, 'r') as file:
            current_burger_king_patrons = json.load(file)
    else:
        current_burger_king_patrons = []

def save_patrons_to_bk():
    file = open(bkfilename, 'w+')
    json.dump(current_burger_king_patrons, file)

async def go_to_burger_king(playerName, channel):
    if (playerName in current_burger_king_patrons):
        await channel.send(f"{playerName} is already at Burger King!")
    else:
        current_burger_king_patrons.append(playerName)
        await channel.send(f"{playerName} walks to Burger King..." )

async def leave_burger_king(playerName, channel):
    if (playerName in current_burger_king_patrons):
        current_burger_king_patrons.remove(playerName)
        await channel.send(f"{playerName} walks back home from Burger King")
    else:
        await channel.send(f"{playerName} isn't at Burger King!'" )
    save_patrons_to_bk()

async def list_burger_king_patrons(channel):
    print("running list BK command")

    # list all burger king patrons
    if (len(current_burger_king_patrons) == 0):
        await channel.send(':crab: Burger King is empty! :crab:')
    else:
        bkListStr = "```"
        for patron in current_burger_king_patrons:
            msg = np.random.choice(burger_king_messages, 1, p=burger_king_message_probs)
            bkListStr += f"\n* {patron} {msg[0]} "
        bkListStr += "```"
        await channel.send(bkListStr)


async def parse_bk_msg(message, args, argsLen):
    if (argsLen > 0 and args[0].lower() == "argo"):
        if (argsLen > 3):
            await send_usage_help_msg(message.channel)
            return

        match args[1].lower():
            case "gotobk":
                if (argsLen != 3):
                    await send_usage_help_msg(message.channel)
                    return

                playerName = args[2].lower().strip()

                await go_to_burger_king(playerName, message.channel)

            case "leavebk":
                if (argsLen != 3):
                    await send_usage_help_msg(message.channel)
                    return

                playerName = args[2].lower().strip()

                await leave_burger_king(playerName, message.channel)
            case "listbk":
                await list_burger_king_patrons(message.channel)
            case _:
                await send_usage_help_msg(message.channel)

async def send_usage_help_msg(channel):
    await channel.send("""Unrecognized command. Usage:
!argo notify add [ItemName] [PlayerName]
!argo notify remove [ItemName] [PlayerName]
!argo notify list
!argo gotobk [PlayerName]
!argo leavebk [PlayerName]
!argo listbk
!argo stats
!argo stats [PlayerName]""")