import requests, requests_oauthlib, sys
import json

consumer_key = 'bXoAmDMk2DxTA9Wydr3oA48xU'
consumer_secret = 'p7tIJDaiXtN1mLUyNbTAFrhqhAbAcTPYIMOYf85Lzvfu9jIPVZ'
access_token = '824052439884120067-0BIPo9rjYeLhUpw8l03SKnHdcKfag4M'
access_secret = 'xVT0CTlbR0VuJQvPFh5BFqsVEBTg7v5feqjqCoz24Lm4O'


def verify_credentials(auth_obj):
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    response = requests.get(url, auth=auth_obj)
    return response.status_code == 200


def init_auth():
    auth_obj = requests_oauthlib.OAuth1(consumer_key,
                                        consumer_secret,
                                        access_token,
                                        access_secret)
    if verify_credentials(auth_obj):
        print('Validated credentials OK')
        return auth_obj
    else:
        print('Credentials validation failed')
        sys.exit(1)


def get_tweets_by_screen_name(since_id, auth_obj, screen_name):

    params = {'screen_name': screen_name,
              'count': 200,
              'since_id': since_id,
              'include_entities': 'true'}

    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

    response = requests.get(url, params=params, auth=auth_obj)
    response.raise_for_status()
    return json.loads(response.text)

def get_home_timeline(since_id, auth_obj):

    params = {'count': 200, 'since_id': since_id, 'include_entities': 'false'}
    url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'

    response = requests.get(url, params=params, auth=auth_obj)
    response.raise_for_status()
    return json.loads(response.text)


def get_mentions(since_id, auth_obj):
    params = {'count': 200, 'since_id': since_id, 'include_rts': 1, 'include_entities': 'false'}
    url = 'https://api.twitter.com/1.1/statuses/mentions_timeline.json'

    response = requests.get(url, params=params, auth=auth_obj)
    response.raise_for_status()
    return json.loads(response.text)


def send_dm(auth_obj):
    url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'
    payload = {"event":
                   {"type": "message_create",
                    "message_create":
                        {"target": {"recipient_id": "4027843701"},
                         "message_data": {"text": "Testing"}
                         }
                    }
               }
    response = requests.post(url, data=json.dumps(payload), auth=auth_obj)
    response.raise_for_status()
    return json.loads(response.text)

def list_dms(auth_obj):
    url = 'https://api.twitter.com/1.1/direct_messages/events/list.json'

    response = requests.get(url, auth=auth_obj)
    response.raise_for_status()
    r_json = json.loads(response.text)
    messages = [(e['id'], e['message_create']['message_data']['text'])
                for e in r_json['events']]
    return messages


def get_followers(auth_obj):
    url = 'https://api.twitter.com/1.1/followers/list.json'
    response = requests.get(url=url, auth = auth_obj)
    response.raise_for_status()
    r_json = json.loads(response.text)
    return [{'screen_name': r['screen_name'],
             'name': r['name'],
             'id': r['id']}
             for r in r_json['users']]

def get_friends(auth_obj):
    url = 'https://api.twitter.com/1.1/friends/list.json'
    response = requests.get(url=url, auth = auth_obj)
    response.raise_for_status()
    r_json = json.loads(response.text)
    return [{'screen_name': r['screen_name'],
             'name': r['name'],
             'id': r['id']}
             for r in r_json['users']]


def get_user_suggestions(auth_obj):
    url = 'https://api.twitter.com/1.1/users/suggestions.json'
    response = requests.get(url=url, auth=auth_obj)
    response.raise_for_status()
    r_json = json.loads(response.text)
    return [r['slug'] for r in r_json]

def get_users_by_slug(auth_obj, slug):
    url = 'https://api.twitter.com/1.1/users/suggestions/{}.json'.format(slug)

    response = requests.get(url=url, auth = auth_obj)
    response.raise_for_status()
    r_json = json.loads(response.text)
    return [{'screen_name': r['screen_name'],
             'name': r['name'],
             'id': r['id']}
             for r in r_json['users']]


if __name__ == '__main__':
    auth_obj = init_auth()
    since_id = 1
    #for tweet in get_mentions(since_id, auth_obj):
    #    print(tweet['text'])

    #for tweet in get_home_timeline(since_id=since_id, auth_obj=auth_obj):
    #    print(tweet)

    #for tweet in get_tweets_by_screen_name(since_id=1, auth_obj=auth_obj, screen_name='LewisClient2022'):
    #    print(tweet)
    #
    send_dm(auth_obj)
    #dms = list_dms(auth_obj)
    #print(dms)
    #followers = get_followers(auth_obj)
    #print(followers)
    # friends = get_friends(auth_obj)
    #
    # for friend in friends:
    #     print('@{}'.format(friend['screen_name']))

    # for id, msg in dms:
    #     print('id: {}    text: {}'.format(id, msg))

    # get_user_suggestions(auth_obj=auth_obj)
    # users = get_users_by_slug(auth_obj, 'sports')
    #
    # for user in users:
    #     print('@{}'.format(user['screen_name']))