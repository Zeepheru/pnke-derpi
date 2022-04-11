import requests
import os
import re
import json
import urllib
import time

"""
This is mostly draft, temporary (BWAHAHA) code.
DOCS:
https://docs.python-requests.org/en/latest/


API:
https://derpibooru.org/pages/api

Test image:
2836500 (RD)

"""

def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True)

def justHere(src_path):
    for root, dirs, files in os.walk(src_path):
        for f in files:
            print("")

####

class imgDownloader():
    """
    JUST GRAB MAH YOUTUBE CODE
    """
    def __init__(self) -> None:
        """
        >> Directory structure::
        pnke-derpi/
        ├── -data/
        │   ├── derpi-imgs/
        │   ├── derpi-tags/

        """
        self.rel_path = r"/-data/"
        self.def_path = os.path.join(os.getcwd(), self.rel_path)

    def getImagesPresent(self, id_only=True):
        """
        lists images in the derpi-imgs directory 
        """
        if id_only:
            return [re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', a) for a in os.listdir(os.path.join(self.def_path, "derpi-imgs"))]
        else:
            return os.listdir(os.path.join(self.def_path, "derpi-imgs"))

    def fullDownload(self, id_list=[], tags={}, dir_path="", export_json=True, download_images=True):
        """
        What this is (supposed) to do is to:
        > given an inputed list of id's and corresponding dict of tags (sifted for important ones)
        - check if images and tags? are in the fixed directories
        - download/copy images into a seperate folder
        - (Json) with a json file outlining tags in the main directory
        """




class derpi():
    def __init__(self) -> None:
        self.s = requests.Session()
        print("Session Created.")

        ## vars
        self.base_url = "https://derpibooru.org"

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
        What the fuck I am just bored

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
    
    def getImageInfo(self, id):
        """
        inputs id
        returns r_json["image"] as a dict
        with some new additions for ease of access
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
        # print("Posting: "+url) # commented out for now.
        r_json = self.get(
            url=url,
            printJson=False
        )

        
        r_dict = r_json["image"]
        r_dict["dl"] = r_json["image"]["representations"]["full"]

        return r_dict


    def imageSearch(self, q="safe", sf="first_seen_at", sd="desc", 
        n_get=50, per_page=50,
        desired_tags=[], undesired_tags=[]):
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
        n_iter = int(n_get / per_page)
        list_of_images = []

        if n_get < per_page:
            per_page = int(n_get)

        for pg in range(n_iter+1):
            url = self.combineApiUrl(
                api_path, 
                q_params={
                    "q":urllib.parse.quote(q.replace(" ","")),
                    "filter_id":56027,
                    "page":pg,
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
def randomFun():
    derp = derpi()

    imgList = derp.imageSearch(q="artist:marsminer, explicit, score.gte:100", sf="score", n_get=100)
    for imgId in imgList:
        print(derp.findThatFileName(imgId))

def main():
    derp = derpi()

    ### processing data for batch dl
    s_query = "fs, pp, safe, score.gte:250, score.lte:350"
    imgList = derp.imageSearch(q=s_query, sf="score", n_get=10)

    desired_tags = ["fluttershy", "pinkie pie"] # note same tags with dissimilar strings
    # fuck I need a `too many characters in here` filter

    # maybe instead of n_get, have it iterate through the tags and add where necessary.

    dl_list = []
    tag_list = {}
    for id in imgList:
        r = derp.getImageInfo(id)
        dl_list.append(r["dl"])
        tag_list[id] = [tag for tag in r["tags"] if tag in desired_tags]

    print(dl_list, tag_list)

    # derp.get(derp.combineApiUrl("/api/v1/json/filters/56027"), printJson=True)


if __name__ == "__main__":
    randomFun()