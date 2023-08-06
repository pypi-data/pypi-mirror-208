import logging
from PIL import Image
import numpy as np

from classy_imaginary.enhancers.face_restoration_codeformer import codeformer_model, enhance_faces

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FixFaces:
    def __init__(self):
        """
        Initialize the FixFaces class.
        """
        self.codeformer_net_model = codeformer_model()

    def fix_faces(self, img, fidelity=0.5):
        """
        Fix faces in an image.
        """
        return enhance_faces(img,
                             net=self.codeformer_net_model,
                             fidelity=fidelity)
