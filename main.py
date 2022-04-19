from derpi import *

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
            "dl":r["dl"],
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

def mane6():
    """
    Create the mane6-3000 dataset

    Potentially add functionality to iterate through a list of characters
    """
    mane6 = [
        "twilight sparkle",
        "fluttershy",
        "rainbow dash", 
        "applejack",
        "pinkie pie", 
        "rarity"
    ] # /)

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
    mane6 = [
        "twilight sparkle",
        "fluttershy",
        "rainbow dash", 
        "applejack",
        "pinkie pie", 
        "rarity"
    ] # /)

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

######
def main():
    mane6TestSet()

if __name__ == '__main__':
    main()