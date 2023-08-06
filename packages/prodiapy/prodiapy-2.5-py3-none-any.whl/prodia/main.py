import requests
import time
import os
import asyncio


api_key = None

def Client(api_key:str=None):
    if api_key is None:
        print("No API key provided")
        return
    else:
        global key
        key = api_key

def models():
    print('Available models:')
    print(Models.mlist)

def samplers():
    print('Available samplers:')
    print(Samplers.slist)

def aspect_ratios():
    print('Available ratios:')
    print(ar.alist)


def txt2img(
        prompt:str=None,
        negative_prompt:str="badly draw",
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        sampler:str="Heun",
        aspect_ratio:str="square",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        upscale:bool=False):
    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API kay at https://app.prodia.com/api\nto define api key use:\nprodia.api_key = 'your-key'")
    else:
        if prompt == None:
            print("LOG: Prompt was not defined, used default (kittens on cloud)")
            prompt = "kittens on cloud"
        url = "https://api.prodia.com/v1/job"
        payload = {
            "prompt": prompt,
            "model": model,
            "sampler": sampler,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "upscale": upscale,
            "aspect_ratio": aspect_ratio
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headers2 = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: txt2img image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        time.sleep(3)

        retrieve_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(retrieve_url, headers=headersr2)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                time.sleep(2)
            elif status == "generating":
                print("Still working...")
                time.sleep(2)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status


def img2img(
        imageUrl:str=None,
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        prompt:str=None,
        denoising_strength:float=0.7,
        negative_prompt:str="badly drawn",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        upscale:bool=False,
        sampler:str="Heun"):

    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API key at https://app.prodia.com/api\nto define api key use:\nprodia.Client(api_key='your-key')")
    elif imageUrl is None:
        print("ERROR: Image URL is required and cannot be empty")
    elif prompt is None:
        print("ERROR: Prompt is required and cannot be empty")
    else:
        url = "https://api.prodia.com/v1/transform"

        payload = {
            "steps": steps,
            "sampler": sampler,
            "imageUrl": imageUrl,
            "model": model,
            "prompt": prompt,
            "denoising_strength": denoising_strength,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "upscale": upscale
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headersrecieve = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: img2img image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        time.sleep(5)

        rec_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(rec_url, headers=headersrecieve)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"LOG: Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                time.sleep(3)
            elif status == "generating":
                print("Still working...")
                time.sleep(3)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status

def control_net_scribble(
        imageUrl:str=None,
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        prompt:str=None,
        negative_prompt:str="badly drawn",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        sampler:str="Heun"):

    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API key at https://app.prodia.com/api\nto define api key use:\nprodia.Client(api_key='your-key')")
    elif imageUrl is None:
        print("ERROR: Image URL is required and cannot be empty")
    elif prompt is None:
        print("ERROR: Prompt is required and cannot be empty")
    else:
        url = "https://api.prodia.com/v1/controlnet/scribble"

        payload = {
            "steps": steps,
            "sampler": sampler,
            "imageUrl": imageUrl,
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "seed": seed
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headersrecieve = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: control_net image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        time.sleep(5)

        rec_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(rec_url, headers=headersrecieve)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"LOG: Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                time.sleep(3)
            elif status == "generating":
                print("Still working...")
                time.sleep(3)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status

async def arunv1(
        prompt:str="kittens on cloud",
        negative_prompt:str="badly drawn",
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        sampler:str="Heun",
        aspect_ratio:str="square",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        upscale:bool=False):
    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API kay at https://app.prodia.com/api\nto define api key use:\nprodia.Client(api_key='your-key')")
    else:
        if prompt == "kittens on cloud" or prompt == "" or prompt == " ":
            print("LOG: Prompt was not defined or empty, used default (kittens on cloud)")
        url = "https://api.prodia.com/v1/job"
        payload = {
            "prompt": prompt,
            "model": model,
            "sampler": sampler,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "upscale": upscale,
            "aspect_ratio": aspect_ratio
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headersrecieve = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: txt2img image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        await asyncio.sleep(3)

        rec_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(rec_url, headers=headersrecieve)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                await asyncio.sleep(2)
            elif status == "generating":
                print("Still working...")
                await asyncio.sleep(2)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status


async def arunv2(
        imageUrl:str=None,
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        prompt:str=None,
        denoising_strength:float=0.7,
        negative_prompt:str="badly drawn, low detailed, ugly, mutated, unralistic",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        upscale:bool=False,
        sampler:str="Heun"):

    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API kay at https://app.prodia.com/api\nto define api key use:\nprodia.api_key = 'your-key'")
    elif imageUrl is None:
        print("ERROR: Image URL is required and cannot be empty")
    elif prompt is None:
        print("ERROR: Prompt is required and cannot be empty")
    else:
        url = "https://api.prodia.com/v1/transform"

        payload = {
            "steps": steps,
            "sampler": sampler,
            "imageUrl": imageUrl,
            "model": model,
            "prompt": prompt,
            "denoising_strength": denoising_strength,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "upscale": upscale
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headersrecieve = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: img2img image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        await asyncio.sleep(4)

        rec_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(rec_url, headers=headersrecieve)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"LOG: Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                await asyncio.sleep(2)
            elif status == "generating":
                print("Still working...")
                await asyncio.sleep(2)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status

async def arunv3(
        imageUrl:str=None,
        model:str="Realistic_Vision_V2.0.safetensors [79587710]",
        prompt:str=None,
        negative_prompt:str="badly drawn, low detailed, ugly, mutated, unralistic",
        steps:int=25,
        cfg_scale:int=7,
        seed:int=-1,
        sampler:str="Heun"):

    if key is None:
        print("ERROR: API key is corrupted or not defined, get your API kay at https://app.prodia.com/api\nto define api key use:\nprodia.api_key = 'your-key'")
    elif imageUrl is None:
        print("ERROR: Image URL is required and cannot be empty")
    elif prompt is None:
        print("ERROR: Prompt is required and cannot be empty")
    else:
        url = "https://api.prodia.com/v1/controlnet/scribble"

        payload = {
            "steps": steps,
            "sampler": sampler,
            "imageUrl": imageUrl,
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "seed": seed
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": key
        }
        headersrecieve = {
            "accept": "application/json",
            "X-Prodia-Key": key
        }
        print(f"LOG: img2img image with params:\n{payload}")
        response = requests.post(url, json=payload, headers=headers)
        job_id = response.json()['job']
        await asyncio.sleep(4)

        rec_url = f'https://api.prodia.com/v1/job/{job_id}'
        stt = True
        while stt is True:
            rec = requests.get(rec_url, headers=headersrecieve)
            status = rec.json()['status']
            if status == "succeeded":
                print(f"LOG: Image {job_id} generated!")
                image_url = rec.json()['imageUrl']
                stt = False
                return image_url
            elif status == "queued":
                print("Still working...")
                await asyncio.sleep(2)
            elif status == "generating":
                print("Still working...")
                await asyncio.sleep(2)
            else:
                print(f"ERROR: Something went wrong! Please try later, error: {status}")
                stt = False
                return status




