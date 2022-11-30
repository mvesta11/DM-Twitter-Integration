import requests, requests_oauthlib
import json

class TwitterDMClient:
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_secret):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret = access_secret

    def verify_credentials(self, auth_obj):
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        response = requests.get(url, auth=auth_obj)
        return response.status_code == 200


    def init_auth(self):
        auth_obj = requests_oauthlib.OAuth1(self.consumer_key,
                                            self.consumer_secret,
                                            self.access_token,
                                            self.access_secret)

        if self.verify_credentials(auth_obj):
            self.auth_obj = auth_obj
        else:
            raise Exception('verify your API keys')

    def list_dms(self):
        url = 'https://api.twitter.com/1.1/direct_messages/events/list.json'

        response = requests.get(url, auth=self.auth_obj)
        response.raise_for_status()
        r_json = json.loads(response.text)
        messages = [(e['id'], e['message_create']['message_data']['text'])
                    for e in r_json['events']]
        return messages