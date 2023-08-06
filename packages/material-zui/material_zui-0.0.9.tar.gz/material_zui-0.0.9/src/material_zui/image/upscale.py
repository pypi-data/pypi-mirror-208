import cv2
from cv2 import Mat
from material_zui.image.common import get_image_size
from material_zui.image.data import MAX_MP

# def upscale(path:  str | bytes, newPath: str, wRatio: int = 1, hRatio: int = 1, newWidth: int = 0, newHeight: int = 0, isShowImage: bool = False):
#     """
#     Use AI to upscale image
#     """
#     image = Image.open(path)
#     toWidth, toHeight = [0, 0]
#     if newWidth != 0 and newHeight != 0:
#         toWidth = newWidth
#         toHeight = newHeight
#     else:
#         width, height = image.size
#         toWidth = width*wRatio
#         toHeight = height*hRatio
#     newImage = image.resize((toWidth, toHeight))
#     newImage.save(newPath)
#     print(image.format)
#     if isShowImage:
#         newImage.show()
#     return


# def upscale_to_size(image: ZuiImage, new_width: int = 0,
#                     new_height: int = 0): return image.resize((new_width, new_height))


# def upscale_to_ratio(image: ZuiImage, w_ratio: int = 1, h_ratio: int = 1):
#     width, height = image.size
#     to_width, to_height = [width*w_ratio, height*h_ratio]
#     return image.resize((to_width, to_height))


# def upscales_to_max_size(image: ZuiImage, max_mp: int = MAX_MP) -> ZuiImage:
#     '''
#     @max_mp: max size in megapixels
#     '''
#     width, height = image.size
#     to_width, to_height = image.size
#     while (to_width*to_height < max_mp):
#         to_width += width
#         to_height += height
#     return image.resize((to_width, to_height))


# def upscale_to_max_size(images: list[dict[{'image': ZuiImage, 'max_mp': int}]]): return list(map(lambda image: upscales_to_max_size(
#     image['image'], image['max_mp']), images))


# def save_to(images: list[ZuiImage], path: str):
#     for index, image in enumerate(images):
#         # new_path = os.path.join(path, str(index)+'.jpg')
#         # new_path = os.path.join(path, "{}.{}".format(index, image.format))
#         new_path = os.path.join(path, "{}.{}".format(index, 'jpg'))
#         print(new_path, image.getim())
#         image.save(new_path)

def get_ratio_to_max_mp(width: int, height: int, max_mp: int = MAX_MP) -> int:  # type: ignore
    '''
    @max_mp: max size in megapixels
    '''
    to_width, to_height = width, height
    ratio = 1
    while (to_width*to_height < max_mp):
        ratio += 1
        to_width = width * ratio
        to_height = height * ratio
    return ratio


# @dispatch(Mat, int)
# def get_ratio_to_max_mp(image: Mat, max_mp: int = MAX_MP) -> int:
#     '''
#     @max_mp: max size in megapixels
#     '''
#     print('image', image)
#     height, width = image.shape[:2]
#     return get_ratio_to_max_mp(width, height, max_mp)  # type: ignore

# def get_image_ratio_to_max_mp(image: Mat, max_mp: int = MAX_MP) -> int:
#     '''
#     @max_mp: max size in megapixels
#     '''
#     height, width = image.shape[:2]
#     return get_ratio_to_max_mp(width, height, max_mp)  # type: ignore


def upscale_to_max_size(max_mp: int = MAX_MP):
    def handle_image(image: Mat):
        height, width = image.shape[:2]
        width, height = get_image_size(image)
        ratio = get_ratio_to_max_mp(width, height, max_mp)
        upscale_image = cv2.resize(
            image, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_CUBIC)  # type: ignore
        return upscale_image
    return handle_image


# def upscales_dir_to_max_size(directory_path:  str, new_directory_path: str = '', max_mp: int = MAX_MP) -> list[ZuiImage]:
#     '''
#     @max_mp: max size in megapixels
#     '''
#     new_directory_path = new_directory_path if new_directory_path else directory_path
#     images_name = get_image_names(directory_path)
#     images: list[ZuiImageRes] = []
#     for image_name in images_name:
#         image = cv2.imread(os.path.join(directory_path, image_name))
#         height, width = image.shape[:2]
#         ratio = get_ratio_to_max_mp(width, height, max_mp)  # type: ignore
#         upscale_image = cv2.resize(
#             image, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_CUBIC)  # type: ignore
#         images.append({'name': image_name, 'width': width,
#                       'height': height, 'matImage': upscale_image, 'ratio': ratio})
#     return images  # type: ignore


# def save_upscales_dir_to_max_size(directory_path:  str, new_directory_path: str = '', max_mp: int = MAX_MP):
#     '''
#     @max_mp: max size in megapixels
#     '''
#     images = upscales_dir_to_max_size(
#         directory_path, new_directory_path, max_mp)
#     printTable({
#         'Name': [info['name'] for info in images],
#         'Width': [info['width'] for info in images],
#         'Height': [info['height'] for info in images],
#         'Ratio': [info['ratio'] for info in images],
#     })
