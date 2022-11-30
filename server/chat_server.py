import asyncio


class ChatServerProtocol(asyncio.Protocol):
    # master dict {transport: {'remote': ('127.0.0.1', 76678), 'login-name': 'omari', 'rooms': [public, room1]}
    clients = {}
    rooms = [{'name': 'public',
              'owner': 'system',
              'description': 'The public room which acts as broadcast, all logged-in users are in public room by default'}
             ]

    def __init__(self):
        self._pieces = []

    def _handle_command(self):
        command = ''.join(self._pieces)
        self._pieces = []

        if command.startswith('/lru'):
            # get list of registered users
            lru = [r['login-name'] for r in ChatServerProtocol.clients.values() if r['login-name']]
            response = '/lru '
            for user in lru:
                response += (f'{user}, ')

            response.rstrip(', ')
            response = ''.join([response, '$'])
            self._transport.write(response.encode('utf-8'))

        elif command.startswith('/login '):
            # TODO: check if login-name already exists
            # TODO: what to do when already logged-in

            login_name = command.lstrip('/login').rstrip('$').strip()

            all_login_names = [v['login-name'] for v in ChatServerProtocol.clients.values()]
            if login_name in all_login_names:
                response = '/login already exists$'
            else:
                client_record = ChatServerProtocol.clients[self._transport]
                client_record['login-name'] = login_name
                response = '/login success$'

            self._transport.write(response.encode('utf-8'))

        elif command.startswith('/lrooms '):
            # response format
            # /lroom public&system&public room\nroom1&omari&room to discuss chat service impl$

            room_msgs = ['{}&{}&{}'.format(r['name'], r['owner'], r['description']) for r in ChatServerProtocol.rooms]
            response = '/lrooms {}$'.format('\n'.join(room_msgs))
            self._transport.write(response.encode('utf-8'))

        elif command.startswith('/post '):
            # expected request format: /post public&hello everyone
            room, msg = command.lstrip('/post').rstrip('$').split('&')

            transports = [k for k, v in ChatServerProtocol.clients.items() if room.strip() in v['rooms']]

            msg_to_send = '/MSG {}$'.format(msg)
            for transport in transports:
                transport.write(msg_to_send.encode('utf-8'))

    def connection_made(self, transport: asyncio.Transport):
        """Called on new client connections"""
        self._remote_addr = transport.get_extra_info('peername')
        print('[+] client {} connected.'.format(self._remote_addr))
        self._transport = transport
        ChatServerProtocol.clients[transport] = {'remote': self._remote_addr, 'login-name': None, 'rooms': ['public']}

    def data_received(self, data):
        """Handle data"""
        self._pieces.append(data.decode('utf-8'))
        if ''.join(self._pieces).endswith('$'):
            self._handle_command()

    def connection_lost(self, exc):
        """remote closed connection"""
        print('[-] lost connectio to {}'.format(ChatServerProtocol.clients[self._transport]))
        self._transport.close()


class ChatServer:
    LOCAL_HOST = '0.0.0.0'

    def __init__(self, port):
        self._port: int = port

    def listen(self):
        """start listening"""
        pass

    def start(self):
        """start"""
        loop = asyncio.get_event_loop()
        server_coro = loop.create_server(lambda: ChatServerProtocol(),
                                         host=ChatServer.LOCAL_HOST,
                                         port=self._port)

        loop.run_until_complete(server_coro)
        loop.run_forever()


if __name__ == '__main__':
    chat_server = ChatServer(port=8080)
    chat_server.start()