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
    Create the mane6-1200 dataset

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

    dataset_name = "mane6-1200"
    general_tag_string = "!clothes"
    min_score = 200
    max_score = 750

    images_per_char = 200 # total of 1200

    ##
    derp = derpi()

    dl_list = {}
    for pony in mane6:
        print("Querying for tag: `{}`".format(pony))

        pony_query = createDerpiSearchQuery(min_score=min_score, max_score=max_score, 
            yes_tags=[pony], no_tags=[horse for horse in mane6 if horse != pony], tag_string=general_tag_string)

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


######
def main():
    mane6()

if __name__ == '__main__':
    main()