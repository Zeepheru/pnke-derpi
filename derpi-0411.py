import requests
import os
import re
import json
import urllib
import time
from tqdm import tqdm
import shutil

from PIL import Image



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

def justHere(src_path):
    for root, dirs, files in os.walk(src_path):
        for f in files:
            print("")

def createallfolders(f_path):
    """
    This somewhat works for full paths (folders.)

    NOT TESTED WITH FILES
    """
    f_path += "\\"
    print(f_path)

    if not os.path.exists(f_path):
        if "\\" not in f_path:
            current_folder = f_path
            if not os.path.exists(current_folder):
                os.mkdir(current_folder)

        else:
            all_folders = re.findall(r'^.*?(?=\\)|(?<=\\).*?(?=\\)|(?<=\\).+$',f_path)
            current_folder = all_folders[0] + "\\" + all_folders[1] # hahah wtf

            for folder in all_folders[2:]:
                current_folder = os.path.join(current_folder,folder)
                if not os.path.exists(current_folder):
                    # print("CREATING "+current_folder)
                    os.mkdir(current_folder)

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
        self.rel_path = r"-data"
        self.def_path = os.path.join(os.getcwd(), self.rel_path)
    
    def writeJson(self, data, filepath):
        if not filepath.endswith(".json"):
            fiepath = filepath + ".json"

        with open (filepath,'w', encoding='utf-8') as f:
            f.write(dump_json(data))

    def downloadFile(self, url, filepath):
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        t=tqdm(total=total_size, unit='iB', unit_scale=True)  

        print("Downloading to: {}".format(filepath))

        with open(filepath, 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()

    def getImagesPresent(self, id_only=True):
        """
        lists images in the derpi-imgs directory 
        """
        if id_only:
            return [int(re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', a)) for a in os.listdir(os.path.join(self.def_path, "derpi-imgs"))]
        else:
            return os.listdir(os.path.join(self.def_path, "derpi-imgs"))
    
    def extractFilename(self, filepath):
        # returns only the filename.
        return ""

    def convertResizeImage(self, filepath, new_size=(0,0), new_format="", delete_prev=True):
        """
        Converts the image.
        To the desired new size and new format (default: jpg)

        some random code on resizing and cropping properly here.
        """
        def reduceSizeToFit(a, b):
            """
            reduces the size of a (x, y) to b (x, y)
            a being the crop, b being the actual image dimensions
            returns (x, y)
            """
            x_a, y_a = a[0], a[1]
            x_b, y_b = b[0], b[1]

            r_x = x_b / x_a
            r_y = y_b / y_a
            if r_x <= r_y:
                x = int(x_a * r_x)
                y = int(y_a * r_x)
            else:
                x = int(x_a * r_y)
                y = int(y_a * r_y)

            del x_a, y_a, x_b, y_b, r_x, r_y

            return (x,y)

        def getCropCoords(og_size, crop):
            """
            returns the (left, upper, right, lower)-tuple
            required for Image to do its thing
            """

            return (
                int((og_size[0] - crop[0])/2),
                int((og_size[1] - crop[1])/2),
                int(og_size[0] - (og_size[0] - crop[0])/2),
                int(og_size[1] - (og_size[1] - crop[1])/2)
            )
        
        if new_size == (0,0) and new_format == "":
            # no resizing done.
            return False

        im = Image.open(filepath)
        
        if new_size != (0,0):
            im = im.crop(
                getCropCoords(im.size, reduceSizeToFit(new_size, im.size))
            )
            im = im.resize(new_size)

        if new_format != "":
            im = im.convert("RGB")
            im.save(re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', filepath) + "." + new_format)
            if delete_prev:
                if not filepath.endswith(new_format):
                    os.remove(filepath)
        else:
            im.save(filepath)        

        return True


    def fullDownload(self, dl_list, dir_path, new_size=(0,0), new_format="", export_json=True, download_images=True, force_redownload=False, start_empty=False):
        """
        adding derpi as an arg is a stopgap measure lull
        pls fix :(

        What this is (supposed) to do is to:
        > given an inputed list of images (sifted for important ones)
        - check if images and tags? are in the fixed directories
        - download/copy images into a seperate folder
        - (Json) with a json file outlining tags in the main directory
        - and then does the crop things on the output dir

        dir_path likely will apply  to both the folder and the 
        if empty string then ideally use datetime (TODO)
        """

        download_folder = os.path.join(self.def_path, dir_path)
        if start_empty:
            #yeahhh boi
            if os.path.exists(download_folder):
                shutil.rmtree(download_folder)

        if not os.path.exists(download_folder):
            createallfolders(download_folder)

    
        if not force_redownload:
            ids_not_needed = [id for id in list(dl_list) if id in self.getImagesPresent()]
        else:
            ids_not_needed = []

        new_dl_list = {}
        for id in list(dl_list):
            # I KNOW there's a more pythonic way, shut up    
            if id not in ids_not_needed:
                new_dl_list[id] = dl_list[id]

        #json first
        if export_json:
            tags = {}
            for id in list(dl_list):
                tags[id] = dl_list[id]["desired_tags"]

            print("Writing json file to {}.json".format(dir_path))
            self.writeJson(tags, os.path.join(self.def_path, dir_path + ".json"))

        #then images
        if download_images:

            for id in list(new_dl_list):
                # downloading first
                self.downloadFile(
                    new_dl_list[id]["dl"],
                    os.path.join(self.def_path, "derpi-imgs", str(id) + "." + dl_list[id]["format"])
                )
            
            for id in list(dl_list):
                # then copying
                src = os.path.join(self.def_path, "derpi-imgs", str(id) + "." + dl_list[id]["format"])
                dst = os.path.join(self.def_path, dir_path, str(id) + "." + dl_list[id]["format"])
                print("Copying {} to {}".format(src, dst))

                shutil.copy(src, dst)

        ## resizing crap
        for f in os.listdir(download_folder):
            print("Performing image functions on {}".format(f))

            self.convertResizeImage(
                os.path.join(download_folder, f),
                new_size=new_size,
                new_format=new_format
            )

        return True


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

    def imageSearchTags(self, q="safe", sf="first_seen_at", sd="desc", 
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
default_queries = "solo, pony, safe, score.gte:200, score.lte:750, !animated, !human, !clothes"
# score range may be seperate

def randomFun():
    derp = derpi()

    imgList = derp.imageSearch(q="artist:marsminer, explicit, score.gte:100", sf="score", n_get=100)
    for imgId in imgList:
        print(derp.findThatFileName(imgId))

def testBatch():
    """
    Test only. 
    To get 20 ponks images and 20 rd images
    """
    s_query_rd = "rd, !pp" + ", " + default_queries
    s_query_pp = "!rd, pp" + ", " + default_queries
    desired_tags = ["rainbow dash", "pinkie pie"]

    derp = derpi()

    # rd
    rd_imgList = derp.imageSearch(q=s_query_rd, sf="score", n_get=150)
    dl_list = {}
    for id in rd_imgList:
        r = derp.getImageInfo(id)
        dl_list[id] = {
            "dl":r["dl"],
            "desired_tags":[tag for tag in r["tags"] if tag in desired_tags],
            "format":r["format"]
        }

    # pp
    pp_imgList = derp.imageSearch(q=s_query_pp, sf="score", n_get=150)
    for id in pp_imgList:
        r = derp.getImageInfo(id)
        if id in list(dl_list):
            print("UHHHHHHHHHHHH" + str(id))

        dl_list[id] = {
            "dl":r["dl"],
            "desired_tags":[tag for tag in r["tags"] if tag in desired_tags],
            "format":r["format"]
        }

    # after combining, 
    dl = imgDownloader()
    dl.fullDownload(
        dl_list=dl_list,
        dir_path="test-1-cropped",
        start_empty=True,
        new_format="jpg",
        new_size=(400,400)
    )

def main():
    derp = derpi()

    ### processing data for batch dl
    s_query = "((!fs, pp) OR (!pp, fs)), solo, safe, score.gte:200, score.lte:1200, !animated" # this one is refined for two solo chars

    imgList = derp.imageSearch(q=s_query, sf="score", n_get=20)

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
    testBatch()