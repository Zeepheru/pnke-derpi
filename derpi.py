from matplotlib.font_manager import json_dump
from numpy import r_
import requests
import re
import urllib
import json

from derpidatabase import pgDerpi

"""
This is mostly draft, temporary (BWAHAHA) code.
DOCS:
https://docs.python-requests.org/en/latest/


API:
https://derpibooru.org/pages/api
Also:
https://derpibooru.org/pages/search_syntax

Test image:
2836500 (RD)
"""

def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True)            

class derpi():
    def __init__(self, local_sql_db=True, prefer_local=True) -> None:
        """
        local_sql_db can be set False for circumstances where the code needs to be run
        without a functioning local postgres database

        prefer_local is self-explanatory
        """
        self.s = requests.Session()
        print("Session Created.")

        ## vars
        self.base_url = "https://derpibooru.org"

        ## postgreSQL db
        self.local_sql = local_sql_db # used for later, whether the local db is even available
        if local_sql_db:
            self.pref_local = prefer_local # only if local postgres is even enabled lol
            # also currently not used.

            self.db = pgDerpi()

    def combineApiUrl(self, api_path, params = {}, q_params = {}):
        url = self.base_url + api_path

        for param in list(params):
            url = url.replace(":"+param, str(params[param]))
        
        #remove last fwd slash
        url = re.sub(r'/$', "", url)
        
        if len(q_params) != 0:
            url = url + '?' + '&'.join(query + "=" + str(q_params[query]) for query in list(q_params))

        return url

    def get(self, url, printJson=True):
        """
        For posting get urls, for debug use
        returns the json (and prints it if required)
        """
        r = self.s.get(url)
        if r.status_code != 200:
            print(r.status_code)
            return False

        if printJson: 
            print(dump_json(r.json()))

        return r.json()

    def findThatFileName(self, id, printPost=False):
        """
        What the fuck I am just bored (yes)

        printPost is set to false for the iterative thing, 
        but really I should be using proper logging code ;)
        """
        try:
            int(id)
        except:
            print("Id - NaN")
            return 
            
        api_path = r'/api/v1/json/images/:image_id'
        url = self.combineApiUrl(
                api_path, {"image_id":id}
            )
        if printPost:
            print("Posting: "+url)

        r_json = self.get(
            url=url,
            printJson=False
        )

        return r_json["image"]["name"]
    
    def getImageInfo(self, id, overwrite_local=False):
        """
        inputs id
        returns r_json["image"] as a dict
        with some new additions for ease of access

        importantly, the keys:
            src, fname, format, tags
        
        overwrite_local is whether to call the api regardless and overwrite the local entries
        """

        try:
            int(id)
        except:
            print("Id - NaN")
            return 

        # checks if present in db
        r_dict = self.db.getId(id)

        if r_dict != None and not overwrite_local: # I need this for the console output
            print(f"Data for image: {id} found in local db.")
            r_dict["src"] = r_dict["source"]
            r_dict["fname"] = str(id) + "." + r_dict["format"] 

            if r_dict["src"] == None:
                print(f"Image {id} has an invalid source, likely duplicate.")
                return None
            else:
                return r_dict
        
        else:
            # API TIME
            api_path = r'/api/v1/json/images/:image_id'
            url = self.combineApiUrl(
                    api_path, {"image_id":id}
                )
            # print("Posting: "+url) # commented out for now.
            r_dict = self.get(url=url, printJson=False)["image"]

            if self.local_sql:
                # give the db the r_dict
                self.db.updateId(data=r_dict, overwrite=True)

            try:
                r_dict["src"] = r_dict["representations"]["full"]
                r_dict["fname"] = str(id) + "." + r_dict["format"] 
                return r_dict
            except:
                print(f"Image {id} has the wrong json keys - likely means the image id is valid but not available, eg duplicates")
                # Generally, if r is none the other places should not take the image
                return None


    def imageSearchTagsDeprec(self, q="safe", sf="first_seen_at", sd="desc", 
        n_get=50, per_page=50,
        desired_tags=[], undesired_tags=[]):
        """
        Modified version of imageSearch() designed solely to get 
        a select number of images that fit the given tag criteria

        NOTE:
        if there are OR tags, put them in the query
        wait this whole function is sort of irrelevant because everything can be 
        chucked into the search query.
        What the HAAAAAY

        (Untested.)
        """
        api_path = r'/api/v1/json/search/images'
        q = urllib.parse.quote(q)

        pg = 1
        list_of_images = []

        while len(list_of_images) <= n_get:
            url = self.combineApiUrl(
                api_path, 
                q_params={
                    "q":q,
                    "filter_id":56027,
                    "page":pg,
                    "per_page":per_page,
                    "sd":sd,
                    "sf":sf
                    }
                )
            
            r_json = self.get(
                url=url,
                printJson=False
            )

            if len(r_json["images"]) == 0:
                break

            for image in r_json["images"]:
                if len(list_of_images) > n_get:
                    break

                id = image["id"]
                r = self.getImageInfo(id)
                if not all(a in r["tags"] for a in desired_tags) or any(a in r["tags"] for a in undesired_tags):
                    continue
                else:
                    list_of_images.append(id)

            pg += 1

        return list_of_images

    def imageSearch(self, q="safe", sf="first_seen_at", sd="desc", 
        n_get=50, per_page=50):
        """
        The Big one. Searches using the tags
        query is "q"

        NOTE:
        I have no procedure for filter_id's 
        56027 is "everything". That's the default for now.

        https://derpibooru.org/search?q=marble+pie%2C+score.gte%3A400%2C+safe

        As for sd and sf:
        default for sf is first_seen_at
        default for sd is desc

        -----
        n_get: number of images to get
        default=50 (1 max page)
        0 is no limit (WARNING: lag though)

        ------
        # just saying, the order _might_ be screwed, somehow.
        """
        api_path = r'/api/v1/json/search/images'
        n_iter = int((n_get - 1) / per_page)
        list_of_images = []

        if n_get < per_page:
            per_page = int(n_get)

        for pg in range(n_iter + 1):
            url = self.combineApiUrl(
                api_path, 
                q_params={
                    "q":urllib.parse.quote(q),
                    "filter_id":56027,
                    "page":pg+1,
                    "per_page":per_page,
                    "sd":sd,
                    "sf":sf
                    }
            )
            print("Posting: "+url)

            r_json = self.get(
                url=url,
                printJson=False
            )

            ## initially just print the total;
            if pg == 0:
                print("Number of queried images: {}".format(r_json['total']))

            ## get list of images, in order
            list_of_images += [image["id"] for image in r_json["images"]]

        list_of_images = list_of_images[:n_get]
        # print(list_of_images)
        # print(len(list_of_images))

        return list_of_images
####

# other utils
def createDerpiSearchQuery(def_query="solo, pony, !animated, !human, !webm, !gif, !eqg, !comic, !meme, created_at.lte:3 days ago", 
    min_score=(), max_score=(), yes_tags=[], no_tags=[], tag_string="", sfw=True):
    """
    Default query is the default, standard query

    yes_tags and no_tags are lists of tags to be added.
    """

    # buncha regex to make this work properly with badly input strings 
    # :D

    if sfw:
        # yes.
        yes_tags.append("safe")
        no_tags.append("explicit")

    # add tag_string and clean up with regex
    query = re.sub(r'([\s]+$)|(,[\s]+$)',"",re.sub(r'[\s]+$',', ',def_query+" ")+re.sub(r'^[\s]{0,99}(?=\S)','',tag_string)+" ")

    # add min and max score
    if min_score != ():
        query += ", score.gte:{}".format(int(min_score))
    if max_score != ():
        query += ", score.lte:{}".format(int(max_score))

    # add yes and no tags.
    if yes_tags != [] and yes_tags != None:
        query += ', ' + ', '.join(a for a in yes_tags)
    if no_tags != [] and no_tags != None:
        query += ', ' + ', '.join("!"+a for a in no_tags)

    return query


####

def randomCode():
    print("Never Gonna Give You Up")
    
    derp = derpi()
    data = derp.getImageInfo(2836500, overwrite_local=True)
    print(dump_json(data))

if __name__ == "__main__":
    randomCode()
