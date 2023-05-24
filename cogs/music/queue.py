import sqlite3

db_path = "./data/music.db"


# Creates the tables if they don't exist
def initialize_tables():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create servers table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS servers (
                        server_id TEXT PRIMARY KEY,
                        is_playing INTEGER DEFAULT 0,
                    )''')

    # Create queue table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS queue (
                        server_id TEXT,
                        song_link TEXT,
                        queued_by TEXT,
                        index INTEGER,
                        has_played INTEGER DEFAULT 0,
                        PRIMARY KEY (server_id, order_num)
                    )''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Queue a song in the db
def add_song(server_id, song_link, queued_by):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    add_server(server_id, cursor, conn)

    # Grab current index
    cursor.execute(f"""
                   SELECT MAX(index)
                   FROM queue
                   WHERE server_id = ?
                   """, (server_id,))
    result = cursor.fetchone()

    # Highnest number or 0
    max_order_num = result[0] + 1 if result[0] is not None else 0

    cursor.execute("""
                   INSERT INTO queue (server_id, song_link, queued_by, index)
                   VALUES (?, ?, ?, ?)
                   """, (server_id, song_link, queued_by, max_order_num))

    conn.commit()
    conn.close()


# Add server to db if first time queuing
def add_server(server_id, cursor, conn):
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
def mark_song_as_finished(server_id, order_num):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the song as finished
    cursor.execute('''DELETE FROM queue
                   WHERE server_id = ? AND order_num = ?''',
                   (server_id, order_num))
    #cursor.execute('''UPDATE queue
    #               SET is_finished = 1
    #               WHERE server_id = ? AND index = ?''',
    #               (server_id, order_num))

    # Get the order numbers of unplayed songs
    cursor.execute('''SELECT index
                   FROM queue
                   WHERE server_id = ? AND is_finished = 0''', (server_id,))
    unplayed_order_nums = [row[0] for row in cursor.fetchall()]

    # Update the order numbers of unplayed songs
    for new_order, old_order in enumerate(unplayed_order_nums, start=1):
        cursor.execute('''UPDATE queue
                       SET order_num = ?
                       WHERE server_id = ? AND order_num = ?''',
                       (new_order, server_id, old_order))

    # Close connection
    conn.commit()
    conn.close()


# Sets the playing variable in a server to true or false
def update_server(server_id, playing: bool):
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add server to db if not present
    add_server(server_id, cursor, conn)

    value = 1 if playing else 0

    # Update field
    cursor.execute("""UPDATE servers
                   SET is_playing = ?
                   WHERE server_id = ?
                   """, (value, server_id))

    # Close connection
    conn.commit()
    conn.close()

def is_server_playing(server_id):
    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add server to db if not present
    add_server(server_id, cursor, conn)

    cursor.execute("""SELECT is_playing
                   FROM servers
                   WHERE server_id = ?""",
                   (server_id,))

    result = cursor.fetchone()

    conn.commit()
    conn.close()

    return result
