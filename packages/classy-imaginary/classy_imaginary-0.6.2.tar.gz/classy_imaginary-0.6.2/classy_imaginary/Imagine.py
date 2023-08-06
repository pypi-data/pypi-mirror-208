from typing import Optional

import torch

from classy_imaginary import config
from classy_imaginary.api import _generate_single_image
from classy_imaginary import ImaginePrompt, ImagineResult
from classy_imaginary.enhancers.face_restoration_codeformer import codeformer_model
from classy_imaginary.model_manager import get_diffusion_model
from classy_imaginary.safety import EnhancedStableDiffusionSafetyChecker
from classy_imaginary.utils import platform_appropriate_autocast, fix_torch_nn_layer_norm, fix_torch_group_norm
from transformers import logging as transformers_logging, AutoFeatureExtractor
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
transformers_logging.set_verbosity_error()


class Imagine:
    def __init__(self,
                 model_name: str = config.DEFAULT_MODEL,
                 model_weights_path: str = None,
                 control_model_name: str = None,
                 half_mode: bool = None,
                 precision="autocast",
                 for_inpainting: bool = False
                 ):
        """
        Initialize the Imagine class.
        :param model_name: the name of the SD model to use.
        :param model_weights_path: the path to the model weights to use.
        :param half_mode: whether to use half-precision. If None, will use half-precision if available.
        :param precision: whether to use autocast or not.
        :param for_inpainting: whether to use the model for inpainting.
        """
        self.model_name = model_name
        self.control_model_name = control_model_name
        self.half_mode = half_mode
        self.precision = precision
        model_config = config.get_model_config(model_name)
        control_model_config = config.get_control_model_config(self.control_model_name) if self.control_model_name else None

        if model_config is None:
            raise ValueError(f"Unknown model name: {model_name}")

        if model_weights_path is not None:
            model_config.weights_url = model_weights_path

        self.sd_model = get_diffusion_model(
            weights_location=model_config.weights_url,
            config_path=model_config.config_path,
            control_weights_location=control_model_config.weights_url if control_model_config else None,
            half_mode=half_mode,
            for_inpainting=for_inpainting,
        )

    def imagine(self,
                prompt: ImaginePrompt,
                nsfw_filter: bool = False,
                debug_img_callback=None,
                progress_img_callback=None,
                progress_img_interval_steps=3,
                progress_img_interval_min_s=0.1) -> Optional[ImagineResult]:
        """
        Run inference on the model.
        :param prompt: ImaginePrompt.
        :param nsfw_filter: whether to filter out NSFW images.
        :param debug_img_callback: a callback that will be called with the debug image.
        :param progress_img_callback: a callback that will be called with the progress image.
        :param progress_img_interval_steps: the number of steps between progress images.
        :param progress_img_interval_min_s: the minimum time between progress images.
        :return: a list of ImagineResult objects.
        """
        with torch.no_grad(), platform_appropriate_autocast(
                self.precision,
        ), fix_torch_nn_layer_norm(), fix_torch_group_norm():
            result = _generate_single_image(
                prompt,
                self.sd_model,
                nsfw_filter=nsfw_filter,
                safety_feature_extractor=None,
                safety_checker=None,
                codeformer_model=None,
                debug_img_callback=debug_img_callback,
                progress_img_callback=progress_img_callback,
                progress_img_interval_steps=progress_img_interval_steps,
                progress_img_interval_min_s=progress_img_interval_min_s,
                add_caption=False,
            )

            return result
