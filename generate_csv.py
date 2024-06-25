import os
import pandas as pd

#####
#  mode: 'create' for creating a new CSV file, 'append' for appending to an existing file. 
# global variables fyi

# CHANGE HERE!!!
generators = ['DreamStudio', 'Midjourney', 'StarryAI', 'openai']
methods = ['I2I', 'T2I']
categories = ['art', 'disaster', 'news', 'instagram', 'pixiv']
generated_image_path_baselines = './dataset/'
original_image_path_baselines = './select_data/'
csv_path_baselines = "./csvs/"
flagmode = ['create', 'append']
# CHANGE HERE!!!
# real images in org_baseline/category
# fake images in gen_baseline/generator/method/category
# csv files will be saved in csv_path_baselines
'''dataarray = []
dataarray.append({'generator': generator, 'category': 'art', 'method': method[1], 'generated_image_path': './dreamstudio/art_2500', 
                  'original_image_path': './select_data/art/art_2500', 'csv_file_path': './dreamstudio_text2image.csv', 'mode': 'create'})
dataarray.append({'generator': generator, 'category': 'disaster', 'method': method[1], 'generated_image_path': './scrape_text2image/dreamstudio/disaster_3k', 
                  'original_image_path': './select_data/disaster/disaster_3k', 'csv_file_path': './dreamstudio_text2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'news', 'method': method[1], 'generated_image_path': './scrape_text2image/dreamstudio/news_3k', 
                  'original_image_path': './select_data/news/news_3k', 'csv_file_path': './dreamstudio_text2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'insta', 'method': method[1], 'generated_image_path': './scrape_text2image/dreamstudio/insta_3k', 
                  'original_image_path': './select_data/instagram/insta_3k', 'csv_file_path': './dreamstudio_text2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'pixiv', 'method': method[1], 'generated_image_path': './scrape_text2image/dreamstudio/pixiv_3k', 
                  'original_image_path': './select_data/pixiv/pixiv_3k', 'csv_file_path': './dreamstudio_text2image.csv', 'mode': 'append'})

dataarray.append({'generator': generator, 'category': 'art', 'method': method[0], 'generated_image_path': './scrape_image2image/dreamstudio/art_2500', 
                  'original_image_path': './select_data/art/art_2500', 'csv_file_path': './dreamstudio_image2image.csv', 'mode': 'create'})
dataarray.append({'generator': generator, 'category': 'disaster', 'method': method[0], 'generated_image_path': './scrape_image2image/dreamstudio/disaster_3k', 
                  'original_image_path': './select_data/disaster/disaster_3k', 'csv_file_path': './dreamstudio_image2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'news_3k', 'method': method[0], 'generated_image_path': './scrape_image2image/dreamstudio/news_3k', 
                  'original_image_path': './select_data/news/news_3k', 'csv_file_path': './dreamstudio_image2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'insta_3k', 'method': method[0], 'generated_image_path': './scrape_image2image/dreamstudio/insta_3k', 
                  'original_image_path': './select_data/instagram/insta_3k', 'csv_file_path': './dreamstudio_image2image.csv', 'mode': 'append'})
dataarray.append({'generator': generator, 'category': 'pixiv_3k', 'method': method[0], 'generated_image_path': './scrape_image2image/dreamstudio/pixiv_3k', 
                  'original_image_path': './select_data/pixiv/pixiv_3k', 'csv_file_path': './dreamstudio_image2image.csv', 'mode': 'append'})
'''# Replace 'your_generator', 'your_category', and 'your_method' with actual values

category = 'pixiv_3k'

# Paths (replace with actual paths)
generated_image_path = './scrape_image2image/dreamstudio/pixiv_3k'
original_image_path = './select_data/pixiv/pixiv_3k'
csv_file_path = './dreamstudio_image2image.csv' 

def common_names(set1, set2):
    # Extract the base name without extension for each file in the sets
    base_names1 = {os.path.splitext(filename)[0] for filename in set1}
    base_names2 = {os.path.splitext(filename)[0] for filename in set2}
    # Find intersection of both sets to get common names
    common = base_names1.intersection(base_names2)
    return common



def generate_csv(mode, generator, category, method, generated_image_path, original_image_path, csv_file_path):
    files_in_A = os.listdir(generated_image_path)
    files_in_B = os.listdir(original_image_path)

    images_in_A = set([file for file in files_in_A if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
    images_in_B = set([file for file in files_in_B if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
    changed_names_in_A = set()

    for base_name in images_in_A:#deal with artist name problem 
        modified_base_name = base_name.replace("и╣", "ü")
        changed_names_in_A.add(modified_base_name)
    base_names1 = {os.path.splitext(filename)[0] for filename in changed_names_in_A}

    common_images = common_names(changed_names_in_A, images_in_B)

    #print ("We  cannot find corresponding original image for these images in the dataset " + generator + " " + method + " " + category)
    #print (base_names1 - common_images)
    data = []

    for image_name in common_images:
        text_file_name = os.path.splitext(image_name)[0] + '.txt'
        text_file_path = os.path.join(original_image_path, text_file_name)

        if os.path.isfile(text_file_path):
            with open(text_file_path, 'r') as file:
                text_content = file.read()

            data.append({
                'Image_Name': os.path.splitext(image_name)[0] + os.path.splitext(image_name)[1],
                'Text_Prompt': text_content,
                'Generator': generator,
                'Category': category,
                'Method': method
            })

    new_data_df = pd.DataFrame(data)
   
    if mode == 'create':
        new_data_df.to_csv(csv_file_path, index=False)
    elif mode == 'append':
        # Check if the CSV file exists
        if os.path.exists(csv_file_path):
            new_data_df.to_csv(csv_file_path, mode='a', header=False, index=False)
        else:
            # If it doesn't exist, write the new data with the header
            new_data_df.to_csv(csv_file_path, index=False)
    else:
        raise ValueError("Mode must be 'create' or 'append'.")

for generator in generators:
    #if(generator == 'openai'): continue #just in case
    flag = 0
    for method in methods:
        for category in categories:
            #if (generator == 'StarryAI' and method == 'I2I' and category == 'art'): continue # just in case
            generate_path = generated_image_path_baselines + generator + "/" + method + "/" + category
            original_path = original_image_path_baselines + category
            csv_path = csv_path_baselines + generator + ".csv"
            generate_csv(mode=flagmode[flag], generator=generator, category=category, method=method, generated_image_path=generate_path, original_image_path=original_path, csv_file_path=csv_path)
            flag = 1
