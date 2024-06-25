import utils

import random
import logging
import os
import base64
import openai
import shutil

from PIL import Image
from glob import glob


def text_to_images(logger, client, text_content, dest_image_path):
    success, error = 1, None
    try:
        response = client.images.generate(
            model="dall-e-3", prompt=text_content, response_format="b64_json"
        )

        image_data = base64.b64decode(response.data[0].b64_json)
        with open(dest_image_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        success = 0
        error = format(e)
        logger.error(f"{error}")

    return success, error


def image_to_image(logger, client, source_image_path, dest_image_path):
    success, error = 1, None
    # compress the picture to match OpenAI's limit
    compressed_picture = Image.open(source_image_path)
    compressed_picture.convert("RGBA").save("data/temp.png", format="png", quality=20)

    try:
        response = client.images.create_variation(
            image=open("data/temp.png", "rb"), response_format="b64_json"
        )

        image_data = base64.b64decode(response.data[0].b64_json)
        with open(dest_image_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        success = 0
        error = format(e)
        logger.error(f"{error}")

    return success, error


def get_pictures_and_description(
    logger: logging, category_budget: dict, input_folder: str
) -> tuple[dict, dict]:
    pictures_suffixes = ["jpg", "png"]
    description_suffixes = ["txt"]
    pictures_path, description_path = {}, {}

    for category in category_budget:
        category_folder = (
            f"{input_folder}/{category}/{category}_{category_budget[category]}"
        )
        pictures_path[category], description_path[category] = [], []

        for suffix in pictures_suffixes:
            pictures_path[category].extend(glob(f"{category_folder}/*.{suffix}"))
            pictures_path[category].sort()

        for suffix in description_suffixes:
            description_path[category].extend(glob(f"{category_folder}/*.{suffix}"))
            description_path[category].sort()

        logger.info(
            f"{category} has {len(pictures_path[category])} pictures and description"
        )

    logger.debug(f"pictures_path: {pictures_path}")
    logger.debug(f"description_path: {description_path}")
    return pictures_path, description_path


def handle_existed_pictures(
    logger: logging,
    category_budget: dict,
    pictures_path: dict,
    description_path: dict,
    output_folder_from_text: str,
    output_folder_from_image: str,
) -> tuple[dict, dict]:
    exist_pictures_suffixes = ["jpg", "png"]
    filtered_pictures_path, filtered_description_path = {}, {}
    for category in category_budget:
        filtered_pictures_path[category] = []
        filtered_description_path[category] = []

        exist_pictures_path_from_text = []
        for suffix in exist_pictures_suffixes:
            exist_pictures_path_from_text.extend(
                glob(
                    f"{output_folder_from_text}/*{category}*/*{suffix}",
                    recursive=True,
                )
            )
        exist_pictures_name_from_text = [
            image.split("/")[-1] for image in exist_pictures_path_from_text
        ]

        exist_pictures_path_from_image = []
        for suffix in exist_pictures_suffixes:
            exist_pictures_path_from_image.extend(
                glob(
                    f"{output_folder_from_image}/*{category}*/*{suffix}",
                    recursive=True,
                )
            )
        exist_pictures_name_from_image = [
            image.split("/")[-1] for image in exist_pictures_path_from_image
        ]

        for i in range(len(pictures_path[category])):
            picture_name = pictures_path[category][i].split("/")[-1]
            if (
                picture_name in exist_pictures_name_from_text
                and picture_name in exist_pictures_name_from_image
            ):
                for path in glob(
                    f"{output_folder_from_text}/*{category}*/{picture_name}",
                    recursive=True,
                ):
                    if path.split("/")[-2] != f"{category}_{category_budget[category]}":
                        shutil.copy(
                            path,
                            f"{output_folder_from_text}/{category}_{category_budget[category]}/",
                        )
                        break

                for path in glob(
                    f"{output_folder_from_image}/*{category}*/{picture_name}",
                    recursive=True,
                ):
                    if path.split("/")[-2] != f"{category}_{category_budget[category]}":
                        shutil.copy(
                            path,
                            f"{output_folder_from_image}/{category}_{category_budget[category]}/",
                        )
                        break
            else:
                filtered_pictures_path[category].append(pictures_path[category][i])
                filtered_description_path[category].append(
                    description_path[category][i]
                )

        logger.info(
            f"{category} has {len(filtered_pictures_path[category])} filtered pictures and description"
        )

    logger.debug(f"filtered_pictures_path: {filtered_pictures_path}")
    logger.debug(f"filtered_description_path: {filtered_description_path}")
    return filtered_pictures_path, filtered_description_path


if __name__ == "__main__":
    input_folder = "data/prompts_enhancement"
    output_folder_from_text = f"results/scrape_text2image/openai"
    output_folder_from_image = f"results/scrape_image2image/openai"
    category_budget = {
        "art": 500,
        "disaster": 500,
        "instagram": 500,
        "news": 500,
        "pixiv": 500,
    }

    args = utils.get_argparser()
    logger = utils.get_file_and_console_logger(args)

    for category in category_budget:
        os.makedirs(
            f"{output_folder_from_text}/{category}_{category_budget[category]}",
            exist_ok=True,
        )
        os.makedirs(
            f"{output_folder_from_image}/{category}_{category_budget[category]}",
            exist_ok=True,
        )

    pictures_path, description_path = get_pictures_and_description(
        logger, category_budget, input_folder
    )

    filtered_pictures_path, filtered_description_path = handle_existed_pictures(
        logger,
        category_budget,
        pictures_path,
        description_path,
        output_folder_from_text,
        output_folder_from_image,
    )

    total_count = 0
    for category in category_budget:
        total_count += len(filtered_pictures_path[category])

    success_count_from_text, fail_count_from_text = 0, 0
    success_count_from_image, fail_count_from_image = 0, 0

    client = openai.OpenAI(api_key="Replace with your own API key")
    failed_pictures = []
    for category in category_budget:
        for i in range(len(filtered_pictures_path[category])):
            if args.phase == "test":
                i = random.randrange(0, len(filtered_pictures_path))
                logger.info(f"test the program with {i}th file")
            else:
                logger.info(
                    f"{category}[{i:4}/{len(filtered_pictures_path[category]):4}->{total_count:5}] {fail_count_from_text} text-fail and {fail_count_from_image} image-fail"
                )
                total_count -= 1

            picture_path = filtered_pictures_path[category][i]
            description_content = open(
                filtered_description_path[category][i], "r"
            ).read()

            picture_name = picture_path.split("/")[-1]

            save_folder_from_text = (
                f"{output_folder_from_text}/{category}_{category_budget[category]}"
            )
            save_folder_from_image = (
                f"{output_folder_from_image}/{category}_{category_budget[category]}"
            )

            save_path_from_text = f"{save_folder_from_text}/{picture_name}"
            save_path_from_image = f"{save_folder_from_image}/{picture_name}"

            if args.phase == "test" or args.phase == "text" or args.phase == "both":
                success, error = text_to_images(
                    logger, client, description_content, save_path_from_text
                )
                success_count_from_text += success == 1
                fail_count_from_text += success == 0
                if success == 0:
                    failed_pictures.append(
                        (
                            category,
                            "text2image",
                            picture_path,
                            description_content,
                            error,
                        )
                    )

            if args.phase == "test" or args.phase == "image" or args.phase == "both":
                success, error = image_to_image(
                    logger, client, picture_path, save_path_from_image
                )
                success_count_from_image += success == 1
                fail_count_from_image += success == 0
                if success == 0:
                    failed_pictures.append(
                        (
                            category,
                            "image2image",
                            picture_path,
                            description_content,
                            error,
                        )
                    )

            if args.phase == "test":
                break

    logger.info(
        f"text  to image: {success_count_from_text:5} success and {fail_count_from_text:5} fail"
    )
    logger.info(
        f"image to image: {success_count_from_image:5} success and {fail_count_from_image:5} fail"
    )
    logger.info(f"OpenAI:failed files: {failed_pictures}")
