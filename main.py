from imgDl import *
from derpi import *

## these
global mane6, v, derp, debugMode
debugMode = True
v = True
mane6 = [
        "twilight sparkle",
        "fluttershy",
        "rainbow dash", 
        "applejack",
        "pinkie pie", 
        "rarity"
    ] # /)

####

global introMessage, pnkeDerpiVersion 

pnkeDerpiVersion = "0.2.0"

introMessage = f"""
    ____  _   ____ __ ______            ____  __________  ____  ____
   / __ \/ | / / //_// ____/           / __ \/ ____/ __ \/ __ \/  _/
  / /_/ /  |/ / ,<  / __/    ______   / / / / __/ / /_/ / /_/ // /  
 / ____/ /|  / /| |/ /___   /_____/  / /_/ / /___/ _, _/ ____// /   
/_/   /_/ |_/_/ |_/_____/           /_____/_____/_/ |_/_/   /___/   
                                                                    
Fancy ASCII Text Art beacuse...
Version {pnkeDerpiVersion}
"""

######################## 

def randomFun():
    

    imgList = derp.imageSearch(q="artist:marsminer, explicit, score.gte:100", sf="score", n_get=100)
    for imgId in imgList:
        print(derp.findThatFileName(imgId))

def mane6_3000():
    """
    Create the mane6-3000 dataset

    Potentially add functionality to iterate through a list of characters
    """

    dataset_name = "mane6-3000"
    general_tag_string = "!clothes"
    min_score = 200
    max_score = 750
    extra_no_tags = [
        "g5"
    ]

    images_per_char = 500 # total of 3000

    ##
    

    dl_list = {}
    for pony in mane6:
        print("\nQuerying for tag: `{}`".format(pony))

        pony_query = createDerpiSearchQuery(min_score=min_score, max_score=max_score, 
            yes_tags=[pony], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)

        imgList = derp.imageSearch(q=pony_query, sf="score", n_get=images_per_char)
        
        for id in imgList:
            r = derp.getImageInfo(id)
            if r == None:
                continue

            dl_list[id] = {
                "src":r["src"],
                "desired_tags":[tag for tag in r["tags"] if tag in mane6],
                "format":r["format"]
            }

    dl = imgDownloader()
    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400)
    )

def mane6TestSet():
    """
    a mane6TestSet to accompany the main training sets
    (Resized)

    Components (per horse):
    2 safe 75-100
    3 safe 150-200
    3 suggestive 500-600
    2 safe 750-1000

    total of 60
    """

    dataset_name = "mane6-testset-a"
    general_tag_string = "!clothes"
    extra_no_tags = [
        "g5"
    ]


    dl_list = {}
    for pony in mane6:
        print("\nQuerying for tag: `{}`".format(pony))

        # _what is recursion_
        # I'm sorry.

        pony_query_A = createDerpiSearchQuery(min_score=75, max_score=100, 
            yes_tags=[pony, "safe"], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)
        pony_query_B = createDerpiSearchQuery(min_score=150, max_score=200, 
            yes_tags=[pony, "safe"], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)
        pony_query_C = createDerpiSearchQuery(min_score=500, max_score=600, 
            yes_tags=[pony, "suggestive"], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)
        pony_query_D = createDerpiSearchQuery(min_score=750, max_score=1000, 
            yes_tags=[pony, "safe"], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)

        imgList = derp.imageSearch(q=pony_query_A, sf="score", n_get=2) + derp.imageSearch(q=pony_query_B, sf="score", n_get=3) + derp.imageSearch(q=pony_query_C, sf="score", n_get=3) + derp.imageSearch(q=pony_query_D, sf="score", n_get=2) 
        
        for id in imgList:
            r = derp.getImageInfo(id)
            if r == None:
                continue

            dl_list[id] = {
                "dl":r["dl"],
                "desired_tags":[tag for tag in r["tags"] if tag in mane6],
                "format":r["format"]
            }

    dl = imgDownloader()
    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg"
    )

def updateSet(dataset_name="mane6-6000"):
    
    dl = imgDownloader()
    dl_list = {}

    ids = dl.loadFromCSV(filepath=f"{dataset_name}.csv", return_type="df")["id"].tolist()
    print(f"CSV loaded. len = {len(ids)}")

    for i, id in enumerate(ids):

        print(f'Obtaining info for {id} from Derpi [{i+1}/{len(list(ids))}].')
        r = derp.getImageInfo(id)
        if r == None:
            continue

        dl_list[id] = { ## THIS WHOLE SECTION SHOULD JUST BE LOADED FROM the CSV; also hybrid csv+api datasets
            "src":r["src"],
            "fname":r["fname"],
            "desired_tags":[tag for tag in r["tags"] if tag in mane6],
            "format":r["format"]
            }

    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400),
        export_csv=True,
        download_images=False
    )

def hybrid():
    """
    6k boi
    this is a hybrid loading scheme, with both API calls and 
    loading the csv for mane6-3000-v2
    """
    
    dl = imgDownloader()
    dl_list = {}
    dataset_name = "mane6-6000"
    general_tag_string = "!clothes"
    min_score = 100
    max_score = 1000
    extra_no_tags = [
        "g5"
    ]

    dl_list_0 = dl.loadFromCSV(filepath="mane6-3000-v2.csv")
    # print(f"CSV loaded. len = {len(list(dl_list))}")
    # print(dl_list[list(dl_list)[0]])

    # now we have the initial 3000 images
    # and because I'm lazy, the way I'll do it is to:
    # do the API search calls for all 6000, but check if the image is already in dl_list
    # if so, don't individually query

    images_per_char = 1000 # total of 6000

    for pony in mane6:
        print("\nQuerying for tag: `{}`".format(pony))

        pony_query = createDerpiSearchQuery(min_score=min_score, max_score=max_score, 
            yes_tags=[pony], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)

        imgList = derp.imageSearch(q=pony_query, sf="random", n_get=images_per_char) # random now
        
        for i, id in enumerate(imgList):
            if id not in list(dl_list_0):
                if v: 
                    print(f'Obtaining {id} from Derpi [{i+1}/{len(list(imgList))}].')

                r = derp.getImageInfo(id)
                if r == None:
                    continue
                
                dl_list[id] = {
                    "src":r["src"],
                    "desired_tags":[tag for tag in r["tags"] if tag in mane6],
                    "format":r["format"],
                    "fname":r["fname"]
                }
            elif id in list(dl_list_0):
                if v: 
                    print(f'Obtaining {id} from CSV [{i+1}/{len(list(imgList))}].')

                dl_list[id] = { #prolly works
                    "src":dl_list_0[id]["src"],
                    "desired_tags":[dl_list_0[id]["tag"]],
                    "format":dl_list_0[id]["format"],
                    "fname":dl_list_0[id]["fname"]
                }
            else:
                print(f'What the fuck: {id} - this is impossible.')

    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=False,
        new_format="jpg",
        new_size=(400,400)
    )

def getSpecificNumber():
    """
    Generally used to create test sets while checking if the image is in another dataset
    to reach a certain number of images.

    (NOT UPDATED TO THE BETTER TEMPLATE)
    """

    
    dl = imgDownloader()
    dataset_name = "milk-test-alpha"

    general_tag_string = "!clothes"
    min_score = 100
    max_score = 1000
    extra_no_tags = [
        "g5"
    ]

    # dl_list = dl.loadFromCSV(filepath="mane6-testset-a-rs400.csv")
    dl_list = {}
    no_ids = dl.loadFromCSV(filepath="milk-beta.csv", return_type="df")["id"].tolist() # already in m6-6000
    desired_no_per_char = 10 # each

    for pony in mane6:
        print("\nQuerying for tag: `{}`".format(pony))

        pony_query = createDerpiSearchQuery(min_score=min_score, max_score=max_score, 
            yes_tags=[pony] + ["explicit"], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, 
            tag_string=general_tag_string, sfw=False)

        imgList = derp.imageSearch(q=pony_query, sf="random", n_get=50) # random now
        # I've not put in an actual method to do the numbers properly, so here's just 50 and I'll cut it down to 

        n = 0

        for i, id in enumerate(imgList):
            if n >= desired_no_per_char:
                break

            if id in no_ids:
                # don't want the image
                continue

            if v: 
                print(f'Obtaining {id} from Derpi [{n+1}/{desired_no_per_char}].')

            r = derp.getImageInfo(id)
            if r == None:
                continue
            
            dl_list[id] = {
                "src":r["src"],
                "desired_tags":[tag for tag in r["tags"] if tag in ["safe", "explicit"]],
                "format":r["format"],
                "fname":r["fname"]
            }

            n += 1

    ### loadsafeimages (from m6-3000-v2), just ids beacuse I dont want to deal with bugs
    df = dl.loadFromCSV(filepath=f"mane6-3000-v2.csv", return_type="df")

    df["desired_tags"] = df["desired_tags"].apply(lambda x:str(x))  # ashdjhsbvkjhszbcjhsbdfc
    df["desired_tags"] = df["desired_tags"].apply(lambda x:re.sub(r"'|\[|\]", '', x))

    for pony in mane6:
        pony_df = df.loc[df["desired_tags"] == pony].head(desired_no_per_char)
        for n, id in enumerate(pony_df['id'].tolist()):
            # lmao

            print(f'Obtaining {id} from Derpi [{n+1}/{desired_no_per_char}].')

            r = derp.getImageInfo(id)
            if r == None:
                continue
            
            dl_list[id] = {
                "src":r["src"],
                "desired_tags":[tag for tag in r["tags"] if tag in ["safe", "explicit"]],
                "format":r["format"],
                "fname":r["fname"]
            }

    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400),
        export_csv=True
    )

def csvCloppity(dataset_name="", score = (100, 1000), desired_tags=[], max_images=0, load_backup=True):
    """
    The most well-written function for dataset creation, use this as a template

    Backup is in the form of a json because I can't be arsed to write conversion code

    TODO JSON OR CSV YA DUM DUM ???!!!!!
    TODO also write some better explanations in this 
    """
    if dataset_name == "": 
        print("Dataset name is empty. Exiting")
        return False
    elif desired_tags == [] or type(desired_tags).__name__ != 'list':
        print("Desired tags is empty or not a list. Exiting")
        return False

    ## basic init for stuffffs
    dl = imgDownloader()

    # no "pony query" as loading from local csv's for this
    csv_files_to_load = [
        "mane6-6000.csv",
        "mane6-3000-v2.csv"
    ]
    # otherwise the pony query code goes in here

    # no dedicated test set yet
    ## creating the ids list 
    ids = []
    for f in csv_files_to_load:
        ids += dl.loadFromCSV(filepath=f, return_type="df")["id"].tolist()
    ##

    print(f"Length of Ids: {len(ids)}")
    if max_images == 0:
        max_images = len(ids)

    imgs_api_not_needed = [] # images already in backup 
    dl_list = {}
    if load_backup:
        try:
            dl_list = dl.loadFromCSV(filepath="backup.csv", return_type="dict")
            imgs_api_not_needed = list(dl_list)
            print("INFO - Successfully loaded from backup.json")
        except:
            pass # just pass

    for i, id in enumerate(ids):
        if i == max_images:
            # more than the max images
            break
        elif id in imgs_api_not_needed:
            print(f'{id} Loaded from backup [{i+1}/{min(len(list(ids)), max_images)}].')
            continue
        
        try:
            print(f'Obtaining info for {id} from Derpi [{i+1}/{min(len(list(ids)), max_images)}].')
            r = derp.getImageInfo(id) # get INFO
            if r == None: 
                # for shit
                continue

            dl_list[id] = { 
                "src":r["src"],
                "fname":r["fname"],
                "desired_tags":[tag for tag in r["tags"] if tag in desired_tags], # ja
                "format":r["format"]
                }

        except Exception as e:
            # likely some form of network error
            print(e)
            # export the backup json
            print(f"INFO - dl_list creation exited. Creating backup.json at {dl.def_path}")
            dl.writeJson(dl_list, os.path.join(dl.def_path, "backup.json"))
            return False

    del r # hmm

    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400), # keeping it at 400 for now, details amirite
        export_csv=True,
        download_images=False
    ) 

def modifyCloppity(dataset_name="", score = (100, 1000), desired_tags=[], max_images=0, load_backup=True):
    """
    https://towardsdatascience.com/dealing-with-list-values-in-pandas-dataframes-a177e534f173
    """
    if dataset_name == "": 
        print("Dataset name is empty. Exiting")
        return False
    elif desired_tags == [] or type(desired_tags).__name__ != 'list':
        print("Desired tags is empty or not a list. Exiting")
        return False

    ## basic init for stuffffs
    
    dl = imgDownloader()

    df = dl.loadFromCSV(filepath="milk-naught.csv", return_type="df")
    
    ### 
    df = df.sample(frac=1) # SHUFFLE

    ## current super crummy method of JUST CONVERT TO STRINGS
    df["desired_tags"] = df["desired_tags"].apply(lambda x:str(x)) 
    df["desired_tags"] = df["desired_tags"].apply(lambda x:re.sub(r"'|\[|\]", '', x))
    ##
    
    ## gets 950 of both explicit and safe
    df_safe = df.loc[df["desired_tags"] == "safe"].head(950)
    df_explicit = df.loc[df["desired_tags"] == "explicit"].head(950)
    # print(type(df.loc[df["id"] == 2512202]["tags"].item()))
    # print(df.loc[df["id"] == 2512202]["tags"].item())
    # print(df_safe.head)
    # print(df_explicit.head)

    dl.fullDownload(
        dl_list=pd.concat([df_safe, df_explicit]),
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400), 
        export_csv=True,
        download_images=True
    ) 

######
def mainOne():
    a = derp.tagsSearch(q="*", n_get = 0)
    
    # print(len(a))

    "To keep the functions and all the arguments without running time for peak laziness:"
    return "No :D"

    modifyCloppity(
        dataset_name="milk-beta",
        desired_tags=["safe", "suggestive", "questionable", "explicit", "grimdark", "semi-grimdark"],
        score=(100, 1000), # not needed but anyway
        max_images=0, # no DEBUG
        load_backup=False
    )

def lull():
    """
    Something something move images...

    """
    dl = imgDownloader()
    dl.quarantine(src="derpi-imgs", dst="derpi-imgs-nsfw", no_tags=["explicit"], move_first=True)
    # it works, just remember to remove the break

#### DONT TOUCHY TOUCH
def main():
    global derp
    """
    Actual main function that runs the actual desired other functions. Sets up Derpi and the intro message.
    """
    if debugMode:
        introMessage = f"""
PNKE-Derpibooru V {pnkeDerpiVersion} 
  ___  ___ ___ _   _  ___   __  __  ___  ___  ___ 
 |   \| __| _ ) | | |/ __| |  \/  |/ _ \|   \| __|
 | |) | _|| _ \ |_| | (_ | | |\/| | (_) | |) | _| 
 |___/|___|___/\___/ \___| |_|  |_|\___/|___/|___| , aka print() mode.
                                                  
Remember to set debugMode to False if this is not desired.
        """
        
    print(introMessage)
    derp = derpi(local_sql_db=True, prefer_local=True, debug=debugMode) 
    ###
    # << functions are below >>
    mainOne()

if __name__ == '__main__':

    main()