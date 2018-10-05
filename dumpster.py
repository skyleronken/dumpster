import tweepy
from tweepy import OAuthHandler
import requests
import time
import re
from IPy import IP

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''


def check_cisco_config(status):
    short_link = status.text.split()[0]
    response = requests.get(short_link)
    content = response.text
    created = status.created_at

    if "This page has been removed!" in content:
        return

    ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', content)
    if len(ips) > 0:
        pub_ips = []
        for ip in ips:
            ip_obj = IP(ip)
            ip_type = ip_obj.iptype()
            if ip[0:3] == '255':
                continue
            if ip_type == "PRIVATE" or ip_type == "LOOPBACK":
                continue
            else:
                pub_ips.append(ip)

        if len(pub_ips) > 0:
            #print(content)
            print("Found Public IPs in {} created at {}: {}".format(short_link, created, pub_ips))

    else:
        return


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("Waiting due to rate limit...")
            time.sleep(15 * 60)
        except StopIteration:
            print("End of iteration")
            break


if __name__ == "__main__":

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth)

    status_count = 0
    for status in limit_handled(tweepy.Cursor(api.user_timeline, id="dumpmon").items()):
        status_count += 1
        if "cisco" in status.text:
            check_cisco_config(status)

    print("Parsed {} Tweets".format(status_count))
