# This module stores functions associated with the "Stats" feature. This
# feature allows a player to look up a player's stats or the overall stats
# of the current archipelago.

#custom module import
from archipelago_site import get_player_stats

def format_hours_minutes(last_activity):
    last_activity_hours = int(float(last_activity) / 60 / 60)
    last_activity_minutes_percent = (float(last_activity) / 60 / 60) % 1
    last_activity_minutes = int(last_activity_minutes_percent * 60)
    return f"{last_activity_hours}:{last_activity_minutes}"

async def send_stats_msg(message, channel):
    await channel.send(message)

async def parse_stats_msg(message, args, argsLen):
    if (argsLen > 0 and args[0].lower() == "argo"):
        if (argsLen > 3):
            await send_usage_help_msg(message.channel)
            return

        match args[1].lower():
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