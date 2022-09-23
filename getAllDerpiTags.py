import enum
from derpidatabase import *
from derpi import *

"""
Proof of concept simple script
"""

def main():
    derp = derpi(local_sql_db=True, prefer_local=True, debug=True) 

    # get tags
    allTheTags = derp.tagsSearch(q="*", n_get = 25000) # 500 pages worth, by then the tags are well into single digits.

    total = len(allTheTags)

    # udpate tags
    for i, tagResponse in enumerate(allTheTags):
        i += 1
        print(f"{i}/{total}.")
        derp.db.updateTags(tagResponse, overwrite=True, commit=True)


if __name__ == "__main__":
    main()