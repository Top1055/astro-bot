import sqlite3

import discord
import asyncio

db_path = "./data/music.db"

FFMPEG_OPTS = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',

    'options':
        '-vn'
}

# Creates the tables if they don't exist
def initialize_tables():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create servers table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS servers (
                        server_id TEXT PRIMARY KEY,
                        is_playing INTEGER DEFAULT 0
                    );''')

    # Set all to not playing
    cursor.execute("UPDATE servers SET is_playing = 0;")

    # Create queue table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS queue (
                        server_id TEXT NOT NULL,
                        song_link TEXT,
                        queued_by TEXT,
                        position INTEGER NOT NULL,
                        has_played INTEGER DEFAULT 0,
                        PRIMARY KEY (position),
                        FOREIGN KEY (server_id) REFERENCES servers(server_id)
                    );''')
    # Clear all entries
    cursor.execute("DELETE FROM queue;")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Queue a song in the db
async def add_song(server_id, song_link, queued_by):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    await add_server(server_id, cursor, conn)

    max_order_num = await get_max(server_id, cursor) + 1

    cursor.execute("""
                   INSERT INTO queue (server_id, song_link, queued_by, position)
                   VALUES (?, ?, ?, ?)
                   """, (server_id, song_link, queued_by, max_order_num))

    conn.commit()
    conn.close()


# Add server to db if first time queuing
async def add_server(server_id, cursor, conn):
    # Check if the server exists
    cursor.execute('''SELECT COUNT(*)
                   FROM servers
                   WHERE server_id = ?''', (server_id,))

    result = cursor.fetchone()
    server_exists = result[0] > 0

    # If the server doesn't exist, add it
    if not server_exists:
        cursor.execute('''INSERT INTO servers (server_id)
                       VALUES (?)''', (server_id,))
        conn.commit()


# set song as played and update indexes
async def mark_song_as_finished(server_id, order_num):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the song as finished
    cursor.execute('''DELETE FROM queue
                   WHERE server_id = ? AND position = ?''',
                   (server_id, order_num))

    # Close connection
    conn.commit()
    conn.close()


# Grab max order from server
async def get_max(server_id, cursor):
    cursor.execute(f"""
                   SELECT MAX(position)
                   FROM queue
                   WHERE server_id = ?
                   """, (server_id,))
    result = cursor.fetchone()

    # Highnest number or 0
    max_order_num = result[0] if result[0] is not None else -1

    return max_order_num


# Pop song from server
async def pop(server_id):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # JUST INCASE!
    await add_server(server_id, cursor, conn)

    max_order = await get_max(server_id, cursor)
    if max_order == -1:
        conn.commit()
        conn.close()
        return None

    cursor.execute('''SELECT song_link
                   FROM queue
                   WHERE server_id = ? AND position = ?
                   ''', (server_id, max_order))
    result = cursor.fetchone()

    conn.commit()
    conn.close()

    await mark_song_as_finished(server_id, max_order)

    return result[0]


# Sets the playing variable in a server to true or false
async def update_server(server_id, playing: bool):
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add server to db if not present
    await add_server(server_id, cursor, conn)

    value = 1 if playing else 0

    # Update field
    cursor.execute("""UPDATE servers
                   SET is_playing = ?
                   WHERE server_id = ?
                   """, (value, server_id))

    # Close connection
    conn.commit()
    conn.close()


async def is_server_playing(server_id):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add server to db if not present
    await add_server(server_id, cursor, conn)

    cursor.execute("""SELECT is_playing
                   FROM servers
                   WHERE server_id = ?""",
                   (server_id,))

    result = cursor.fetchone()
    print(result)

    conn.commit()
    conn.close()

    return True if result[0] == 1 else False


# Delete all songs from a server
async def clear(server_id):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    await add_server(server_id, cursor, conn)
    await update_server(server_id, False)

    # Delete all songs from the server
    cursor.execute('''DELETE FROM queue WHERE server_id = ?''', (server_id,))

    conn.commit()
    conn.close()


# Play and loop songs in server
async def play(ctx):
    server_id = ctx.guild.id

    # Wait until song is stopped playing 
    #while ctx.voice_client.is_playing():
        #await asyncio.sleep(1)

    # check next song
    url = await pop(server_id)

    # if no other song update server and return
    if url is None:
        await update_server(server_id, False)
        return

    # else play next song and call play again
    ctx.voice_client.play(
            AstroPlayer(ctx, url, FFMPEG_OPTS))

class AstroPlayer(discord.FFmpegPCMAudio):
    def __init__(self, ctx, source, options) -> None:
        self.ctx = ctx
        super().__init__(source, **options)

    def _kill_process(self):
        super()._kill_process
        asyncio.run(play(self.ctx))
