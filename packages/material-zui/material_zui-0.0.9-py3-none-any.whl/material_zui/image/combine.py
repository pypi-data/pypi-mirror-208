# import cv2
# import uuid
# from cv2 import Mat
# from material_zui.image.data import IMG_EXT, MAX_MP
# from material_zui.image.index import get_image_info, get_image_paths, get_images
# from material_zui.image.upscale import get_image_ratio_to_max_mp


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


# def handle_image(directory_path: str, new_directory_path: str = '', extension: str = ''):
#     image_info = get_image_info(directory_path)
#     dir_name = image_info['dir_name']
#     ext = extension or image_info['extension']
#     new_image_path = f'{dir_name}/{str(uuid.uuid4())}.{ext}'
#     new_directory_path = new_directory_path if new_directory_path else new_image_path
#     # print(new_directory_path)

#     def handle_each_image(*functions):
#         result: Mat = image_info['image']
#         for function in functions:
#             result = function(result)
#         cv2.imwrite(new_directory_path, result)
#     return handle_each_image


# def handle_images(directory_path: str, new_directory_path: str = '', extension: str = ''):
#     image_paths = get_image_paths(directory_path)

#     def handle_each_image(*functions):
#         for image_path in image_paths:
#             image_info = get_image_info(image_path)
#             name = image_info['name']
#             ext = extension or image_info['extension']
#             output_image_path = ''
#             if new_directory_path and directory_path != new_directory_path:
#                 output_image_path = f'{new_directory_path}/{name}.{ext}'
#             handle_image(image_path, output_image_path, extension)(*functions)
#     return handle_each_image


# # def save_upscale_toJpg(directory_path:  str, new_directory_path: str = '', max_mp: int = MAX_MP) -> None:
# #     new_directory_path = new_directory_path if new_directory_path else directory_path
# #     images = get_images(directory_path)
# #     image_paths = get_image_paths(directory_path)
# #     for index, image in enumerate(images):
# #         ratio = get_image_ratio_to_max_mp(image, max_mp)
# #         image_url = upscale(image_paths[index], ratio)
# #         png_dir = f'{new_directory_path}/{index}.png'
# #         jpg_dir = f'{new_directory_path}/{index}.jpg'
# #         download(image_url, png_dir)
# #         to_jpg(png_dir, jpg_dir)
# #         print(index+1, jpg_dir, ratio)
