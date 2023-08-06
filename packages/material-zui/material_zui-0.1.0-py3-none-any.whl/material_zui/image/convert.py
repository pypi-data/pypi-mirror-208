from PIL import Image
import os
import cv2
from cv2 import Mat
from material_zui.image.data import K_SIZE, MAX_MP
from material_zui.log.index import printTable

# def convert_to_sketch(image: Mat) -> Mat:
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     inverted_gray_image = 255 - gray_image  # type: ignore
#     blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
#     inverted_blurred_image = 255 - blurred_image
#     pencil_sketch = cv2.divide(
#         gray_image, inverted_blurred_image, scale=256.0)
#     return pencil_sketch


# def to_sketch(img: Mat, k_size: int = K_SIZE) -> Mat:
#     grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     invert_img = cv2.bitwise_not(grey_img)
#     blur_img = cv2.GaussianBlur(invert_img, (k_size, k_size), 0)
#     invblur_img = cv2.bitwise_not(blur_img)
#     return cv2.divide(grey_img, invblur_img, scale=256.0)

def to_sketch(k_size: int = K_SIZE):
    def handle_image(image: Mat):
        grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        invert_img = cv2.bitwise_not(grey_img)
        blur_img = cv2.GaussianBlur(invert_img, (k_size, k_size), 0)
        invblur_img = cv2.bitwise_not(blur_img)
        return cv2.divide(grey_img, invblur_img, scale=256.0)
    return handle_image


# def save_sketch_then_upscale(directory_path:  str, new_directory_path: str = '', k_size: int = 21, max_mp: int = MAX_MP) -> None:
#     images = upscales_dir_to_max_size(
#         directory_path, new_directory_path, max_mp)
#     for image in images:
#         sketch_image = to_sketch(k_size)(image['matImage'])
#         cv2.imwrite(os.path.join(new_directory_path,
#                     image['name']), sketch_image)
#     printTable({
#         'Name': [info['name'] for info in images],
#         'Width': [info['width'] for info in images],
#         'Height': [info['height'] for info in images],
#         'Ratio': [info['ratio'] for info in images],
#     })


# def to_jpg(image: Mat) -> None:
#     '''
#     @image_path: `abc/def/input.png`
#     @output_path: `abc/def/output.jpg` or `abc/def/output.jpeg`
#     '''
#     # image = Image.open(image_path)
#     # image.save(output_path, format="JPEG")
#     # image.close()
#     # cv2.imread(image_path)
#     # image.to


def save_to_jpg(image_path: str, output_path: str) -> None:
    '''
    @image_path: `abc/def/input.png`
    @output_path: `abc/def/output.jpg` or `abc/def/output.jpeg`
    '''
    image = Image.open(image_path)
    image.save(output_path, format="JPEG")
    image.close()


def to_grayscale(image: Mat): return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def save_to_grayscale(image_path: str, output_path: str):
    image = cv2.imread(image_path)
    grayscale_image = to_grayscale(image)
    cv2.imwrite(output_path, grayscale_image)
