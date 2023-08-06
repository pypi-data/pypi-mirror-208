import os
import uuid
from pathlib import Path
import cv2
import requests
from cv2 import Mat
from material_zui.image.data import IMG_EXT
from material_zui.log import printTable

# def save_upscale_toJpg(directory_path:  str, new_directory_path: str = '', max_mp: int = MAX_MP) -> None:
#     new_directory_path = new_directory_path if new_directory_path else directory_path
#     images = get_images(directory_path)
#     for index, image in enumerate(images):
#         ratio = get_image_ratio_to_max_mp(image, max_mp)
#         jpg_dir = f'{new_directory_path}/{index}.jpg'
#         upscale_image = cv2.resize(
#             image, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_CUBIC)  # type: ignore
#         cv2.imwrite(jpg_dir, upscale_image)
#         print(index+1, jpg_dir, ratio)


def handle_image(directory_path: str, new_directory_path: str = '', extension: str = ''):
    image_info = get_image_info(directory_path)
    dir_name = image_info['dir_name']
    ext = extension or image_info['extension']
    new_image_path = f'{dir_name}/{str(uuid.uuid4())}.{ext}'
    new_directory_path = new_directory_path if new_directory_path else new_image_path

    def handle_each_image(*functions):
        result: Mat = image_info['image']
        for function in functions:
            result = function(result)
        cv2.imwrite(new_directory_path, result)
    return handle_each_image


def handle_images(directory_path: str, new_directory_path: str = '', extension: str = ''):
    image_paths = get_image_paths(directory_path)

    def handle_each_image(*functions):
        items = []
        for image_path in image_paths:
            image_info = get_image_info(image_path)
            name = image_info['name']
            ext = extension or image_info['extension']
            output_image_path = ''
            if new_directory_path and directory_path != new_directory_path:
                output_image_path = f'{new_directory_path}/{name}.{ext}'
            handle_image(image_path, output_image_path, extension)(*functions)
            items.append((image_path, output_image_path))
        printTable({
            'Input path': [item[0] for item in items],
            'Output path': [item[1] for item in items],
        })
    return handle_each_image

# def get_image_sizes(directory_path: str) -> list[dict[{'name': str, 'width': int, 'height': int}]]:
#     images = get_image(directory_path)
#     images_name = get_image_name(directory_path)
#     return [{'name': images_name[index], 'width':image.width, 'height':image.height}
#             for index, image in enumerate(images)]


# def get_image(directory_path: str) -> list[Image.Image]:
#     images_name = get_image_name(directory_path)
#     # print(images_name)
#     return list(map(lambda file_name: Image.open(os.path.join(
#         directory_path, file_name)), images_name))
# def get_image(directory_path: str) -> list[ZuiImage]:
#     images_name = get_image_name(directory_path)
#     images = [Image.open(os.path.join(directory_path, file_name))
#               for file_name in images_name]
#     return [{'image': image, 'name': images_name[index], 'ext': image.format or '', 'width':image.width, 'height':image.height} for index, image in enumerate(images)]


def get_image_names(directory_path: str) -> list[str]: return list(filter(lambda file_name: file_name.endswith(
    IMG_EXT), os.listdir(directory_path)))


def get_image_paths(directory_path: str) -> list[str]:
    images_name = get_image_names(directory_path)
    return [os.path.join(directory_path, image_name) for image_name in images_name]


def get_images(directory_path: str) -> list[Mat]: return [cv2.imread(
    image_path) for image_path in get_image_paths(directory_path)]


# def get_image_info(image_path: str) -> dict[{'image': Mat, 'name': str, 'dir_name': str, 'width': int, 'height': int, 'extension': str}]:
#     '''
#     @file_name: `abc.jpg`
#     @name: `abc`
#     @extension: `jpg`
#     '''
#     image = cv2.imread(image_path)
#     height, width = image.shape[:2]
#     file_name = os.path.basename(image_path)
#     name = os.path.basename(image_path)
#     extension = os.path.splitext(image_path)[1][1:]
#     dir_name = os.path.dirname(image_path)
#     # print(width, height, extension)
#     return {'image': image, 'name': name, 'dir_name': dir_name, 'width': width, 'height': height, 'extension': extension}

def get_image_info(image_path: str) -> dict[{'image': Mat, 'file_name': str, 'name': str, 'dir_name': str, 'width': int, 'height': int, 'extension': str}]:
    '''
    @file_name: `abc.jpg`
    @name: `abc`
    @extension: `jpg`
    '''
    path = Path(image_path)
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    file_name = path.name
    name = path.stem
    extension = os.path.splitext(image_path)[1][1:]
    dir_name = os.path.dirname(image_path)
    return {'image': image, 'file_name': file_name, 'name': name, 'dir_name': dir_name, 'width': width, 'height': height, 'extension': extension}


def get_image_size(image: Mat) -> tuple[int, int]:
    height, width = image.shape[:2]
    return (width, height)

# def change_image_path(file_path: str, file_name: str) -> str:
#     path_prefix = os.path.splitext(file_path)[0]
#     return f'{path_prefix}{file_name}'


def download(url: str, path: str) -> None:
    '''Download image by url to path'''
    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)
