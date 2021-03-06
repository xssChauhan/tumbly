from os.path import exists, join, abspath, dirname
import sqlite3

''' Database Functions '''


BASE_PATH = 'databases'

# Check database exists, if not, create it and necessary table etc.


def create_check_database(database_name):
    # Update the path
    database_path = join(BASE_PATH, database_name)
    if not exists(database_path):
        # Create the database
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # Create table for tags, photos and photo tags
        c.execute('''CREATE TABLE IF NOT EXISTS tags
                  (tag_id integer primary key autoincrement,
                   tag text,
                   unique(tag))''')
        c.execute('''CREATE TABLE IF NOT EXISTS photos
                  (photo_id integer primary key autoincrement,
                   note_count integer,
                   url text,
                   unique(url))''')
        c.execute('''CREATE TABLE IF NOT EXISTS photo_tags
                  (tag_id integer,
                   photo_id integer,
                   unique (tag_id, photo_id),
                   foreign key(tag_id) references tags(tag_id),
                   foreign key(photo_id) references photos(photo_id))''')
        conn.commit()
        return conn
    else:
        # If it exists connect
        return sqlite3.connect(database_path)

# Functions to call to insert data into database tables


def add_tags(c, tags, verbose=None):
    c.executemany('''INSERT INTO tags (tag)
                     SELECT * FROM (SELECT ?)
                     WHERE NOT EXISTS
                             (SELECT * FROM tags WHERE tag = ?)
                     LIMIT 1''', [(t, t) for t in tags]
                  )


def add_photo(c, url, note_count, verbose=None):
    c.execute('''INSERT INTO photos (url, note_count)
                 SELECT * FROM (SELECT ?, ?)
                 WHERE NOT EXISTS (
                   SELECT * FROM photos WHERE url = ?
                 ) LIMIT 1''', (url, note_count, url))


def link_tags_photo(c, tags, url, verbose=None):
    photo_id = c.execute('''SELECT photo_id from photos
                            where url = ? LIMIT 1''',
                         (url,)).fetchone()[0]
    tag_ids = [c.execute('''SELECT tag_id from tags
                             where tag = ? LIMIT 1''', (t,)).fetchone()[0]
               for t in tags]
    if verbose:
        for tag_id, photo_id in product(tags, [url]):
            print ("#%s %s" % (tag_id, photo_id))
    data = [(photo_id, t, photo_id, t) for t in tag_ids]
    c.executemany('''INSERT INTO photo_tags (photo_id, tag_id)
                     SELECT * FROM (SELECT ?, ?)
                     WHERE NOT EXISTS (
                       SELECT * FROM photo_tags
                         WHERE photo_id = ?
                         AND   tag_id = ?
                     ) LIMIT 1''', data)
