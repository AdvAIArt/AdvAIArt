import base64
import os
import requests
import time
import argparse


def image_to_base64(image_path):
    """Convert image to Base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def safe_request(url, method="get", retries=3, **kwargs):
    """Perform a network request safely, with retries and exception handling."""
    for attempt in range(retries):
        try:
            if method == "get":
                response = requests.get(url, **kwargs)
            elif method == "post":
                response = requests.post(url, **kwargs)
            else:
                raise ValueError("Unsupported method")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(
                f"Request error ({e}), attempt {attempt + 1} of {retries}. Retrying..."
            )
            time.sleep(10)  # Wait for 10 seconds before retrying
    return None


def generate_image_from_text(api_key, input_folder, output_folder):
    text_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-Key": api_key,
    }

    for text_file in text_files:
        text_file_path = os.path.join(input_folder, text_file)
        image_file_name = os.path.splitext(text_file)[0] + ".png"
        image_file_path = os.path.join(output_folder, image_file_name)

        if os.path.isfile(image_file_path):
            print(f"Image {image_file_name} already exists, skipping {text_file}")
            continue

        with open(text_file_path, "r") as file:
            prompt_text = file.read().strip()

        payload = {
            "model": "photography",
            "aspectRatio": "square",
            "highResolution": True,
            "images": 1,
            "steps": 150,
            "initialImageMode": "color",
            "prompt": prompt_text,
        }

        response = safe_request(
            "https://api.starryai.com/creations/",
            method="post",
            json=payload,
            headers=headers,
        )
        if response:
            creation_response = response.json()
            creation_id = creation_response.get("id")
            if not creation_id:
                print(f"Unable to create artwork for {text_file}, skipping.")
                continue

            status = creation_response.get("status", "")
            time.sleep(10)
            while status != "completed":
                check_response = safe_request(
                    f"https://api.starryai.com/creations/{creation_id}", headers=headers
                )
                if check_response:
                    check_response_data = check_response.json()
                    status = check_response_data.get("status", "")
                    if status == "completed":
                        time.sleep(20)
                        image_url = check_response_data["images"][0]["url"]
                        image_data = requests.get(image_url).content
                        with open(image_file_path, "wb") as f:
                            f.write(image_data)
                        print(f"Image {image_file_name} has been saved.")
                        break
                    elif status == "failed":
                        print(f"Artwork creation failed for {text_file}, skipping.")
                        break
                else:
                    print("Unable to get status update, ending task.")
                    break
        else:
            print("Request failed or no response, skipping this file.")


def generate_image_from_image(api_key, input_folder, output_folder):
    all_files = os.listdir(input_folder)
    text_files = [f for f in all_files if f.endswith(".txt")]

    for text_file in text_files:
        text_file_path = os.path.join(input_folder, text_file)
        base_name = os.path.splitext(text_file)[0]
        image_file = next(
            (
                f
                for f in all_files
                if f.startswith(base_name)
                and f.split(".")[-1] in ["jpg", "png", "webp", "jpeg"]
            ),
            None,
        )

        if image_file:
            image_file_path = os.path.join(input_folder, image_file)
            output_image_path = os.path.join(output_folder, base_name + ".png")

            if os.path.isfile(output_image_path):
                print(f"Image {output_image_path} already exists, skipping {text_file}")
                continue

            initial_image_encoded = image_to_base64(image_file_path)

            with open(text_file_path, "r") as file:
                prompt_text = file.read().strip()

            payload = {
                "model": "anime",
                "aspectRatio": "square",
                "highResolution": True,
                "images": 1,
                "steps": 50,
                "initialImageMode": "color",
                "initialImageEncoded": initial_image_encoded,
                "prompt": prompt_text,
                "initialImageStrength": 50,
            }

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-API-Key": api_key,
            }

            response = safe_request(
                "https://api.starryai.com/creations/",
                method="post",
                json=payload,
                headers=headers,
            )
            if response:
                creation_response = response.json()
                creation_id = creation_response.get("id")
                if not creation_id:
                    print(f"Unable to create artwork for {text_file}, skipping.")
                    continue

                status = creation_response.get("status", "")
                time.sleep(10)
                while status != "completed":
                    check_response = safe_request(
                        f"https://api.starryai.com/creations/{creation_id}",
                        headers=headers,
                    )
                    if check_response:
                        check_response_data = check_response.json()
                        status = check_response_data.get("status", "")
                        if status == "completed":
                            time.sleep(20)
                            image_url = check_response_data["images"][0]["url"]
                            image_data = requests.get(image_url).content
                            with open(output_image_path, "wb") as f:
                                f.write(image_data)
                            print(f"Image {output_image_path} has been saved.")
                            break
                        elif status == "failed":
                            print(f"Artwork creation failed for {text_file}, skipping.")
                            break
                    else:
                        print("Unable to get status update, ending task.")
                        break
            else:
                print("Request failed or no response, skipping this file.")


def generate_test_images(api_key, input_folder, output_folder):
    generate_image_from_text(api_key, input_folder, output_folder)
    generate_image_from_image(api_key, input_folder, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StarryAI Image Generation Script")
    parser.add_argument("mode", choices=["test", "text", "image"], help="Run mode")
    parser.add_argument("--api_key", required=True, help="StarryAI API Key")
    parser.add_argument("--input_folder", help="Input folder path")
    parser.add_argument("--output_folder", help="Output folder path")

    args = parser.parse_args()

    if args.mode == "test":
        if not args.input_folder or not args.output_folder:
            print("Test mode requires input and output folder paths.")
        generate_test_images(args.api_key, args.input_folder, args.output_folder)
    elif args.mode == "text":
        if not args.input_folder or not args.output_folder:
            print("Text generation mode requires input and output folder paths.")
        generate_image_from_text(args.api_key, args.input_folder, args.output_folder)
    elif args.mode == "image":
        if not args.input_folder or not args.output_folder:
            print("Image generation mode requires input and output folder paths.")
        generate_image_from_image(args.api_key, args.input_folder, args.output_folder)
