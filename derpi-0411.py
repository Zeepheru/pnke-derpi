import requests
import os
import re
import json
import urllib


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
    def __init__(self) -> None:
        pass


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
    
    def getImageDownload(self, id):
        """
        inputs id
        returns the url of the full downloadable image

        There's other info but hey I only need the link.
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
        print("Posting: "+url)
        r_json = self.get(
            url=url,
            printJson=False
        )

        return r_json["image"]["representations"]["full"]
    
    def imageSearch(self, q="safe", sd="first_seen_at", sf="desc", n_get=50, per_page=50):
        """
        The Big one. Searches using the tags
        query is "q"

        NOTE:
        I have no procedure for filter_id's 
        56027 is "everything". That's the default for now.

        https://derpibooru.org/search?q=marble+pie%2C+score.gte%3A400%2C+safe

        As for sd and sf:
        default for sd is first_seen_at
        default for sf is desc

        -----
        n_get: number of images to get
        default=50 (1 max page)
        0 is no limit (WARNING: lag though)
        """
        api_path = r'/api/v1/json/search/images'
        n_iter = int(n_get / per_page)
        list_of_images = []

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

            ## get list of images, in order
            list_of_images += [image["id"] for image in r_json["images"]]

        list_of_images = list_of_images[:n_get]
        # print(list_of_images)
        # print(len(list_of_images))

        return list_of_images

####
def main():
    derp = derpi()

    

    imgList = derp.imageSearch(q="artist:marsminer, explicit, score.gte:100", sd="score", n_get=20)
    for imgId in imgList:
        print(derp.findThatFileName(imgId))
    # print(derp.getImageDownload(2836500))
    # print(derp.findThatFileName(2393347))

    # derp.get(derp.combineApiUrl("/api/v1/json/filters/56027"), printJson=True)


if __name__ == "__main__":
    main()