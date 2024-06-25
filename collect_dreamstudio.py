import os
import io
import glob
import warnings
import numpy as np
from PIL import Image
from stability_sdk import client
import argparse
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

parser = argparse.ArgumentParser(description="Generate images from text.")
parser.add_argument(
    "phase", type=str, help='What is the stage? ["test", "text", "image"]'
)
args = parser.parse_args()

phase = args.phase
DIR = "art_2500"

# Our Host URL should not be prepended with "https" nor should it have a trailing slash.
os.environ["STABILITY_HOST"] = "grpc.stability.ai:443"

# Sign up for an account at the following link to get an API Key.
# https://platform.stability.ai/

# Click on the following link once you have created an account to be taken to your API Key.
# https://platform.stability.ai/account/keys

# Paste your API Key below.
os.environ["STABILITY_KEY"] = "Replace with your own API key"

# Set up our connection to the API.
stability_api = client.StabilityInference(
    key=os.environ["STABILITY_KEY"],  # API Key reference.
    verbose=True,  # Print debug messages.
    engine="stable-diffusion-xl-1024-v1-0",  # Set the engine to use for generation.
    # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
)


def text_to_images(image, text, path, success_count, fail_count):
    # Set up our initial generation parameters.
    width, height = 1024, 1024  # image.size
    try:
        answers = stability_api.generate(
            prompt=text,
            seed=4253978046,  # If a seed is provided, the resulting generated image will be deterministic.
            # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
            # Note: This isn't quite the case for Clip Guided generations, which we'll tackle in a future example notebook.
            steps=50,  # Amount of inference steps performed on image generation. Defaults to 30.
            cfg_scale=8.0,  # Influences how strongly your generation is guided to match your prompt.
            # Setting this value higher increases the strength in which it tries to match your prompt.
            # Defaults to 7.0 if not specified.
            width=width,  # Generation width, defaults to 512 if not included.
            height=height,  # Generation height, defaults to 512 if not included.
            samples=1,  # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M,  # Choose which sampler we want to denoise our generation with.
            # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
            # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )
    except Exception as e:
        fail_count += 1
        print("FAILED: {}".format(e))
        return success_count, fail_count

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated images.
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again."
                )
                fail_count += 1
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img_path = path  # os.path.join(path.split(".")[0], str(artifact.seed) + ".png")
                img.save(img_path)
                success_count += 1

    return success_count, fail_count


def image_to_image(image, text, path, success_count, fail_count):
    # Set up our initial generation parameters.
    width, height = 1024, 1024  # image.size
    # resize the image to 512x512
    image = image.resize((width, height), Image.LANCZOS)
    # image.save("./temp.png")
    try:
        answers2 = stability_api.generate(
            prompt=text,
            init_image=image,  # Assign our previously generated img as our Initial Image for transformation.
            start_schedule=0.5,  # Set the strength of our prompt in relation to our initial image.
            seed=123463446,  # If attempting to transform an image that was previously generated with our API,
            # initial images benefit from having their own distinct seed rather than using the seed of the original image generation.
            steps=50,  # Amount of inference steps performed on image generation. Defaults to 30.
            cfg_scale=7.0,  # Influences how strongly your generation is guided to match your prompt.
            # Setting this value higher increases the strength in which it tries to match your prompt.
            # Defaults to 7.0 if not specified.
            width=width,  # Generation width, defaults to 512 if not included.
            height=height,  # Generation height, defaults to 512 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M,  # Choose which sampler we want to denoise our generation with.
            # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
            # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )
    except Exception as e:
        fail_count += 1
        print("FAILED: {}".format(e))
        return success_count, fail_count

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated image.
    for resp in answers2:
        # print(resp)
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again."
                )
                fail_count += 1
            if artifact.type == generation.ARTIFACT_IMAGE:
                img2 = Image.open(io.BytesIO(artifact.binary))
                img2_path = path  # os.path.join(path.split(".")[0], str(artifact.seed) + ".png")
                img2.save(img2_path)
                success_count += 1

    return success_count, fail_count


if __name__ == "__main__":
    images = glob.glob("./select_data/{}/*.jpg".format(DIR)) + glob.glob(
        "./select_data/{}/*.png".format(DIR)
    )
    images = sorted(images)
    texts = glob.glob("./select_data/{}/*.txt".format(DIR))
    texts = sorted(texts)
    if not os.path.exists("./scrape_text2image"):
        os.mkdir("./scrape_text2image")
    if not os.path.exists("./scrape_image2image"):
        os.mkdir("./scrape_image2image")
    if not os.path.exists("./scrape_text2image/dreamstudio"):
        os.mkdir("./scrape_text2image/dreamstudio")
    if not os.path.exists("./scrape_image2image/dreamstudio"):
        os.mkdir("./scrape_image2image/dreamstudio")

    success_count1, fail_count1 = 0, 0
    success_count2, fail_count2 = 0, 0

    assert len(images) == len(texts)
    for i in range(len(images)):
        if phase == "test":
            i = int(np.random.randint(0, len(images)))
        print("Working on the {}th image.".format(i))
        image = Image.open(images[i])
        text = open(texts[i], "r").read()

        ori_dir = images[i].split("/")[-2]
        ori_image_name = images[i].split("/")[-1]
        ori_text_name = texts[i].split("/")[-1]
        assert ori_image_name.split(".")[0] == ori_text_name.split(".")[0]

        path1 = "./scrape_text2image/dreamstudio/{}".format(ori_dir)
        path2 = "./scrape_image2image/dreamstudio/{}".format(ori_dir)
        if not os.path.exists(path1):
            os.mkdir(path1)
        if not os.path.exists(path2):
            os.mkdir(path2)

        text2image_path = os.path.join(path1, ori_image_name)
        image2image_path = os.path.join(path2, ori_image_name)

        if phase == "test":
            success_count1, fail_count1 = text_to_images(
                image, text, text2image_path, success_count1, fail_count1
            )
            success_count2, fail_count2 = image_to_image(
                image, text, image2image_path, success_count2, fail_count2
            )
            break
        elif phase == "text":
            if os.path.exists(text2image_path):
                print("File already exists!")
                continue
            success_count1, fail_count1 = text_to_images(
                image, text, text2image_path, success_count1, fail_count1
            )
        elif phase == "image":
            if os.path.exists(image2image_path):
                print("File already exists!")
                continue
            success_count2, fail_count2 = image_to_image(
                image, text, image2image_path, success_count2, fail_count2
            )
        else:
            raise ValueError("Invalid phase.")

    if phase == "test" or phase == "text":
        print(
            "DREAM: Success count for text2image: {}, fail count: {}".format(
                success_count1, fail_count1
            )
        )
    if phase == "test" or phase == "image":
        print(
            "DREAM: Success count for image2image: {}, fail count: {}".format(
                success_count2, fail_count2
            )
        )
