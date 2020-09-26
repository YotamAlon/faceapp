import os
import time
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

KEY = os.environ['AZURE_KEY']
ENDPOINT = 'https://face-show.cognitiveservices.azure.com/'


class TooManyFaces(Exception): pass


class FaceAPI(object):
    limit_per_minute = 20

    def __init__(self):
        self.client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

    def sleep_after_query(self):
        time.sleep(60 / self.limit_per_minute)

    def detect_face(self, url):
        detected_faces = self.client.face.detect_with_url(url=url)
        self.sleep_after_query()
        return detected_faces

    def find_similar(self, face_id, face_ids):
        similar_faces = self.client.face.find_similar(face_id=face_id, face_ids=face_ids)
        self.sleep_after_query()
        return similar_faces

    def submit_image(self, url):
        detected_faces = self.detect_face(url)
        if len(detected_faces) > 1:
            raise TooManyFaces(f'The image {url} contains more than one face')

        face_size = detected_faces[0].face_rectangle.width * detected_faces[0].face_rectangle.height
        return detected_faces[0].face_id, face_size

    def get_same_faces(self, face_id, face_ids):
        similar_faces = self.find_similar(face_id, face_ids)
        return [similar_face.face_id for similar_face in similar_faces]


api = FaceAPI()