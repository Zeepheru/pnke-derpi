from sympy import N
from derpi import *

global mane6, v
v = True
mane6 = [
        "twilight sparkle",
        "fluttershy",
        "rainbow dash", 
        "applejack",
        "pinkie pie", 
        "rarity"
    ] # /)


def randomFun():
    derp = derpi()

    imgList = derp.imageSearch(q="artist:marsminer, explicit, score.gte:100", sf="score", n_get=100)
    for imgId in imgList:
        print(derp.findThatFileName(imgId))

def rdpp():
    """
    Test only. 
    To get 20 ponks images and 20 rd images
    """
    s_query_rd = createDerpiSearchQuery(min_score=200, max_score=750, yes_tags=["rd"], no_tags=["pp","ts","fs"], tag_string="!clothes")
    s_query_pp = createDerpiSearchQuery(min_score=200, max_score=750, yes_tags=["pp"], no_tags=["rd","ts","fs"], tag_string="!clothes")
    desired_tags = ["rainbow dash", "pinkie pie"]

    derp = derpi()

    # rd
    rd_imgList = derp.imageSearch(q=s_query_rd, sf="score", n_get=125)
    dl_list = {}
    for id in rd_imgList:
        r = derp.getImageInfo(id)
        dl_list[id] = {
            "src":r["src"],
            "desired_tags":[tag for tag in r["tags"] if tag in desired_tags],
            "format":r["format"]
        }

    # pp
    pp_imgList = derp.imageSearch(q=s_query_pp, sf="score", n_get=125)
    for id in pp_imgList:
        r = derp.getImageInfo(id)
        if id in list(dl_list):
            print("UHHHHHHHHHHHH" + str(id))

        dl_list[id] = {
            "src":r["src"],
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
    derp = derpi()

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

    ##
    derp = derpi()

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
    derp = derpi()
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
    derp = derpi()
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
    # for a 120-ish img testset
    # 20 per char + testSetA

    derp = derpi()
    dl = imgDownloader()
    dl_list = {}
    dataset_name = "mane6-testset-b-rs400"

    general_tag_string = "!clothes"
    min_score = 100
    max_score = 1000
    extra_no_tags = [
        "g5"
    ]

    dl_list = dl.loadFromCSV(filepath="mane6-testset-a-rs400.csv")
    no_ids = dl.loadFromCSV(filepath="mane6-6000.csv", return_type="df")["id"].tolist() # already in m6-6000
    desired_no_per_char = 20

    for pony in mane6:
        print("\nQuerying for tag: `{}`".format(pony))

        pony_query = createDerpiSearchQuery(min_score=min_score, max_score=max_score, 
            yes_tags=[pony], no_tags=[horse for horse in mane6 if horse != pony] + extra_no_tags, tag_string=general_tag_string)

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
                "desired_tags":[tag for tag in r["tags"] if tag in mane6],
                "format":r["format"],
                "fname":r["fname"]
            }

            n += 1

    dl.fullDownload(
        dl_list=dl_list,
        dir_path=dataset_name,
        start_empty=True,
        new_format="jpg",
        new_size=(400,400),
        export_csv=True
    )

def csvCloppity(dataset_name="", score = (100, 1000), desired_tags=[], max_images=0):
    """
    The most well-written function for dataset creation, use this as a template
    """
    if dataset_name == "": 
        print("Dataset name is empty. Exiting")
        return False
    elif desired_tags == [] or type(desired_tags).__name__ != 'list':
        print("Desired tags is empty or not a list. Exiting")
        return False

    ## basic init for stuffffs
    derp = derpi()
    dl = imgDownloader()
    dl_list = {}

    # no pony qury as loading from local csv's for this
    csv_files_to_load = [
        "mane6-6000.csv",
        "mane6-3000-v2.csv"
    ]

    # no dedicated test set yet
    ## creating the ids list 
    ids = []
    for f in csv_files_to_load:
        ids += dl.loadFromCSV(filepath=f, return_type="df")["id"].tolist()
    ##

    print(f"Length of Ids: {len(ids)}")

    for i, id in enumerate(ids):
        if i == max_images and max_images != 0:
            # more than the max images
            break

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


######
def main():
    modfiyCloppity(
        dataset_name="milk-alpha",
        desired_tags=["safe", "suggestive", "questionable", "explicit", "grimdark", "semi-grimdark"],
        score=(100, 1000), # not needed but anyway
        max_images=0 # no DEBUG
    )

def lull():
    dl = imgDownloader()
    dl.quarantine(src="derpi-imgs",dst="temp-dir",no_tags=["explicit"])
    # it works, just remember to remove the break

if __name__ == '__main__':
    main()