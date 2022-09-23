import psycopg
from psycopg import sql
import re
import json
from datetime import datetime

"""
AH

https://www.psycopg.org/psycopg3/docs/basic/usage.html
(also yes there's code to PROPERLY keep the connection details in a .ini file)
but hey. this ain't important. I'm using defaults anyway
    TODO just a _future note_

structure derived from:
https://derpibooru.org/pages/data_dumps


fucking problems
https://www.psycopg.org/psycopg3/docs/basic/from_pg2.html
"""

# TODO below are notes
noteToSelfForMMMGS = """
may have to add more tables for that, or even if you are especially ambitiuos
just add a new table to this that denotes whether the image is for PNKE or MILK or IC
I mean, though considering this is the "pnkederpibooru" db, that might not be the best of ideas.

otherwise for MMMGS, if it's going to its own 

"""

class pgDerpi():
    def __init__(self) -> None:
        self.connect()
        self.cur = self.conn.cursor()
        self.clientcur = psycopg.ClientCursor(self.conn)
        
        # checks and creates tables
        self.tableChecks()

    def resetTables(self):
        print("< !!!!!!!!! >")
        print("< !!!!!!!!! >")
        print("< !!!!!!!!! >")
        input("WARNING: The following command erases all data from the main tables. DEBUG ONLY. REMOVE AFTER PUSH TO PROD. Press enter to continue...")
        for table in list(self.table_info):
            # creating copies anyway
            self.cur.execute(f"DROP TABLE IF EXISTS {table}_backup;")
            self.cur.execute(f"CREATE TABLE {table}_backup AS TABLE {table};")

            self.cur.execute(f"DROP TABLE {table};")

        self.conn.commit()

    def closeServer(self):
        # might wanna update this (so I can more easily take data in and out)
        self.cur.close()

    def connect(self):
        """
        sets up self.conn as the connection to the db
        
        'errors' are thrown if the db doesn't exist, or other misc errors
        """
        try:
            self.conn = psycopg.connect(
                host="localhost",
                dbname="pnkederpibooru", # this is the current name
                user="postgres",
                password="postgres")

            print("Local database connection succuesful!")

        except psycopg.OperationalError as e:
            if re.search(r'database.does not exist', str(e)) != None:
                # tells user that the db should be created
                print("Database 'pnkederpibooru' does not exist. Please manually create the db")
                """
                >>> psql commands
                
                $ psql -U postgres
                CREATE DATABASE pnkederpibooru;
                """
            else:
                # some other less important error
                print(e)
        
    def tableChecks(self):
        """
        checks and creates the tables:
        images, image_taggings, tags

        dict below is self explanatory.

        # Not functioning cols:
        - images.image_size
        - images.hides
        - images.version_path

        # Renamed cols (AHHHH):
        - image_height = height 
        - image_width = width 
        - favorites = faves 
        - image_aspect_ratio = aspect_ratio 
        - user_id = uploader_id 
        - image_mime_type" = mime_type 
        - image_format" = format 
        - image_sha512_hash = sha512_hash
        - image_orig_sha512_hash = orig_sha512_hash

        # New cols 
        - image.source (moved from Derpi's public.image_sources)

        # New tables
        - artist (standalone)
        - comments 

        ## comments is fully standalone and isn't integrated with anything else 
        aka the code to check images and stuff doesn't bother with comments, yet
        it's there for MMMGS future use.
        ## artists, also not used at the moment (can just take from tags WHERE category is origin)
        """
        self.table_info ={
            "images":[
                ('id', 'bigint'),
                ('created_at', 'timestamp'),
                ('updated_at', 'timestamp'),
                ('width', 'integer'),
                ('height', 'integer'),
                ('size', 'integer'),
                ('source', 'text'),
                ('comment_count', 'integer'),
                ('score', 'integer'),
                ('faves', 'integer'),
                ('upvotes', 'integer'),
                ('downvotes', 'integer'),
                ('hides', 'integer'),
                ('aspect_ratio', 'double precision'),
                ('uploader_id', 'bigint'),
                ('mime_type', 'text'),
                ('format', 'text'),
                ('name', 'text'),
                ('version_path', 'text'),
                ('sha512_hash', 'text'),
                ('orig_sha512_hash', 'text')
            ],
            "image_taggings":[
                ('image_id', 'bigint'),
                ('tag_id', 'bigint')
            ],
            "tags":[
                ('id', 'bigint'),
                ('image_count', 'bigint'),
                ('name', 'text'),
                ('slug', 'text'),
                ('category', 'text'),
                ('description', 'text'),
                ('short_description', 'text')
            ],
            "artists":[
                ('id', 'bigint'),
                ('image_count', 'bigint'),
                ('name', 'text'),
                ('tag', 'text')
            ],
            "comments":[
                ('id', 'bigint'),
                ('image_id', 'bigint'),
                ('author', 'text'),
                ('avatar', 'text'),
                ('body', 'text')
            ]
        }
        self.table_uniques = {
            "images":['id'],
            "image_taggings":[], 
            "tags":['id','name'],
            "artists":['id','name'],
            "comments":['id']
        }

        # create 'CREATE' command
        create_cmds = []
        for table_name in list(self.table_info):
            self.cur.execute(
                f"""SELECT EXISTS (SELECT FROM pg_tables 
                WHERE schemaname = 'public' AND tablename = %s);""", [table_name]
            )
            if self.cur.fetchone()[0]: # (bool,)
                # table exists
                continue

            # as this checks and creates tables one by one, it can deal with singly deleted tables (for resetting etc)

            print(f"creating table: '{table_name}'")
            create_cmd = f"CREATE TABLE {table_name} (\n" 
            create_cmd += ',\n'.join(str(a[0]) + ' ' + str(a[1]) for a in self.table_info[table_name])
            if self.table_uniques[table_name] != []:
                create_cmd += ',\nUNIQUE(' + ', '.join(str(a) for a in self.table_uniques[table_name]) + ")"
            create_cmds.append(create_cmd + "\n);")

        # print(create_cmds)
        for command in create_cmds:
            # print(command)
            self.cur.execute(command)

        self.conn.commit()

    """
    quickcommands (negates the need to type sql commands lmao)
    v is for printing outputs

    also note that None can mean an empty table
    """
    def quickShowTable(self, table_name="", rowlimit=20, v=False):
        """
        set v=True to print for you ya lazy bugger

        TODO: I think it should be fetchall/many, not fetchone -> returns a single row 
        """
        # note the \x
        self.cur.execute(
            f"SELECT * FROM {table_name} LIMIT %s;", [rowlimit]
        )
        
        r = self.cur.fetchone()
        if v:
            print(r)
        return r

    def quickSelect(self, wide=False, query="*", table_name = "", rowLimit=None, v=False):
        # lmao
        command = f"SELECT {query} FROM {table_name}"
        if rowLimit != None:
            command += f" LIMIT = {rowLimit}" 
        if wide:
            self.cur.execute(r"\x on")

        command += ";"

        self.cur.execute(command)
        r = self.cur.fetchone()
        if v:
            print(r)
        return r

    def deleteRow(self, col, value=None, table_name = "", askForConfirmation=True):
        """
        Deletes from table (table_name) all rows that match the condition
        col = value

        askForConfirmation=True -> user has to cnfirm; default is True

        TODO TODO conditions need to be better written (its own function.)
        """    

        if not col:
            print("no condition.")
            return False

        if askForConfirmation:
            print(f"Delete rows from table:{table_name} where {col}={value}?")
            while True:
                answer = input("Confirmation required (y/n): ")
                if answer == "y":
                    break
                elif answer == "n":
                    print("Operation cancelled.")
                    return False
                else:
                    continue
            
        self.cur.execute(
            f"DELETE FROM {table_name} WHERE {col} = %s;", [value]
        ) # execute but you get the result.
        
        self.conn.commit()
        msg = self.cur.statusmessage
        if not msg:
            print("No rows deleted.")
            return False
        else:
            fuckfuckfuckfuckfuckfuck = msg.replace('DELETE ', '')
            print(f"{fuckfuckfuckfuckfuckfuck} rows deleted.")
            return True
        
    ###
    def getId(self, img_id=0):
        """
        ~check is just to only check that the id exists in images, returning a bool~

        input the imd_id, returns as a dict:
        - all cols in 'images'
        - tag_ids from 'image_taggings'
        - tags, being the corresponding tag name
        """
        return_data = {}

        ## images
        self.cur.execute(
            'SELECT * FROM images WHERE id = %s;', [img_id]
            )
        r = self.cur.fetchone()
        if r == None:
            # id not in db
            return None

        for i, col in enumerate(self.table_info["images"]):
            return_data[col[0]] = r[i]
        ## changing some datetimes back
        # may not be needed in the future
        # converting back to strings from datetime.datetime()
        return_data["created_at"] = return_data["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return_data["updated_at"] = return_data["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

        # image tags (ids)
        self.cur.execute(
            'SELECT tag_id FROM image_taggings WHERE image_id = %s;', [img_id]
            )
        r = self.cur.fetchall()
        return_data["tag_ids"] = [a[0] for a in r]

        # tag names
        id_list_postgres = "(" + str(return_data["tag_ids"])[1:-1] + ")"
        self.cur.execute(
            'SELECT name FROM tags WHERE id IN %(id_list)s;', {'id_list':id_list_postgres}
            )
        r = self.cur.fetchall()
        return_data["tags"] = [a[0] for a in r]

        # print(return_data)

        return return_data

    def updateTags(self, tag_info, overwrite=True, commit=False):
        """
        Updates the table "tags" with a tag_info dict, or a tag_response object.

        overwrite is self-explanatory
        commit is whether to commit (self.conn.commit() )
        """
        ## minor editing for reasons. "escapes" the newlines
        tag_info["description"] = tag_info["description"]

        # cols      
        cols = [col[0] for col in self.table_info["tags"]]
        cols = [x.replace("image_count", "images") for x in cols] # alas...

        info = tuple(tag_info[col] for col in cols)

        if overwrite:
        
            self.cur.execute(
                """
                INSERT INTO tags 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id, name)
                DO UPDATE SET
                    image_count = EXCLUDED.image_count,
                    category = EXCLUDED.category,
                    slug = EXCLUDED.slug,
                    description = EXCLUDED.description,
                    short_description = EXCLUDED.short_description;
                """, 
                info
            )
        else:
            self.cur.execute(
                """
                INSERT INTO tags 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id, name)
                DO NOTHING;
                """, 
                info
            )
        if commit:
            self.conn.commit()
        return True

    def updateId(self, data={}, overwrite=False):
        """
        udpates all values corresponding to the id
        aka writes them into all the tables.

        Assumes data is the output of derpi.getImageInfo()
        >> the dict - image:{} 

        the proper upsert syntax is used later a bit (lol)
        otherwise overwrite=True means to do so; False means ON CONFLCT DO NOTHING
        """
        #################### debug 
        # data = json.load(open('test-image-format.json'))["image"]
        ##################

        "the cols things is basically getting the columns of the local database for uses"
        cols = [col[0] for col in self.table_info["images"]]
        
        ## fixing some DERPIBOORU INCONSISTENCIES 
        data["source"] = data["representations"]["full"]
        #(keys not found) -> NULL
        datakeylist = list(data.keys())
        for col in list(self.table_info["images"]):
            if col[0] not in datakeylist:
                data[col[0]] = 'NULL'

        # aaaaaaa
        # adding quotation marks to all the "texts"
        for col in self.table_info["images"]:
            if col[1] == "text":
                if data[col[0]] != 'NULL':
                    data[col[0]] = "'" + data[col[0]] + "'"

        # time stuff
        ## I SWEAR DOING THIS THE OTHER WAY WILL BE FUCKING FUN
        data["created_at"] = "TIMESTAMP '" + data["created_at"].replace("T", " ").replace("Z", "") + "'"
        data["updated_at"] = "TIMESTAMP '" + data["updated_at"].replace("T", " ").replace("Z", "") + "'"
        # I guess just reconvert back lol?

        ### OVERWRITING
        if overwrite:
            print(f"Removing previous entries for image: {data['id']}")
            self.cur.execute(f"DELETE FROM images WHERE id = {data['id']};")
            self.cur.execute(f"DELETE FROM image_taggings WHERE image_id = {data['id']};")

        images_row = ', '.join(str(data[col]) for col in cols)
        self.cur.execute(f"INSERT INTO images VALUES ({images_row}) ON CONFLICT DO NOTHING;")

        # img taggings
        for tag_id in data["tag_ids"]:
            image_tagging_list_str = f"{data['id']},{tag_id}"
            self.cur.execute(f"INSERT INTO image_taggings VALUES ({image_tagging_list_str}) ON CONFLICT DO NOTHING;")

        # print(data.keys())
        if "tag_info" not in data.keys():
            "Means tags were not queried; only inserts name and id"
            for i, tag_id in enumerate(data["tag_ids"]):
                # create seperate value list with just name and id
                # print(value_str)
                self.cur.execute(
                    f"""
                    INSERT INTO tags 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id, name)
                    DO NOTHING;
                    """,
                    (tag_id, None, data['tags'][i], None, None, None, None)
                )
            
        else:
            for info_dict in data["tag_info"]:
                self.updateTags(tag_info=info_dict, overwrite=True, commit=False)
                

        print(f"Inserted data for image: {data['id']} into DB tables.")
        # finally,
        self.conn.commit()
        return True


"INSERT INTO tags VALUES (1, 1);"

if __name__ == "__main__":
    # TESTING TESTING
    a = pgDerpi()
    # a.resetTables()
    # a = pgDerpi()
    
    # a.updateId(overwrite=True)
    # print(a.quickShowTable("image_taggings"))
    print(a.getId(2836500))
