import requests
import os
import lxml
from datetime import datetime, timezone
from lxml import html


def _load_tracker_site():
    tracker_site_ip = os.environ["TRACKER_SITE_URL"]

    try:
        response = requests.get(tracker_site_ip)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving content from {tracker_site_ip}: {e}")
        return None

def _get_hashable_key(entry):
    return (entry['Finder'],entry['Location'])

def _get_stats_hashable_key(entry):
    return (entry['Name'])

def _load_player_stats_site():
    tracker_site_ip = os.environ["STATS_SITE_URL"] #multiworld tracker site NOT sphere tracker

    try:
        response = requests.get(tracker_site_ip)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving content from {tracker_site_ip}: {e}")
        return None
    
#gets the all player stats into an array of dictionaries.
def get_player_stats():
    player_site_html = _load_player_stats_site()

    if not player_site_html:
        utc_now = datetime.now(timezone.utc)
        utc_timestamp_string = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"[{utc_timestamp_string}] [WARNING ] Failed to retrieve site!")
        return None
    
    table = html.fromstring(player_site_html).find(".//table[@id='checks-table']")
    columns = [col.text_content().strip() for col in table[0].xpath("tr/th")]
    footer_columns = ["Status", "Checks", "%", "LastActivity"]
    body = table[1]
    foot = table[2]
    activity_min = -1.0

    result = {}

    for entry in body:
        values = [cell.text_content().strip() for cell in entry]
        new_entry = (dict(zip(columns, values)))

        if (activity_min == -1.0):
            print(new_entry)
            activity_min = float(new_entry['LastActivity'])
        else:
            activity_min = min(activity_min, float(new_entry['LastActivity']))

        new_entry_hash = _get_stats_hashable_key(new_entry)

        result[new_entry_hash] = new_entry

    #custom footer logic
    values = [cell.text_content().strip() for cell in foot[0]]

    neededValues = []
    for i in range(2, len(values)):
        neededValues.append(values[i])
    
    new_entry = (dict(zip(footer_columns, neededValues)))
    new_entry['LastActivity'] = str(activity_min)
    result["Footer"] = new_entry

        
    return result

# gets the n most recent actions as an array of dictionaries.
def get_recent_archipelago_actions(n=-1):
    tracker_site_html = _load_tracker_site()

    if not tracker_site_html:
        utc_now = datetime.now(timezone.utc)
        utc_timestamp_string = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"[{utc_timestamp_string}] [WARNING ] Failed to retrieve site!")
        return None

    table = html.fromstring(tracker_site_html).find(".//table[@id='checks-table']")
    columns = [col.text_content().strip() for col in table[0].xpath("tr/th")]
    body = table[1]

    result = {}

    for entry in body:
        values = [cell.text_content().strip() for cell in entry]
        new_entry = (dict(zip(columns, values)))
        new_entry_hash = _get_hashable_key(new_entry)

        result[new_entry_hash] = new_entry

        if n != -1 and len(result) >= n:
            return result

    return result

def check_for_new_archipelago_actions(old_set, new_set):
    new_actions = {}
    for entry in new_set.values():
        entry_hash = _get_hashable_key(entry)

        if not (entry_hash in old_set):
            new_actions[entry_hash] = entry

    return new_actions
