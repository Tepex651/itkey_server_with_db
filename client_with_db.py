import datetime
import random
import sys

import asyncio
import asyncpg
import yaml


config = 'config_with_db.yaml'
try:
    with open(config, 'r') as file:
        full_file = yaml.load(file, Loader=yaml.FullLoader)
        db_conf = full_file['db']
        servers_conf = [full_file[server] for server in full_file if server != 'db']
except OSError:
    print("Could not open/read file:", config)
    sys.exit()


async def connect_client(**conf):
    """Open connections with server and database. 
    Start functions 'send_seconds' and 'read_db'
    
    """
    _, writer = await asyncio.open_connection(host=conf['host'], port=conf['port'])
    print(f"{datetime.datetime.now().time()} - Openned connection with server {conf['id']} port - {conf['port']}")
    conn = await asyncpg.connect(host=db_conf['host'], 
                                 password=db_conf['password'], 
                                 user=db_conf['user'], 
                                 database=db_conf['database'], 
                                 port=db_conf['port'])
    await asyncio.gather(send_seconds(writer, conf['id']), read_db(conn, conf['id']))


async def send_seconds(writer, server_id):
    """Start sending random seconds to server"""
    while True:
        seconds_for_server = str(random.randint(1, 10)) + '\n'
        seconds_for_client = random.randint(1, 10)
        await asyncio.sleep(seconds_for_client)
        print(f'{datetime.datetime.now().time()} - Send to server {server_id}: {seconds_for_server}')
        writer.write(seconds_for_server.encode())
        
        
async def read_db(conn, server_id):
    """Generates random digit from 1 to 10. Writes it to variable 'seconds'. 
    Reading records from database every 'seconds'
    
    """
    seconds = random.randint(5, 10)
    print(f"I will read server's {server_id} data from db every {seconds} seconds.")
    while True:
        await asyncio.sleep(seconds)
        results = await conn.fetch('''
                SELECT * FROM test 
                WHERE EXTRACT(EPOCH FROM CURRENT_TIMESTAMP - created) <= $2 AND server_id = $1;
                ''', server_id, seconds)
        print(datetime.datetime.now().time(), f"Server's {server_id} data")
        if results:
            for record in results:
                print(*record.values())
        else:
            print('No data')


async def main():
    """Makes list of connections coroutines and start them at the same time"""
    connections = [connect_client(**conf) for conf in servers_conf]
    await asyncio.gather(*connections)
   
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Connection was closed')