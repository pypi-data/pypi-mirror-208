from PIL import Image
from cv2 import Mat

ZuiImage = dict[{'name': str, 'ext': str, 'width': int, 'height': int,
                 'image': Image.Image, 'matImage': Mat,  'ratio': int}]

ZuiImageRes = dict[str, str | int | Image.Image | Mat | None]
