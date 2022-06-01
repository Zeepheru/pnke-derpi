import requests
import os
import re
import json
import time
import pandas as pd
from tqdm import tqdm
import shutil

from PIL import Image
Image.MAX_IMAGE_PIXELS = None # disabling the protections lol
from derpi import derpi


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
        │   ├── derpi-imgs-nsfw/
        │   ├── derpi-tags/

        """
        self.rel_path = r"-data"
        self.def_path = os.path.join(os.getcwd(), self.rel_path)
        self.local_img_src_paths = [
            "derpi-imgs",
            "derpi-imgs-nsfw"
        ]
    
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

    def getTagsFrom(self, tag_output):
        if type(tag_output).__name__ == "list":
            return tag_output
        elif type(tag_output).__name__ == "str":
            if re.search(r'\[.\]', tag_output) != None:
                # stoopid things
                tag_output = re.sub(r"'|\[|\]", '', tag_output)
                
            return re.findall(r'(?!,).+?(?=,|$)', tag_output)

    def getTagsFromDF(self, df, id=0):
        """
        Uses the inputs df and id to spit out a list of tags for the image
        where df is using a somewhat standard format for dataframes

        this function prefers the column to be "tags"

        ahhaha the function above
        """
        df.rename(columns = {'desired_tags':'tags'}, inplace = True) 
        df.rename(columns = {'tag':'tags'}, inplace = True) 

        tag_output = df.loc[df["id"] == int(id)]["desired_tags"].item()
        return self.getTagsFrom(tag_output)

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
    
    def exportDfToCSV(self, df, filepath):
        "LOL. "
        print("Writing csv file to {}.csv".format(filepath))
        df.to_csv(os.path.join(self.def_path, filepath + ".csv"), index = False, header=True)

    def loadFromCSV(self, filepath, return_type="dict"):
        """
        loads from a CSV file with the (newest default format)
        returns dl_list, a dict with each id and the corresponding required data

        Note: I know I should really just make everything run on Pandas df's
        but I'm lazy and can't be arsed, so have fun with slower running code (as if calling the api is _blazing fast_)

        NOTE NOTE NOTE
        This code returns desired_tags as a LIST. If some if statement is required, check
        main.py for the code to convert to strings and such
        """
        filepath = re.sub(r'\.csv\.csv$', r'\.csv', filepath) #idiot(me)-proofing
        filepath_full = os.path.join(self.def_path, filepath)

        if not filepath_full.endswith(".csv"):
            print("{filepath_full} - Not a CSV File.")
            return
        elif not os.path.exists(filepath_full):
            repath = filepath_full.replace('.csv', r'\\') + filepath
            if os.path.exists(repath):
                filepath_full = repath
            else:
                print("{filepath} - Does not exist.")
                return

        del filepath

        df = pd.read_csv(filepath_full)
        df.rename(columns = {'tag':'desired_tags'}, inplace = True) #me dum dum
        df.rename(columns = {'tags':'desired_tags'}, inplace = True) # also / in case lol

        # df["desired_tags"] = df["desired_tags"].apply(lambda x:str(x)) 
        # df["desired_tags"] = df["desired_tags"].apply(lambda x:re.sub(r"'|\[|\]", '', x))

        # ah yes
        df["desired_tags"] = df["desired_tags"].apply(lambda x: re.findall(r'(?!,).+?(?=,|$)', x))
        

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
        download_folder = os.path.join(self.def_path, f"{dir_path}\\images") # IMAGES ONLY
        if start_empty:
            #yeahhh boi
            if os.path.exists(download_folder):
                shutil.rmtree(download_folder)

        if not os.path.exists(download_folder):
            createallfolders(f"{download_folder}")
        ## 

        ## convertiong to a df if needed
        dl_list_dict = {}
        if type(dl_list).__name__ == "dict":
            print("INFO: dl_list is a dictionary. Recommended to use Pandas Dataframes.") # TODO lmao I need to log

            dl_list_dict = dict(dl_list_dict) # for purposes.

            taglist_str = []
            for id in list(dl_list):
                # not needed
                taglist_str.append(','.join(tag for tag in dl_list[id]["desired_tags"]))
            # basically ['tag,tag,tag,tag,...', 'tag,tag']

            data = {'id': list(dl_list),
                    'tags': [dl_list[id]["desired_tags"] for id in list(dl_list)], 
                    'src': [dl_list[id]["src"] for id in list(dl_list)],
                    'fname': [dl_list[id]["fname"] for id in list(dl_list)],
                    'format': [dl_list[id]["format"] for id in list(dl_list)] 
                    }

            dl_list = pd.DataFrame(data, columns=['id', 'tags', 'src', 'fname', 'format'])

            if new_format != "":
                # I think this works
                ## this basically changes the fnames in the df to new fnames
                dl_list["fname"] = dl_list["fname"].apply(lambda x: re.sub(r'(?<=\.)[a-zA-Z0-9]+$', f'{new_format}', x))
        else:
            # stupid renames
            dl_list.rename(columns = {'desired_tags':'tags'}, inplace = True) #me dum dum
                
        
        df_ids = dl_list["id"].tolist()
        imgs_present = self.getImagesPresent()
        if not force_redownload:
            ids_not_needed = [a for a in df_ids if a in imgs_present]
        else:
            ids_not_needed = []
        del df_ids, imgs_present

        # creates the new df based on what's not in ids_not_needed
        new_dl_list = dl_list.loc[~dl_list["id"].isin(ids_not_needed)]

        ## csv/json first
        if export_csv:
            # TODO no functions yet, code is here until needed
            # also yes, still the main directory
            self.exportDfToCSV(df=dl_list, filepath=f"{dir_path}\\{dir_path}")

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
            ## setting up the nsfw-sfw divide
            def evalSfw(row):
                # True / False
                tagList = self.getTagsFrom(row["tags"])
                if "explicit" in tagList:
                    return "derpi-imgs-nsfw"
                else:
                    return "derpi-imgs"
                
            # dl_list['nsfw'] = dl_list.apply(evalSfw)
            dl_list['dl_folder'] = dl_list.apply(evalSfw) # only one purpose anyway

            total = len(new_dl_list)
            for n, id in enumerate(new_dl_list["id"].tolist()):
                print("({}/{}) - {}%".format(n+1, total, (n+1)/total*100)) # the math lol

                # downloading first
                self.downloadFile(
                    new_dl_list.loc[new_dl_list["id"] == id]["src"].item(),
                    os.path.join(self.def_path, dl_list.loc[dl_list["id"] == id]['dl_folder'], 
                    new_dl_list.loc[new_dl_list["id"] == id]["fname"].item())
                )
            
            print("Copying Files.")
            """
            New method of copying files that is a bit less clunky.
            (taken from self.quarantine() )
            A dict `img_filenames` is created by listdir the various source paths

            img_filenames = {
                id: full_path,
                ...
            }
            """
            img_filenames = {}
            for source_path in self.local_img_src_paths:
                full_src_path = os.path.join(self.def_path, source_path)

                for f in os.listdir(full_src_path):
                    img_filenames[int(re.sub(r'\..+$', '', f))] = os.path.join(self.def_path, f)
            
            for id in dl_list["id"].tolist():
                try:
                    src = img_filenames[id]
                    dst = os.path.join(
                        self.def_path, dir_path, 
                        "images", 
                        str(id)+"."+dl_list.loc[dl_list["id"] == id]["format"].item())

                    print("Copying {} to {}".format(src, dst))

                    shutil.copy(src, dst)
                except Exception as e:
                    print(e)
                    # lol


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

    def quarantine(self, no_tags=[], src="", dst="", move_first=True):
        """
        !! PATHS ARE TENTATIVELY RELATIVE WITHIN THE -data folder. !!!
        lol

        Function to basically batch move a bunch of files out of certain directories.
        This was an issue after I realised I'd turned off the explicit filter
        
        checks images in src and moves the specified ones to dst.

        might also have mmmgs use idk :)
        - move_first just means it checks each image and moves without creating some intermediary.

        TODO TODO need to add /images for the newer datasets
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
            try:
                if any(a in img["tags"] for a in no_tags):
                    if not move_first:
                        move_list[id] = img

                    else:
                        img_src = os.path.join(src, img_filenames[id])
                        img_dst = os.path.join(dst, img_filenames[id])
                        print(f"Moving {img_src} to {img_dst}")
                        shutil.move(img_src, img_dst)
            except:
                pass
                # the duplicate image error that isn't really dealt with by this code.

        if move_first:
            # no need to do anyth else.
            return
            
        print(f"{len(list(move_list))} images found with the tag(s) {no_tags}.")
        
        # Move
        for id in list(move_list):
            img_src = os.path.join(src, img_filenames[id])
            img_dst = os.path.join(dst, img_filenames[id])
            print(f"Moving {img_src} to {img_dst}")
            shutil.move(img_src, img_dst)