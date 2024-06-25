# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
import time
import nltk
# from selenium.webdriver.common.keys import Keys
# import lxml
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc
# from lxml import etree
import os
import openai
import glob
# import urllib.request
import json
import threading
# import uuid
import argparse
from multiprocessing import Process

nltk.download('punkt')

parser = argparse.ArgumentParser(description='Generate images from text.')
parser.add_argument('phase', type=str, help='What is the stage? ["test", "main", "redo"]')
args = parser.parse_args()

phase = args.phase
data_dir = "insta"
texts = glob.glob("./select_data/{}/*.txt".format(data_dir))
texts = sorted(texts)

START = 0
LIMIT = len(texts)
BATCH_SIZE = 10
BATCHES = LIMIT // BATCH_SIZE + 1
START_BATCH = START // BATCH_SIZE

openai.api_key = "Replace with your own API key"
PASSED = 0

lock = threading.Lock()


def api_call(index):
    global PASSED
    indi = True
    no_response = 0
    try:
        text = texts[index]
    except:
        return
    save_path = text.replace("{}".format(data_dir), "{}_gpt".format(data_dir))
    if os.path.exists(save_path):
        return

    with open(text, "r") as f:
        words = f.read()
    f.close()

    four_prompts = words.split("\n")
    # print(four_prompts)
    four_prompts = [prompt.split("--ar")[0].replace("in the style of", "") for prompt in four_prompts if prompt != ""]
    words = ";\n".join(four_prompts)
    # inputs = "Given the descriptions of one single photo, combine all the information and generate one " \
    #          "single stable diffusion prompt made of keywords to generate photography. After that, avoid and " \
    #          "remove the artist names, art movements, art styles, and camera models in your prompt. Please only " \
    #          "include your prompt in the answer. \"{}\"".format(words)
    inputs = "Given the descriptions of one single picture, combine all the information and generate one " \
             "single stable diffusion prompt made of keywords to generate instagram posts. After that, avoid and " \
             "remove the artist names, and camera models in your prompt. Please only include your prompt in the " \
             "answer. \"{}\"".format(words)
    # inputs = "Given the descriptions of one single painting, combine all the information and generate one single stable " \
    #          "diffusion prompt made of keywords to generate art. After that, avoid and remove the artist names " \
    #          " and camera models in your prompt. Please only include your prompt in " \
    #          "the answer. \"{}\"".format(words)
    # print(inputs)
    # exit()
    while indi:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": inputs}
                ]
            )
            output = response["choices"][0]["message"]["content"]
            output = output.replace("\"", "")
            indi = response["choices"][0]["finish_reason"] != "stop" or len(output) == 0
            if indi:
                 raise NotImplementedError
        except Exception as e:
            no_response += 1
            # print(e)
            # print(response["choices"][0]["finish_reason"], output)
            if no_response > 3:
                break
            # print("{}th attempt reveives no response. Retrying....".format(i, no_response))
            continue

    if indi:
        lock.acquire()
        try:
            PASSED += 1
        finally:
            lock.release()
        return

    lock.acquire()
    try:
        with open(save_path, "w") as f:
            f.write(output)
        f.close()
    finally:
        lock.release()
    return


if __name__ == '__main__':
    if phase == "test":
        api_call(10)
    elif phase == "redo":
        start = time.time()
        for i in range(LIMIT):
            print("Processing {}/{}, time used: {:.2f}s.".format(i, LIMIT, time.time()-start))
            api_call(i)
    else:
        for i in range(START_BATCH, BATCHES):
            thread_list = []
            start = time.time()
            for j in range(BATCH_SIZE):
                index = i * BATCH_SIZE + j
                p = threading.Thread(target=api_call, args=(index, ))
                p.start()
                thread_list.append(p)

            for p in thread_list:
                p.join()

            time_used = time.time()-start
            print("Batch: {}/{}, Time used: {}s. Failed: {}.".format(i, BATCHES, time_used, PASSED))
            if time_used < 15 and time_used > 1:
                time.sleep(16 - time_used)
