import datetime
from datetime import datetime
import logging
import os
import openai
from urllib.request import urlopen
from bs4 import BeautifulSoup
import googleSerp as gs
import html2text
import requests
import json
import yaml
import streamlit as st

log = logging.getLogger(__name__)


def setupLogger() -> None:
    dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")
    if not os.path.isdir('./logs'):
        os.mkdir('./logs')
    # TODO need to check if there is a log dir available or not
    logging.basicConfig(filename=('./logs/' + str(dt) + 'applyJobs.log'), filemode='w',
                        format='%(asctime)s::%(name)s::%(levelname)s::%(message)s',
                        datefmt='./logs/%d-%b-%y %H:%M:%S')
    log.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
    c_handler.setFormatter(c_format)
    log.addHandler(c_handler)


class GPTMax:
    setupLogger()

    def __init__(self,
                 openai_api_key,
                 openai_organization,
                 stablediffusion_key,
                 model,
                 filename='output.csv',
                 ) -> None:
        self.stablediffusion_key = stablediffusion_key
        self.model = model
        # self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        openai.organization = openai_organization
        log.info("Starting Gpt Max")
        # dirpath: str = os.getcwd()
        # log.info("current directory is : " + dirpath)

    def optimizedPrompt(self, prompt):
        seedPrompt = "I want you to become my prompt engineer. Your goal is to help me craft the best possible prompt " \
                     "for my needs. This prompt will be used by you, ChatGPT. You will follow the following " \
                     "processes. 1. Your first response will ask me what the prompt should be about. I will provide " \
                     "my answer, but we will need to improve it through continual iterations by going through the " \
                     "next steps. 2. Based on my input, you will generate 2 sections. a) Revised prompt (provide your " \
                     "rewritten prompt. it should be clear, concise, and easily understood by you), b) Questions (ask " \
                     "any relevant questions pertaining to what additional information is needed from me to improve " \
                     "the prompt). 3. We will continue this iterative process with me providing additional " \
                     "information to you and you updating the prompt in the Revised prompt section until I say we are " \
                     "done." \
                     "Here is the seed prompt: {}".format(prompt) \

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[

                {"role": "user", "content": seedPrompt}
            ]
        )
        return completion.choices[0].message.content

    def bitcoinPriceAnalysis(self):
        print("Bitcoin Price Analysis")

        # Get Bitcoin Price From the last 30 days
        url = "https://coinranking1.p.rapidapi.com/coin/Qwsogvtv82FCd/history"
        querystring = {
            "referenceCurrencyUuid": "yhjMzLPhuIDl", "timePeriod": "7d"}
        headers = {
            "X-RapidAPI-Key": "a617d6467dmshac84323ce581a72p11caa9jsn1adf8bbcbd47",
            "X-RapidAPI-Host": "coinranking1.p.rapidapi.com"
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        print("JSON...")
        JSONResult = json.loads(response.text)
        print("Getting History...")
        history = JSONResult["data"]["history"]
        prices = []
        print("Filling Prices...")
        for change in history:
            prices.append(change["price"])

        # ask ChatGPT To analyze the prices
        pricesList = ','.join(prices)
        chatGPTPrompt = "Hey there ChatGPT! Could you provide a brief analysis based on the recent Bitcoin prices over the last seven days? I'll share the price data with you, and I'd love to hear your insights on what this could mean for the cryptocurrency market. Thanks in advance for your help! price list: " + pricesList
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[

                {"role": "user", "content": chatGPTPrompt}
            ]
        )
        return completion.choices[0].message.content

    def searchTheWeb(self, query):
        print("Searching the web...")
        url = gs.GetTop1GoogleResults(query)
        print("URL Found: " + url)
        print("Opening URL...")
        html = urlopen(url).read()
        print("Pasrsing Content...")
        soup = BeautifulSoup(html, features="html.parser")
        extractedText = soup.get_text()
        print("Extract Text...")
        h = html2text.HTML2Text()
        h.ignore_links = True
        blogPost = h.handle(extractedText)
        print("Generating Summary...")
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[

                {"role": "user", "content": """In the following input, I am going to give you a text you
                 should summarize for me. I will give you a maximum and a minimum
                 amount of words you should use for the text. I am also going
                 to give you the text itself after that. The language
                 of the text you get should define in which language
                 you write the summary. For Example, if the text is German
                 the summary should be in German too. This goes for every language.
                 While writing the summary I want you to remember the following information:
                 When it comes to writing content, two factors are crucial,'perplexity' and 'burstiness'
                 ,Perplexity measures the complexity of text. Separately, burstiness compares
                 the variations of sentences. Humans tend to write with great burstiness,
                 for example, with some longer or complex sentences alongside shorter sentences.
                 AI sentences tend to be more uniform. Therefore, when writing the following content
                 I am going to ask you to create, I need it to have a good amount of perplexity
                 and burstiness. Keep that information in mind while writing. Minimum: 100, Maximum: 500, Text: """ + blogPost}

            ]
        )

        summary = completion.choices[0].message.content
        return summary

    def generateImages(self, prompt):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[

                {"role": "user", "content": """You are an expert AI artist with over 30 years of experience
    
                Here is a full matrix of styles, time periods, photography techniques, miscellaneous styles, artists, architects, color palettes, lighting, environment, and perspectives for you to utilize:
                
                Style	Time Periods	Photography Techniques	Misc Styles	Artists	Architects	Color Palette	Lighting	Environment	Perspectives
                Nouveau	Ancient Egypt	Macro Photography	Synthwave	Hayao Miyazaki	Frank Lloyd Wright	Bright Colors	Soft Light	Natural	Bird's Eye View
                Film Noir	Ancient Greece	Tilt Shift	Polymer Clay	Peter Elson	Frank Gehry	Dark Colors	Hard Light	Urban	Worm's Eye View
                Manga	Modern	Bokeh Effect	Cyberpunk	Katsuhiro Otomo	Zaha Hadid	Bold Colors	Mood Light	Futuristic	Isometric View
                Post-Apocalyptic	Futuristic	Long Exposure	Pixel Art	Moebius	Mies van der Rohe	Desaturated	Spot Light	Dystopian	Low Angle View
                Surrealism	Renaissance	High Dynamic Range	3D Printing	Salvador Dali	Le Corbusier	Dreamlike	Backlight	Cosmic	High Angle View
                Abstract	Baroque	Panoramic	Pixel Sorting	Pablo Picasso	Antoni Gaudi	Geometric	Rim Light	Digital	Overhead View
                Impressionism	Gothic	Timelapse	Collage	Claude Monet	Eero Saarinen	Pastel	Fill Light	Enchanted	Dutch Angle
                Expressionism	Romanticism	Night Photography	Vexel Art	Edvard Munch	Philip Johnson	Intense	Key Light	Abstract	Worm's Eye View
                Pop Art	Art Deco	Infrared	ASCII Art	Roy Lichtenstein	I. M. Pei	Bold Graphics	High-Key	Iconic	Eye Level View
                Futurism	Art Nouveau	Long Exposure Light Painting	Low Poly	Umberto Boccioni	Santiago Calatrava	Futuristic	Low-Key	Technologic	Tilted View
                Realism	Dadaism	Lens Flare	8-Bit Art	Johannes Vermeer	Norman Foster	Realistic	Shadow	Naturalistic	Oblique View
                Minimalism	Abstract Expressionism	Silhouette	Vaporwave	Kazimir Malevich	Tadao Ando	Minimal	Flat Light	Simple	Front View
                Gothic	Color Field	Action Photography	Aesthetic	Michelangelo	Frank Furness	Dark	Dramatic Light	Mysterious	Rear View
                Romanticism	Hyperrealism	Zoom Blur	80's Retro	Caspar David Friedrich	Richard Rogers	Soft	Back Light	Nostalgic	Side View
                Renaissance	Pop Surrealism	Slow Shutter	90's Grunge	Leonardo da Vinci	Foster + Partners	Rich	Spot Light	Cultural	Three-Quarter View
                Baroque	Neo-Expressionism	Panning	Anime	Caravaggio	Thomas Heatherwick	Decorative	Key Light	Ornate	Full-Face View
                Art Deco	Suprematism	Macro Action	Space Art	Tamara de Lempicka	Jean Nouvel	Elegant	High-Key	Glamorous	Half-Profile View
                Art Nouveau	Futurism (Literary)	Time Warp	Dark Fantasy	Alph					
                
                The goal is to create amazing and extremely detailed pictures that utilize the matrix above. When creating pictures, start a prompt with "/imagine prompt: "
                
                /imagine prompt: A majestic lion , sits atop a rock formation, basking in the warm glow of a golden sunset . The surrounding grasslands stretch out as far as the eye can see, creating a vast and serene landscape . The lion's fur is painted in bold and striking colors, reminiscent of a Pop Art style . The composition of the image is a perfect balance between foreground and background, with the lion being the clear focal point, 4K,hyper detailed illustration,
                
                
                
                Please keep this information in mind and generate a prompt about  """ + prompt}

            ]
        )

        promptGenerated = completion.choices[0].message.content

        # connect to stable diffusion API
        url = 'https://stablediffusionapi.com/api/v3/text2img'

        data = {
            "key": self.stablediffusion_key,
            "prompt": promptGenerated,
            "negative_prompt": "",
            "width": "512",
            "height": "512",
            "samples": "1",
            "num_inference_steps": "20",
            "seed": None,
            "guidance_scale": 7.5,
            "safety_checker": "yes",
            "webhook": None,
            "track_id": None
        }

        response = requests.post(url, json=data)
        JSONResult = json.loads(response.text)
        print("Generating Image...")
        imgURL = JSONResult["output"][0]
        return imgURL


if __name__ == '__main__':
    with open("config.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    assert parameters['openai_api_key'] is not None
    assert parameters['openai_organization'] is not None
    assert parameters['stablediffusion_key'] is not None
    assert parameters['model'] is not None
    try:
        gptmax = GPTMax(parameters['openai_api_key'],
                        parameters['openai_organization'],
                        parameters['stablediffusion_key'],
                        parameters['model'],
                        )
        st.title('ChatGPT Max Edition 2.1, using model {} 🚀'.format(gptmax.model))
        st.subheader(
            'Now, You Can Generate Images, Analyze Current Crypto Prices, and Search The Web With ChatGPT')

        prompt = st.text_input("Prompt:", value="", max_chars=100, key=None,
                               type="default", help=None, autocomplete=None, on_change=None,
                               args=None, kwargs=None, placeholder="search the web for ...", disabled=False,
                               label_visibility="visible")

        if st.button('Generate'):
            if 'bitcoin' in prompt:
                with st.spinner('Analyzing Current Bitcoin Price...'):
                    result = gptmax.bitcoinPriceAnalysis()
                    st.text_area("Analysis", result.strip(),
                                 height=500, max_chars=None, key=None, )
                st.success('Done!')
            elif 'search' in prompt:
                with st.spinner('Searching the web for the latest information...'):
                    prompt = prompt.replace("search the web for ", "")
                    result = gptmax.searchTheWeb(prompt)
                    st.text_area("Results", result.strip(),
                                 height=500, max_chars=None, key=None, )
                st.success('Done!')
            elif 'image' in prompt:
                with st.spinner('Generating Your Image...'):
                    result = gptmax.generateImages(prompt)
                    st.image(result)
                st.success('Done!')
            else:
                with st.spinner('Optimizing your prompt'):
                    result = gptmax.optimizedPrompt(prompt)
                    st.text_area("Results", result.strip(),
                                 height=500, max_chars=None, key=None, )
                    st.success('Done!')

    except Exception as e:
        log.error(e)
        print(e)



    # choice = input("Input what you'd like to do:\
    # 1. Search the web\
    # 2. Generate images\
    # 3. Bitcoin price analysis\
    # :)")
    #
    # if choice == '1':
    #     prompt = input("What would you like to search for? :)")
    #     gpt.searchTheWeb(prompt)
    # elif choice == '2':
    #     prompt = input("What image would you like to generate? :)")
    #     gpt.generateImages(prompt)
    # elif choice == '3':
    #     gpt.bitcoinPriceAnalysis()
