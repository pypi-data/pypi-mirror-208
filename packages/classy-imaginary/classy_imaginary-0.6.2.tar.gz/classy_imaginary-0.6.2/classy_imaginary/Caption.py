
import logging

import torch
from PIL import Image
from torchvision.transforms import transforms, InterpolationMode

from classy_imaginary.enhancers.describe_image_blip import BLIP_EVAL_SIZE, blip_model
from classy_imaginary.utils import get_device

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# logging.disable_default_handler()


class Caption:
    def __init__(self):
        """
        Initialize the Caption class.
        """
        self.caption_model = blip_model()
        self.device = get_device()

    def preprocess_image(self, image: Image) -> torch.Tensor:
        """
        Preprocess the input image.
        :param image: Image.
        :return: Preprocessed image tensor.
        """
        image = image.convert("RGB")
        preprocess = transforms.Compose(
            [
                transforms.Resize(
                    (BLIP_EVAL_SIZE, BLIP_EVAL_SIZE),
                    interpolation=InterpolationMode.BICUBIC,
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.48145466, 0.4578275, 0.40821073),
                    (0.26862954, 0.26130258, 0.27577711),
                ),
            ]
        )
        return preprocess(image).unsqueeze(0).to(self.device)

    def generate_caption(self,
                         image: Image,
                         min_length=30,
                         max_length=80,
                         num_beams=3) -> str:
        """
        Run inference on the model.
        :param image: Image.
        :param min_length: Minimum length of the caption.
        :param max_length: Maximum length of the caption.
        :param num_beams: Number of beams to use.
        """
        gpu_image = self.preprocess_image(image)
        print(gpu_image.shape)
        with torch.no_grad():
            caption = blip_model().generate(
                gpu_image, sample=True, num_beams=num_beams, max_length=max_length, min_length=min_length
            )
        return caption[0]
