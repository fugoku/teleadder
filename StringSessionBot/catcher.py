from itertools import islice
from datetime import datetime, timedelta, timezone
import time
import random
# from config import db
from telethon.tl.types import ChannelParticipantsAdmins

users = []




async def runner(user, out_group, client):
    try:
        invite = await client(InviteToChannelRequest(
            out_group,
            [user]
        ))
        username = user.username
        print(f"RunningMan added {username}")
    except PeerFloodError:
        print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        return "Flooded"

    except UserPrivacyRestrictedError:
        print("The user's privacy settings do not allow you to do this. Skipping.")
        return "Restricted"

    except ChatWriteForbiddenError:
        print("The session is not an Admin and cannot add user, please make Admin and try again")
        return "NotAdmin"

    except UserNotMutualContactError:
        print("The user isn't a mutal contact")
        return False

    except:
        traceback.print_exc()
        print("Unexpected Error")
    return "Good"



async def catcher(source_entity, target_entity, client, last_user_id):
    max_add = 50
    number = 0
    offset = 0
    index_former = index
    group_admin = await client.get_participants(group, filter=ChannelParticipantsAdmins)
    async for user in client.iter_participants(group):
        if index_former > offset:
            offset = offset + 1
            pass
        else:
            index = index + 1
            # db.update({'index': index})

            user_legible = check_status(user, group_admin)
            if user_legible:
                run = await runner(user, out_group, client)

                if run == "Good":
                    number += 1
                    time.sleep(random.randint(1, 5))

                if number >= max_add:
                    print(f"Reached {max_add} cooling down")
                    cooldown = datetime.now() + timedelta(minutes=30)
                    break
                if run == "Flooded":
                    print(f"Reached max capacity Flooded")
                    break
                if run == "NotAdmin":
                    print(f"Not an Admin")
                    break
            else:
                pass
    # index = index + number
    # db.update({'index': index})
    print(f"Added {number}")
    return index


async def groupGetter(group, client):
    group = await client.get_entity(group)
    return group


def check_status(user, group_admin):
    "This checks to see that the user entity meets all the criteria before being added"
    if user.bot:
        return False
    if user in group_admin:
        return False
    if user.deleted:
        return False

    try:
        inactivity_date = datetime.now(timezone.utc) - timedelta(days=15)
        if user.status.was_online > inactivity_date:
            # check if user was online in last 5 months
            return True
        else:
            return False
    except AttributeError:
        if user.participant.date > inactivity_date:
            return True
        else:
            return False

