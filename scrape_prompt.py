import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import glob
import os

# DreamStudio: https://beta.dreamstudio.ai/generate
# StarryAI: https://starryai.com/app/my-creations
# Midjourney: https://discord.com/channels/1163581652409262250/1165910994749505626
# ChatGPT: https://chat.openai.com/
EMAIL = "Replace with your own email"
PASSWORD = "Replace with your own password"
DATASET = "pixiv"
LIMIT = 5800
options = uc.ChromeOptions()
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
options.headless = False
driver = uc.Chrome(options=options)
driver.get("https://discord.com/channels/1163581652409262250/1165910994749505626")
time.sleep(3)


def login(driver):
    email_input = driver.find_element(By.CSS_SELECTOR, "input#uid_5")
    email_input.send_keys(EMAIL)

    password_input = driver.find_element(By.CSS_SELECTOR, "input#uid_7")
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "button.marginBottom8_f4aae3")
    login_button.click()


def start_scraping(driver):
    old_id = None
    files = glob.glob(
        os.path.expanduser(
            "/Users/liuzey/PycharmProjects/chatgpt/text2image/select_data/{}/*.png".format(
                DATASET
            )
        )
    ) + glob.glob(
        os.path.expanduser(
            "/Users/liuzey/PycharmProjects/chatgpt/text2image/select_data/{}/*.jpg".format(
                DATASET
            )
        )
    )
    files = sorted(files)
    length = len(files)
    i = 0
    success = 0
    while i < length:
        print("Scraping the {}th image.".format(i))
        file_path = files[i]
        # file_path = "/Users/liuzey/PycharmProjects/chatgpt/text2image/select_data/disaster/01_01_0003.png"
        if file_path.endswith(".png"):
            txt_path = file_path.replace(".png", ".txt")
        else:
            txt_path = file_path.replace(".jpg", ".txt")
        if os.path.exists(txt_path):
            i += 1
            with open(txt_path, "r") as f:
                content = f.read()
            f.close()
            if not content.startswith("We're sorry"):
                success += 1
            continue
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

        input_element.send_keys("/describe")
        time.sleep(2)
        input_element.send_keys(Keys.SPACE)

        while True:
            try:
                # upload a image
                upload_button = driver.find_element(
                    By.CSS_SELECTOR, 'input.fileInput_ed09f4[type="file"]'
                )
                break
            except:
                print(
                    "Failed to find the upload button. Paused. Make sure that the upload button is visible."
                )
                driver.refresh()
                time.sleep(10)
                continue
                # command = input("Type 'clear' to continue: ")
                # if command.lower() == 'clear':
                #     continue

        upload_button.send_keys(file_path)
        input_element.send_keys(Keys.ENTER)
        time.sleep(13)

        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_message = soup.select("li.messageListItem__6a4fb")[-1]
            message_id = last_message["id"].split("-")[-1]  # Extracting the unique ID
            assert message_id != old_id
            old_id = message_id
            output_content = soup.select_one(
                f"div#message-accessories-{message_id} .embedDescription__33443.embedMargin__9576e"
            ).text
        except:
            print(
                "Failed to get the output. Paused. Please return to the initial state."
            )
            driver.refresh()
            time.sleep(10)
            continue
            # command = input("Type 'clear' to refresh and redo. Type 'pass' to pass.")
            # if command.lower() == 'clear':
            #     driver.refresh()
            #     time.sleep(10)
            #     continue
            # if command.lower() == 'pass':
            #     i += 1
            #     continue

        # save_to_text
        with open(txt_path, "a") as f:
            f.write(output_content)
        f.close()
        if not output_content.startswith("We're sorry"):
            success += 1
        if success >= LIMIT:
            break
        i += 1
        print("Suceeded in scraping {} images.".format(success))
        time.sleep(1)

    driver.quit()


if __name__ == "__main__":
    login(driver)
    #                                                                         #
    #                                                                         #
    # ------ Please finish all the preparations before typing 'start'. ------ #
    #                                                                         #
    #                                                                         #
    user_input = input("Type 'start' to begin scraping: ")
    if user_input.lower() == "start":
        start_scraping(driver)
