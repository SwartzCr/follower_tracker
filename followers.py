from twython import Twython
from datetime import datetime
import json

def auth():
    with open("access.json", 'r') as f:
        db = json.load(f)
    return Twython(db["API_Key"], db["API_Secret"], db["Access_Token"], db["Access_Token_Secret"]), db["username"]

def load_followers():
    with open("followers.json", 'r') as f:
        out = json.load(f)
    return out

def save_followers(followers):
    with open("followers.json", 'w') as f:
        json.dump(followers, f)

def log(lost_followers, last_tweet):
    date = datetime.now().strftime("%m-%d-%Y")
    time = datetime.now().strftime("%I:%M%p")
    try:
        with open(date+"log.txt", 'r') as f:
            my_log = f.read()
    except:
        my_log = ""
    out = time + "\n"
    out += "your last tweet was: " + last_tweet + "\n"
    out += "you lost: "  + ", ".join(lost_followers) + "\n"
    out += "\n"
    out += my_log
    with open(date+"log.txt", 'w') as f:
        f.write(out)

def diff(old_followers, cur_followers):
    return [follower for follower in cur_followers.difference(old_followers)]


def main():
    twitter, user_id = auth()
    cursor_str = "-1"
    cur_followers = []
    while cursor_str != "0":
        followers_list = twitter.get_followers_ids(user_id=user_id, cursor=cursor_str)
        cur_followers += followers_list['ids']
        cursor_str = followers_list['next_cursor_str']
    cur_followers_set = set(cur_followers)
    old_followers_set = set(load_followers())
    save_followers(cur_followers)
    lost_followers = diff(old_followers_set, cur_followers_set)
    if len(lost_followers) > 0:
        last_tweet = twitter.get_user_timeline(user_id=user_id, count=1)[0]['text']
        lost_followers_names = [twitter.lookup_user(user_id=user)[0]['screen_name'] for user in lost_followers]
        log(lost_followers_names, last_tweet)

#run on cron every few minutes
if __name__ == "__main__":
    main()
