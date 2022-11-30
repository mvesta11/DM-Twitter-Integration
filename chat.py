import sys
import aioconsole
import asyncio
import click
from server.chat_server import ChatServer
from client.chat_client import (
    ChatClient,
    NotConnectedError,
    LoginConflictError,
    LoginError
)
from twitter.blk_client import TwitterDMClient

consumer_key = 'bXoAmDMk2DxTA9Wydr3oA48xU'
consumer_secret = 'p7tIJDaiXtN1mLUyNbTAFrhqhAbAcTPYIMOYf85Lzvfu9jIPVZ'
access_token = '824052439884120067-0BIPo9rjYeLhUpw8l03SKnHdcKfag4M'
access_secret = 'xVT0CTlbR0VuJQvPFh5BFqsVEBTg7v5feqjqCoz24Lm4O'


async def display_msgs(chat_client):
    while True:
        msg = await chat_client.get_user_msg()
        print('\n\n\t\tRECEIVED MESSAGE: {}'.format(msg))


async def handle_user_input(chat_client, twitter_client, loop):
    while True:
        print('\n\n')
        print('< 1 > closes connection and quits')
        print('< 2 > list logged-in users')
        print('< 3 > login')
        print('< 4 > list rooms')
        print('< 5 > post message to a room')
        print('< 6 > get twitter direct messages')
        print('< 7 > list twitter followers')
        print('< 8 > send a Twitter DM')
        print('\tchoice: ', end='', flush=True)

        command = await aioconsole.ainput()
        if command == '1':
            # disconnect
            try:
                chat_client.disconnect()
                print('disconnected')
                loop.stop()
            except NotConnectedError:
                print('client is not connected ...')
            except Exception as e:
                print('error disconnecting {}'.format(e))

        elif command == '2':  # list registered users
            users = await chat_client.lru()
            print('logged-in users: {}'.format(', '.join(users)))

        elif command == '3':
            login_name = await aioconsole.ainput('enter login-name: ')
            try:
                await chat_client.login(login_name)
                print(f'logged-in as {login_name}')

            except LoginConflictError:
                print('login name already exists, pick another name')
            except LoginError:
                print('error loggining in, try again')

        elif command == '4':
            try:
                rooms = await chat_client.lrooms()
                for room in rooms:
                    print('\n\t\troom name ({}), owner ({}): {}'.format(room['name'], room['owner'], room['description']))

            except Exception as e:
                print('error getting rooms from server {}'.format(e))

        elif command == '5':
            try:

                user_message = await aioconsole.ainput('enter your message: ')
                await chat_client.post(user_message, 'public')

            except Exception as e:
                print('error posting message {}'.format(e))

        elif command == '6':
            try:
                print('Here are the direct messages for this twitter account:\n')
                for msg in twitter_client.list_dms():
                    print(msg)

            except Exception as e:
                print('error getting direct messages {}'.format(e))

        elif command == '7':
            try:
                print('Here is the list of followers for this twitter account:')
                for follower in twitter_client.get_followers():
                    print(follower)

            except Exception as e:
                print('Error listing followers {}'.format(e))

        elif command == '8':
            try:
                follower_name = input('Enter the name of the follower you want to DM: ')
                msg_dm = input('Enter your DM: ')
                twitter_client.send_dm(msg_dm, follower_name)
            except Exception as e:
                print('Error sending a DM {}'.format(e))


@click.group()
def cli():
    pass


@cli.command(help="run chat client")
@click.argument("host")
@click.argument("port", type=int)
def connect(host, port):
    chat_client = ChatClient(ip=host, port=port)
    loop = asyncio.get_event_loop()

    loop.run_until_complete(chat_client._connect())

    twitter_blk_client = TwitterDMClient(consumer_key=consumer_key,
                                         consumer_secret=consumer_secret,
                                         access_token=access_token,
                                         access_secret=access_secret)
    try:
        twitter_blk_client.init_auth()
    except Exception as e:
        print('error authenticating with twitter API: {}'.format(e))
        sys.exit(1)

    # display menu, wait for command from user, invoke method on client
    asyncio.ensure_future(handle_user_input(chat_client=chat_client, twitter_client = twitter_blk_client, loop=loop))
    asyncio.ensure_future(display_msgs(chat_client=chat_client))

    loop.run_forever()


@cli.command(help='run chat server')
@click.argument('port', type=int)
def listen(port):
    click.echo('starting chat server at {}'.format(port))
    chat_server = ChatServer(port=port)
    chat_server.start()


if __name__ == '__main__':
    cli()