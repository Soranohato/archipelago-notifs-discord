# This module stores important data and functions associated with
# the "notifications" feature. This feature allows users to subscribe
# to notifications on specific items and then receive pings when
# said item is obtained by another player.

from collections import namedtuple
import json
import os
import numpy as np
from datetime import datetime, timezone

#custom module import
from archipelago_site import get_player_stats

filename = "saved_notifs.json"
current_notifications = []

Notification = namedtuple('Notification', ['userIDs', 'usernames', 'itemName', "playerName"])

def load_notifs_from_file():
    global current_notifications

    if(os.path.isfile(filename)):
        with open(filename, 'r') as file:
            current_notifications = json.load(file)
    else:
        current_notifications = []

def save_notifs_to_file():
    file = open(filename, 'w+')
    json.dump(current_notifications, file)

def format_hours_minutes(last_activity):
    last_activity_hours = int(float(last_activity) / 60 / 60)
    last_activity_minutes_percent = (float(last_activity) / 60 / 60) % 1
    last_activity_minutes = int(last_activity_minutes_percent * 60)
    return f"{last_activity_hours}:{last_activity_minutes}"

async def add_notification(user, itemName, playerName, channel):
    userID = user.id
    username = user.name

    existingNotifIndex = -1
    for i, notification in enumerate(current_notifications):
        if (notification.itemName == itemName and notification.playerName == playerName):
            existingNotifIndex = i
            break

    if existingNotifIndex != -1:
        existingNotif = current_notifications[existingNotifIndex]

        if userID in existingNotif.userIDs:
            await channel.send("You are already signed up for this notification!")
            return

        existingNotif.userIDs.append(userID)
        existingNotif.usernames.append(username)

        await channel.send("Notification added!")
    else:
        current_notifications.append(Notification([userID], [username], itemName, playerName))
        await channel.send("Notification added!")

    save_notifs_to_file()

async def remove_notification(user, itemName, playerName, channel=None, uid=-1, uname=""):

    # allow for direct discord.py user object or specify uid/uname manually
    if user:
        userID = user.id
        username = user.name
    else:
        userID = uid
        username = uname

    notifIndex = -1
    for index, notification in enumerate(current_notifications):
        if (notification.itemName == itemName and notification.playerName == playerName):
            notifIndex = index
            break

    if (notifIndex == -1):
        msg = "This notification does not exist!"
        if channel:
            await channel.send(msg)
        else:
            utc_now = datetime.now(timezone.utc)
            utc_timestamp_string = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{utc_timestamp_string}] {msg}")
    else:
        notifObj = current_notifications[notifIndex]

        if not userID in notifObj.userIDs:
            msg = f"Cannot remove: {username} is not signed up for this notification!"
            if channel:
                await channel.send(msg)
            else:
                utc_now = datetime.now(timezone.utc)
                utc_timestamp_string = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"[{utc_timestamp_string}] {msg}")
            return

        # remove the entire notification object or just remove that user (if they are not the only one subscribed)
        if len(notifObj.usernames) == 1:
            current_notifications.pop(notifIndex)
        else:
            notifObj.userIDs.remove(userID)
            notifObj.usernames.remove(username)

        msg = "Notification removed!"
        if channel:
            await channel.send(msg)
        else:
            utc_now = datetime.now(timezone.utc)
            utc_timestamp_string = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{utc_timestamp_string}] {msg}")
    save_notifs_to_file()

async def list_notifications(channel):
    print("running list command")

    # list all active notifications
    if (len(current_notifications) == 0):
        await channel.send('There are no active notifications!')
    else:
        notifsListStr = "Active notifications:\n```"
        for notification in current_notifications:
            notifsListStr += f"\n* {notification.itemName} ==> {notification.playerName} (notifies "

            for i in range(len(notification.usernames)):
                if i != 0:
                    notifsListStr += ", "

                notifsListStr += f"{notification.usernames[i]}"
            notifsListStr += ")"
        notifsListStr += "```"
        await channel.send(notifsListStr)

async def send_stats_msg(message, channel):
    await channel.send(message)

async def parse_notif_msg(message, args, argsLen):
    global current_notifications

    if (argsLen > 0 and args[0].lower() == "argo"):
        if (argsLen == 1 or argsLen == 2):
            await send_usage_help_msg(message.channel)
            return

        match args[2].lower():
            case "add":
                # create a new notification (if it does not already exist)

                if (argsLen != 5):
                    await send_usage_help_msg(message.channel)
                    return

                user = message.author
                itemName = args[3].lower().strip()
                playerName = args[4].lower().strip()

                await add_notification(user,itemName,playerName,message.channel)

            case "remove":
                # remove an existing notification (if a matching one exists)
                if (argsLen != 5):
                    await send_usage_help_msg(message.channel)
                    return

                itemName = args[3].lower().strip()
                playerName = args[4].lower().strip()

                await remove_notification(message.author, itemName, playerName, message.channel)

            case "list":
                await list_notifications(message.channel)
            case "stats":
                if (argsLen != 3 and argsLen != 2):
                    await send_usage_help_msg(message.channel)
                    return
                
                statsTable = get_player_stats()

                if (argsLen == 2):
                    complete = statsTable['Footer']
                    last_activity = format_hours_minutes(complete['LastActivity'])
                    msg_content = f"# ***Overall Stats***\n**Games Complete: **{complete['Status']}\n**Checks complete: **{complete['Checks']}\n**Percent Complete: **{complete['%']}\n**Last Activity: **{last_activity}"
                    await send_stats_msg(msg_content, message.channel)
                    return

                playerName = args[2].strip()

                if(not playerName in statsTable):
                    await message.channel.send(f"{playerName} does not exist in this Archipelago!")
                else:
                    player_stats = statsTable[playerName]
                    last_activity = format_hours_minutes(player_stats['LastActivity'])
                    msg_content = f"# ***{playerName}'s Stats***\n**Game: **{player_stats['Game']}\n**Status: **{player_stats['Status']}\n**Checks complete: **{player_stats['Checks']}\n**Percent Complete: **{player_stats['&percnt;']}\n**Last Activity: **{last_activity}"
                    await send_stats_msg(msg_content, message.channel)
 
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
