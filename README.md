# The Adversarial AI-Art: Understanding, Generation, Detection, and Benchmarking

## Introduction
Generative AI models can produce high-quality images from text prompts. These images often look like those created by human artists or photographers. While this technology is impressive, it also raises security concerns. AI-generated images can be used for fraud, misinformation, and unauthorized art creation. In this project, we systematically explore and detect AI-generated images in adversarial scenarios. We have created the ARIA dataset, which contains over 140,000 images in categories such as artworks, social media images, news photos, disaster scenes, and anime pictures.
You can access our dataset here: [ARIA Dataset](https://kansas-my.sharepoint.com/:f:/g/personal/y844l178_home_ku_edu/EsbfHWbpRGZIrka8U53CyVEBqxJZA1IwKXRx1pSejuMffA?e=o2f0eD)
For more details, see our paper: [The Adversarial AI-Art: Understanding, Generation, Detection, and Benchmarking](https://arxiv.org/abs/2404.14581)

## The ARIA Dataset
- **Total Images:** 144,175
- **Categories:**
  - **Social Media Fraud:** 
    - **Ins:** 26,265 Instagram-style images
  - **Fake News and Misinformation:** 
    - **News:** 26,559 news images
    - **Disaster:** 25,288 disaster scene images
  - **Unauthorized Art Style Imitation:** 
    - **Art:** 43,075 artworks
    - **Pixiv:** 22,988 anime pictures
- **Sources:**
  - **Art:** Best Artworks of All Time [Kaggle Dataset](https://www.kaggle.com/datasets/ikarus777/best-artworks-of-all-time)
  - **Disaster:** Disaster Dataset [Kaggle Dataset](https://www.kaggle.com/datasets/telperion/diasterdatasetraw)
  - **News:** N24News [GitHub Repository](https://github.com/billywzh717/N24News)
  - **Pixiv:** Pixiv Top Daily Illustration 2018 [Kaggle Dataset](https://www.kaggle.com/datasets/stevenevan99/pixiv-top-daily-illustration-2018)
  - **Instagram:** Instagram Images [Kaggle Dataset](https://www.kaggle.com/datasets/shmalex/instagram-images)

## Tasks
- [x] Collect image-to-text prompts
- [x] Collect text-to-image data
- [x] Collect image-to-image data
- [x] User study
- [x] Benchmarking detection
- [x] ResNet-50 Classifier

## How to Run

- **Data Collection**
    - For each script, there are three phases: "test", "text", and "image". "test" generates one random image based on both text and image as a test. "text" is for exhaustive text-to-image generation. "image" is likewise for exhaustive image-to-image generation.
    - Example to run the "test": 
      ```bash
      python collect_dreamstudio.py test
      ```
    - New prompts can be collected with "scrape_prompt", "refine_prompt", and "rewrite_prompt". "refine" is for data cleaning. "rewrite" is feeding them to GPT-4.
    - Collected image data will be saved in `./scrape_text2image` and `./scrape_image2image`.

- **ResNet-50 Classifier**
    To run the code, use the following command:
    ```bash
    python your_script.py --mode [train|test|both] --num_epochs 300 --batch_size 64 --learning_rate 0.005 --early_stopping_patience 5
    ```
### Parameters
Here is the API information for each generator we have used. For detailed parameter information, please refer to our paper Section 3.3 AI-Art Generation:
- DreamStudio / stability.ai: [gRPC API parameters](https://platform.stability.ai/docs/features/api-parameters)
- OpenAI: [API reference](https://platform.openai.com/docs/api-reference/images), [Docs](https://platform.openai.com/docs/guides/images)
- Midjourney: [Parameters](https://docs.midjourney.com/docs/parameter-list)
- StarryAI: [Guide](https://starryai.readme.io/reference/getting-started-with-your-api)

## Tips
1. To ensure the collection goes smoothly, the sleep time in the scripts may need to be changed according to your machine and network environment.
2. Make sure the file directory in your code is correct.
