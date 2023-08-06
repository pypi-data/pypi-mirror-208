import logging
from PIL import Image
import numpy as np

from classy_imaginary.enhancers.upscale_realesrgan import realesrgan_upsampler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Upscaler:
    def __init__(self):
        """
        Initialize the upscaler.
        """
        self.upscaler = realesrgan_upsampler()

    def upscale_image(self, img):
        """
        Upscale the image.
        """
        img = img.convert("RGB")

        np_img = np.array(img, dtype=np.uint8)
        upsampler_output, img_mode = self.upscaler.enhance(np_img[:, :, ::-1])
        return Image.fromarray(upsampler_output[:, :, ::-1], mode=img_mode)
