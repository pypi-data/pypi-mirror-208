import replicate
import os


def set_token(token: str) -> None:
    '''
      Create account then get token from: https://replicate.com/account
    '''
    os.environ["REPLICATE_API_TOKEN"] = token


def run_stable_diffusion(prompt: str) -> list[str]:
    '''https://replicate.com/stability-ai/stable-diffusion'''
    return replicate.run(
        "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        input={"prompt": prompt},
    )  # type: ignore


def text_to_image(prompt: str) -> list[str]:
    '''https://replicate.com/pixray/text2image'''
    urls = replicate.run(
        "pixray/text2image:5c347a4bfa1d4523a58ae614c2194e15f2ae682b57e3797a5bb468920aa70ebf",
        input={"prompts": prompt},
    )
    return [url for url in urls]


def upscale(image_path: str, upscale: int = 2) -> str:
    '''https://replicate.com/sczhou/codeformer'''
    return replicate.run(
        "sczhou/codeformer:7de2ea26c616d5bf2245ad0d5e24f0ff9a6204578a5c876db53142edd9d2cd56",
        input={"image": open(image_path, "rb"), "upscale": upscale}
    )  # type: ignore


def recover_old_photo(image_path: str, with_scratch: bool = False, HR: bool = False) -> str:
    '''https://replicate.com/microsoft/bringing-old-photos-back-to-life'''
    return replicate.run(
        "microsoft/bringing-old-photos-back-to-life:c75db81db6cbd809d93cc3b7e7a088a351a3349c9fa02b6d393e35e0d51ba799",
        input={"image": open(image_path, "rb"),
               "with_scratch": with_scratch, "HR": HR}
    )  # type: ignore


def fill_color(image_path: str, classes: str = "88") -> list[dict[{'image': str}]]:
    '''https://replicate.com/cjwbw/bigcolor'''
    return replicate.run(
        "cjwbw/bigcolor:9451bfbf652b21a9bccc741e5c7046540faa5586cfa3aa45abc7dbb46151a4f7",
        input={"image": open(image_path, "rb"), "classes": classes}
    )  # type: ignore


def face_restore(image_path: str, task: str = "Face Restoration", broken_image: bool = False) -> list[str]:
    '''
    https://replicate.com/yangxy/gpen
    @task
    Allowed values: `Face Restoration`, `Face Colorization`, `Face Inpainting`
    Default value: `Face Restoration`
    '''
    return replicate.run(
        "yangxy/gpen:cf4e15a70049c0119884eb2906c8ae8807af8317bea98313fefd941e414d0c91",
        input={"image": open(image_path, "rb"), "task": task,
               "broken_image": broken_image}
    )  # type: ignore


def tmp(dir_input: str, dir_output: str):
    return 1
