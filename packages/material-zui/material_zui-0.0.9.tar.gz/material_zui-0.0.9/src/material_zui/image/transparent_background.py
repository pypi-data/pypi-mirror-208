import cv2
from cv2 import Mat
from rembg import remove

# with open(input_path, 'rb') as i:
#     with open(output_path, 'wb') as o:
#         input = i.read()
#         output = remove(input)
#         o.write(output)  # type: ignore


def transparent_background(
    image: Mat) -> Mat: return remove(image)  # type: ignore


def save_transparent_background(image_path: str, output_path: str) -> None:
    input = cv2.imread(image_path)
    output = transparent_background(input)
    cv2.imwrite(output_path, output)
