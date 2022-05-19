import requests
import os
import re
import json
import urllib
import time
import pandas as pd
from tqdm import tqdm
import shutil

from PIL import Image


Image.MAX_IMAGE_PIXELS = None # disabling the protections lol

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
    # print(f_path)

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
            filepath = filepath + ".json"

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
        """
        DOES NOTHING AT THE MOMENT.
        """
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

    def loadFromCSVlegacy(self, filepath):
        """
        returns a list of ids, for now (may be configurable in the future idk lollll)

        """
        filepath = os.path.join(self.def_path, filepath)

        if not os.path.exists(filepath) or not filepath.endswith(".csv"):
            print("Not a CSV File / Doesn't exist.")
            return

        df = pd.read_csv(filepath)
        return df['id'].tolist()

    def loadFromCSV(self, filepath, return_type="dict"):
        """
        loads from a CSV file with the (newest default format)
        returns dl_list, a dict with each id and the corresponding required data

        Note: I know I should really just make everything run on Pandas df's
        but I'm lazy and can't be arsed, so have fun with slower running code (as if calling the api is _blazing fast_)
        """
        filepath = re.sub(r'\.csv\.csv$', r'\.csv', filepath) #idiot(me)-proofing
        filepath = os.path.join(self.def_path, filepath)

        if not os.path.exists(filepath) or not filepath.endswith(".csv"):
            print("{filepath} - Not a CSV File / Doesn't exist.")
            return

        df = pd.read_csv(filepath)
        df.rename(columns = {'tag':'desired_tags'}, inplace = True) #me dum dum
        df.rename(columns = {'tags':'desired_tags'}, inplace = True) # also / in case lol

        # ah yes
        df["desired_tags"] = df["desired_tags"].apply(lambda x: re.findall(r'(?!,).+?(?=,)', x))
        

        if return_type == "dict":
            return df.set_index('id').T.to_dict()
        elif return_type == "df" or return_type == "dataframe": 
            return df
        else:
            print("Wrong return_type specified.")
            return None

    def fullDownload(self, dl_list, dir_path, new_size=(0,0), new_format="", 
        export_json=False, export_csv=True, download_images=True, force_redownload=False, start_empty=False):
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

        dl_list should be a df but dict is still supported
        """

        ## setting up local folders.
        download_folder = os.path.join(self.def_path, dir_path)
        if start_empty:
            #yeahhh boi
            if os.path.exists(download_folder):
                shutil.rmtree(download_folder)

        if not os.path.exists(download_folder):
            createallfolders(download_folder)
        ## 

    
        if not force_redownload:
            ids_not_needed = [id for id in list(dl_list) if id in self.getImagesPresent()]
        else:
            ids_not_needed = []


        ## convertiong to a df if needed
        dl_list_dict = {}
        if type(dl_list).__name__ == "dict":
            print("INFO: dl_list is a dictionary. Recommended to use Pandas Dataframes.") # TODO lmao I need to log

            dl_list_dict = dict(dl_list_dict) # for purposes.

            taglist_str = []
            for id in list(dl_list):
                taglist_str.append(','.join(tag for tag in dl_list[id]["desired_tags"]))
            # basically ['tag,tag,tag,tag,...', 'tag,tag']

            data = {'id': list(dl_list),
                    'tag': taglist_str, 
                    'src': [dl_list[id]["src"] for id in list(dl_list)],
                    'fname': [dl_list[id]["fname"] for id in list(dl_list)],
                    'format': [dl_list[id]["format"] for id in list(dl_list)] 
                    }

            dl_list = pd.DataFrame(data, columns=['id', 'tag', 'src', 'fname', 'format'])

            if new_format != "":
                # I think this works
                ## this basically changes the fnames in the df to new fnames
                dl_list["fname"] = dl_list["fname"].apply(lambda x: re.sub(r'(?<=\.)[a-zA-Z0-9]+$', f'{new_format}', x))
                
        # creates the new df based on what's not in ids_not_needed
        new_dl_list = dl_list.loc[~dl_list["id"].isin(ids_not_needed)]
        
        ## csv/json first
        if export_csv:
            # TODO no functions yet, code is here until needed
            # also yes, still the main directory
            print("Writing csv file to {}.csv".format(dir_path))
            dl_list.to_csv(os.path.join(self.def_path, dir_path + ".csv"), index = False, header=True)

        elif export_json:
            ### currently deprecated TODO
            print("WARNING: Exporting as a json is deprecated. Exiting.")
            return False
            tags = {}
            for id in list(dl_list_dict): # if df it is not converted
                tags[id] = dl_list[id]["desired_tags"]

            print("Writing json file to {}.json".format(dir_path))
            self.writeJson(tags, os.path.join(self.def_path, dir_path + ".json"))

        ## then images
        if download_images:
            total = len(new_dl_list)
            for n, id in enumerate(new_dl_list["id"].tolist()):
                print("({}/{}) - {}%".format(n+1, total, (n+1)/total*100)) # the math lol

                # downloading first
                self.downloadFile(
                    new_dl_list.loc[new_dl_list["id"] == id]["src"].item(),
                    os.path.join(self.def_path, "derpi-imgs", 
                    new_dl_list.loc[new_dl_list["id"] == id]["fname"].item())
                )
            
            print("Copying Files.")
            for id in dl_list["id"].tolist():
                try:
                    src = os.path.join(self.def_path, "derpi-imgs", str(id)+"."+dl_list.loc[dl_list["id"] == id]["format"].item())
                    dst = os.path.join(self.def_path, dir_path, str(id)+"."+dl_list.loc[dl_list["id"] == id]["format"].item())
                    print("Copying {} to {}".format(src, dst))

                    shutil.copy(src, dst)
                except Exception as e:
                    print(e)
                    # This means the OG file is a jpg beacuse I fucked some stuff up
                    src = os.path.join(self.def_path, "derpi-imgs", str(id)+"."+"jpg")
                    dst = os.path.join(self.def_path, dir_path, str(id)+"."+"jpg")
                    print("Copying {} to {}".format(src, dst))

                    shutil.copy(src, dst)


        ## resizing crap
        image_files = os.listdir(download_folder) # perform image functions on the export folder.
        for i, f in enumerate(image_files):
            print(f"Performing image functions on {f} [{i+1}/{len(image_files)}]")

            self.convertResizeImage(
                os.path.join(download_folder, f),
                new_size=new_size,
                new_format=new_format
            )

        return True

    def quarantine(self, no_tags=[], src="", dst=""):
        """
        !! PATHS ARE TENTATIVELY RELATIVE WITHIN THE -data folder. !!!

        Function to basically batch move a bunch of files out of certain directories.
        This was an issue after I realised I'd turned off the explicit filter
        
        checks images in src and moves the specified ones to dst.

        might also have mmmgs use idk :)
        """
   
        src = os.path.join(self.def_path, src) # only def_path works btw
        if os.path.exists(src):
            pass
        else:
            print(f"Source path {src} does not exist.")
            return
                  
        if re.search(r'.:\\', dst) != None:
            if not os.path.exists(dst):
                createallfolders(dst)
        else:
            dst = os.path.join(self.def_path, dst)
            if not os.path.exists(dst):
                createallfolders(dst)
        
        # new system for keeping track of filenames
        img_filenames = {}
        for f in os.listdir(src):
            img_filenames[re.sub(r'\..+$', '', f)] = f
            # so the ids correspond to the filenames, I'm doing the regex recursively anyway
        idlist = list(img_filenames)
        if idlist == []:
            print("No images.")
            return
                  
        move_list = {}
        # images to move
                  
        derp = derpi()
        for i, id in enumerate(idlist):
            print(f'Obtaining info for {id} from Derpi [{i+1}/{len(idlist)}].')

            img = derp.getImageInfo(id)
            if any(a in img["tags"] for a in no_tags):
                  move_list[id] = img
                  break
                  ## Debug
            
            
        print(f"{len(list(move_list))} images found with the tag(s) {no_tags}.")
        
        # Move
        for id in list(move_list):
            img_src = os.path.join(src, img_filenames[id])
            img_dst = os.path.join(dst, img_filenames[id])
            print(f"Moving {img_src} to {img_dst}")
            shutil.move(img_src, img_dst)
            


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

        importantly, the keys:
            src, fname, format, tags
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

        try:
            r_dict = r_json["image"]
            r_dict["src"] = r_json["image"]["representations"]["full"]
            r_dict["fname"] = str(id) + "." + r_dict["format"] 
        except:
            print("Image {id} has the wrong json keys - likely means the image id is valid but not available, eg duplicates")
            # Generally, if r is none the other places should not take the image
            return None

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
    # derp.get(derp.combineApiUrl("/api/v1/json/filters/56027"), printJson=True)

if __name__ == "__main__":
    randomCode()
