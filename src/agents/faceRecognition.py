import logging
from typing import List, Optional
from PIL import Image
from face_recognition import load_image_file, face_encodings, compare_faces, face_locations
import numpy as np
from pathlib import Path
import cv2

class FaceRecognition:
    def __init__(self, known_faces: Optional[List[np.ndarray]] = None, tolerance: float = 0.6):
        """
        Initialize the FaceRecognition with known faces and a tolerance level.

        :param known_faces: List of known face encodings.
        :param tolerance: Tolerance for face comparison.
        """
        self.known_faces = known_faces if known_faces is not None else []
        self.tolerance = tolerance
        self.logger = logging.getLogger(__name__)

    def add_known_face(self, trustedFacesPath: str):
        """
        Add a known face from an image file.

        :param trustedFacesPath: Path to the image file containing the face.
        """
        for image in Path(trustedFacesPath).glob('*'):
            image = load_image_file(str(image))
            encodings = face_encodings(image)
            if encodings:
                self.known_faces.append(encodings[0])
                # self.logger.info(f"Added known face {image} from {trustedFacesPath}")
            else:
                self.logger.warning(f"No faces found in {trustedFacesPath}")

    def recognize_faces(self, image: cv2.Mat) -> List[bool]:
        """
        Recognize faces in the given image.

        :param image: The image to recognize faces in.
        :return: List of booleans indicating if each detected face matches a known face.
        """
        unknown_encodings = face_encodings(image)
        
        results = []
        for unknown_encoding in unknown_encodings:
            matches = compare_faces(self.known_faces, unknown_encoding, tolerance=self.tolerance)
            results.append(any(matches))
        
        return results

    def get_face_locations(self, image_path: str) -> List[tuple]:
        """
        Get the locations of faces in the given image.

        :param image_path: Path to the image file to find face locations in.
        :return: List of tuples representing the locations of detected faces.
        """
        image = load_image_file(image_path)
        locations = face_locations(image)
        return locations