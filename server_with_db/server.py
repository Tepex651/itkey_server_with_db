import os

import asyncio
import asyncpg


server_id = int(os.environ['SERVER_ID'])
db_host = os.environ['POSTGRES_HOST']
db_name = os.environ['POSTGRES_DB']
db_user = os.environ['POSTGRES_USER']
db_password = os.environ['POSTGRES_PASSWORD']


async def wait_and_write(conn, seconds):
    """Sleeps 'seconds'. After that writes message to database"""
    await asyncio.sleep(int(seconds))
    await conn.execute('''
            INSERT INTO test(server_id, seconds) VALUES($1, $2)
            ''', server_id, int(seconds))
    print(f'Write into DB COMPLETE {server_id, int(seconds)}')


async def handle_echo(reader, _):
    """Connections to batabase. Reads messages and create task 'wait_and_write'."""
    conn = await asyncpg.connect(host=db_host, password=db_password, user=db_user, database=db_name)
    while True:
        data = await reader.readline()
        if not data:
            print('Connection was closed')
            break
        seconds = data.decode().split('\n')[0]
        print(f'I get {seconds}')
        task = asyncio.create_task(wait_and_write(conn, seconds))


async def main():
    server = await asyncio.start_server(handle_echo, '0.0.0.0', 6000)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())