import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import glob
import os
import numpy as np
import argparse
import urllib
import requests

EMAIL = "Replace with your own email"
PASSWORD = "Replace with your own password!"
DATASET = "art"
options = uc.ChromeOptions()
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
options.headless = False
driver = uc.Chrome(options=options)
driver.get("https://discord.com/channels/1163581652409262250/1165910951325880401")
time.sleep(3)

parser = argparse.ArgumentParser(description="Generate images from text.")
parser.add_argument(
    "phase", type=str, help='What is the stage? ["test", "text", "image"]'
)
args = parser.parse_args()

phase = args.phase
DIR = "art_2500"


def login(driver):
    email_input = driver.find_element(By.CSS_SELECTOR, "input#uid_5")
    email_input.send_keys(EMAIL)

    password_input = driver.find_element(By.CSS_SELECTOR, "input#uid_7")
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "button.marginBottom8_f4aae3")
    login_button.click()


def text_to_images(driver, image, text, path, success_count, fail_count):
    old_id = None
    fail_times = 0

    while True:
        try:
            input_element = driver.find_element(
                By.CSS_SELECTOR,
                'div[role="textbox"][contenteditable="true"][data-slate-editor="true"]',
            )
            break
        except:
            print(
                "Failed to find the text input element. Paused. Make sure that the text area is visible."
            )
            driver.refresh()
            time.sleep(10)
            continue
            # command = input("Type 'clear' to continue: ")
            # if command.lower() == 'clear':
            #     continue

    input_element.send_keys("/imagine")
    time.sleep(2)
    input_element.send_keys(Keys.SPACE)
    input_element.send_keys(text)
    input_element.send_keys(Keys.ENTER)
    time.sleep(70)
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            break
            # image_url = soup.select_one(f'div#message-accessories-{message_id} .imageWrapper_fd6587.imageZoom_'
            #                             f'ceab9d.clickable_dc48ac.lazyImgContainer__68fa8 a.originalLink__94d5d')['data-safe-src']
            # headers = {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
            #     'Referer': 'http://your-url-here.com',
            # }
            # response = requests.get(image_url, headers=headers)
            # with open(path, 'wb') as file:
            #     file.write(response.content)
            # success_count += 1
        except Exception as e:
            print(
                "Failed to get the 2*2 output. Paused. Please return to the initial state."
            )
            print(e)
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    li_element = driver.find_element(
        By.ID, "chat-messages-1165910951325880401-{}".format(message_id)
    )
    upscale_button = li_element.find_element(By.XPATH, ".//button[.//div[text()='U1']]")
    upscale_button.click()
    time.sleep(5)

    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            image_url = soup.select_one(
                f"div#message-accessories-{message_id} .imageWrapper_fd6587.imageZoom_"
                f"ceab9d.clickable_dc48ac.lazyImgContainer__68fa8 a.originalLink__94d5d"
            )["data-safe-src"]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
                "Referer": "http://your-url-here.com",
            }
            response = requests.get(image_url, headers=headers)
            with open(path, "wb") as file:
                file.write(response.content)
            success_count += 1
            break
        except:
            print(
                "Failed to get the final output. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    time.sleep(1)
    return success_count, fail_count


def image_to_image(driver, image, text, path, success_count, fail_count):
    old_id = None
    fail_times = 0

    while True:
        try:
            file_input = driver.find_element(
                By.CSS_SELECTOR, '.uploadInput_a6be39 input[type="file"]'
            )
            break
        except:
            print(
                "Failed to find the image upload element. Paused. Make sure that the area is visible."
            )
            driver.refresh()
            time.sleep(10)
            continue
            # command = input("Type 'clear' to continue: ")
            # if command.lower() == 'clear':
            #     continue
    file_path = os.path.abspath(image)
    file_input.send_keys(file_path)
    time.sleep(1)

    while True:
        try:
            input_element = driver.find_element(
                By.CSS_SELECTOR,
                'div[role="textbox"][contenteditable="true"][data-slate-editor="true"]',
            )
            break
        except:
            print(
                "Failed to get the output. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    input_element.send_keys(Keys.ENTER)
    time.sleep(5)

    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            upload_image_url = soup.select_one(
                f"div#message-accessories-{message_id} .imageWrapper_fd6587.imageZoom_"
                f"ceab9d.clickable_dc48ac.lazyImgContainer__68fa8 a.originalLink__94d5d"
            )["href"]
            break
        except:
            print(
                "Failed to upload the image. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    while True:
        try:
            input_element = driver.find_element(
                By.CSS_SELECTOR,
                'div[role="textbox"][contenteditable="true"][data-slate-editor="true"]',
            )
            break
        except:
            print(
                "Failed to get the output. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    input_element.send_keys("/imagine")
    time.sleep(2)
    input_element.send_keys(Keys.SPACE)
    input_element.send_keys(upload_image_url)
    time.sleep(1)
    input_element.send_keys(text)
    input_element.send_keys(Keys.ENTER)
    time.sleep(75)

    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            # image_url = soup.select_one(f'div#message-accessories-{message_id} .imageWrapper_fd6587.imageZoom_'
            #                             f'ceab9d.clickable_dc48ac.lazyImgContainer__68fa8 a.originalLink__94d5d')[
            #     'data-safe-src']
            # urllib.request.urlretrieve(image_url, path)
            # success_count += 1
            break
        except:
            print(
                "Failed to get the output. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    li_element = driver.find_element(
        By.ID, "chat-messages-1165910951325880401-{}".format(message_id)
    )
    upscale_button = li_element.find_element(By.XPATH, ".//button[.//div[text()='U1']]")
    upscale_button.click()
    time.sleep(7)

    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            image_url = soup.select_one(
                f"div#message-accessories-{message_id} .imageWrapper_fd6587.imageZoom_"
                f"ceab9d.clickable_dc48ac.lazyImgContainer__68fa8 a.originalLink__94d5d"
            )["data-safe-src"]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
                "Referer": "http://your-url-here.com",
            }
            response = requests.get(image_url, headers=headers)
            with open(path, "wb") as file:
                file.write(response.content)
            success_count += 1
            break
        except:
            print(
                "Failed to get the final output. Paused. Please return to the initial state."
            )
            fail_times += 1
            if fail_times < 2:
                driver.refresh()
                time.sleep(10)
                continue
            else:
                fail_count += 1
                return success_count, fail_count
            # command = input("Type 'clear' to continue.")
            # if command.lower() == 'clear':
            #     return success_count, fail_count

    time.sleep(1)
    return success_count, fail_count


if __name__ == "__main__":
    login(driver)
    user_input = input("Type 'start' to begin scraping: ")
    if user_input.lower() == "start":
        pass
    else:
        raise ValueError("Invalid input.")

    images = glob.glob("./select_data/{}/*.jpg".format(DIR)) + glob.glob(
        "./select_data/{}/*.png".format(DIR)
    )
    images = sorted(images)
    texts = glob.glob("./select_data/{}/*.txt".format(DIR))
    texts = sorted(texts)
    assert len(images) == len(texts)

    if not os.path.exists("./scrape_text2image"):
        os.mkdir("./scrape_text2image")
    if not os.path.exists("./scrape_image2image"):
        os.mkdir("./scrape_image2image")
    if not os.path.exists("./scrape_text2image/midjourney"):
        os.mkdir("./scrape_text2image/midjourney")
    if not os.path.exists("./scrape_image2image/midjourney"):
        os.mkdir("./scrape_image2image/midjourney")

    success_count1, fail_count1 = 0, 0
    success_count2, fail_count2 = 0, 0

    for i in range(len(images)):
        if phase == "test":
            i = int(np.random.randint(0, len(images)))
        print("Working on the {}th image.".format(i))
        image = images[i]
        text = open(texts[i], "r").read()

        ori_dir = images[i].split("/")[-2]
        ori_image_name = images[i].split("/")[-1]
        ori_text_name = texts[i].split("/")[-1]
        assert ori_image_name.split(".")[0] == ori_text_name.split(".")[0]

        path1 = "./scrape_text2image/midjourney/{}".format(ori_dir)
        path2 = "./scrape_image2image/midjourney/{}".format(ori_dir)
        if not os.path.exists(path1):
            os.mkdir(path1)
        if not os.path.exists(path2):
            os.mkdir(path2)

        text2image_path = os.path.join(path1, ori_image_name)
        image2image_path = os.path.join(path2, ori_image_name)

        if phase == "test":
            # success_count1, fail_count1 = text_to_images(driver, image, text, text2image_path, success_count1, fail_count1)
            success_count2, fail_count2 = image_to_image(
                driver, image, text, image2image_path, success_count2, fail_count2
            )
            break
        elif phase == "text":
            if os.path.exists(text2image_path):
                print("File already exists!")
                continue
            success_count1, fail_count1 = text_to_images(
                driver, image, text, text2image_path, success_count1, fail_count1
            )
        elif phase == "image":
            if os.path.exists(image2image_path):
                print("File already exists!")
                continue
            success_count2, fail_count2 = image_to_image(
                driver, image, text, image2image_path, success_count2, fail_count2
            )
        else:
            raise ValueError("Invalid phase.")

    if phase == "test" or phase == "text":
        print(
            "OPENAI: Success count for text2image: {}, fail count: {}".format(
                success_count1, fail_count1
            )
        )
    if phase == "test" or phase == "image":
        print(
            "OPENAI: Success count for image2image: {}, fail count: {}".format(
                success_count2, fail_count2
            )
        )
