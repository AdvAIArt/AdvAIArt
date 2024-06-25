# Art: {author}, art
# Disaster: Photography, disaster, incident, realistic
# News: Photography, news, realistic
# Instagram: Instagram posts, lifestyle
# Pixiv: Pixiv style, anime

# remove asepct ratio at the end like "--ar 2:3"

import glob
import os

DATASET = "news"
txt_data = glob.glob("./select_data/{}/*.txt".format(DATASET))
txt_data = sorted(txt_data)
invalid = 0
for item in txt_data:
    with open(item, "r") as f:
        text = f.read()
    f.close()

    if len(text.split("\n")) % 4 != 0 or text.startswith("We're sorry"):
        os.system("rm {}".format(item))
        # os.system("rm {}".format(item.replace("art", "art_gpt")))
        print(item)
        print(text)
        invalid += 1
        print("Removed {}. Total removed: {}".format(item, invalid))
        continue




