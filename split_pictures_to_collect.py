import os
import shutil
from glob import glob


def split_pictures():
    prompts_enhancement_path = "data/prompts_enhancement"
    category_budget = {
        "art": 5000,
        "disaster": 2000,
        "instagram": 2000,
        "news": 2000,
        "pixiv": 2000,
    }
    category_source = {
        "art": "art/art_5400",
        "disaster": "disaster/disaster_3000",
        "instagram": "instagram/instagram_3000",
        "news": "news/news_3000",
        "pixiv": "pixiv/pixiv_3000",
    }
    pictures_suffixes = [".jpg", ".png"]
    description_suffixes = [".txt"]

    for category in category_budget:
        # collect data
        source_folder_path = f"{prompts_enhancement_path}/{category_source[category]}"
        pictures_path = []
        for suffix in pictures_suffixes:
            pictures_path.extend(glob(f"{source_folder_path}/*{suffix}"))
        description_path = []
        for suffix in description_suffixes:
            description_path.extend(glob(f"{source_folder_path}/*{suffix}"))

        # prepare the results folder
        result_folder_path = f"{prompts_enhancement_path}/{category}/{category}_{category_budget[category]}"
        os.makedirs(f"{result_folder_path}", exist_ok=True)

        # make sure pictures are in paired with the description
        pictures_path.sort()
        description_path.sort()
        for i in range(category_budget[category]):
            assert pictures_path[i].split(".")[0] == description_path[i].split(".")[0]

        # save target data
        picture_count, description_count = 0, 0
        for picture in pictures_path[: category_budget[category]]:
            picture_file_name = picture.split("/")[-1]
            shutil.copy(picture, f"{result_folder_path}/{picture_file_name}")
            picture_count += 1
        for description in description_path[: category_budget[category]]:
            description_file_name = description.split("/")[-1]
            shutil.copy(description, f"{result_folder_path}/{description_file_name}")
            description_count += 1

        print(
            f"copy {picture_count} pictures and {description_count} description into {result_folder_path}"
        )


if __name__ == "__main__":
    split_pictures()
