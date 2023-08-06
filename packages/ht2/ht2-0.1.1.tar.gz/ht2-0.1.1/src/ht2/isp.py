"""
image signal processings
"""
import cv2

def sim_img_artifact(img, jpg_compress_rate, mode="jpg"):
    """ compress image and reload to give image compress aritfact

    Args:
        img (_type_): _description_
        jpg_compress_rate (_type_): _description_

    Returns:
        _type_: _description_
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpg_compress_rate]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    im = cv2.imdecode(encimg, 0)
    return im