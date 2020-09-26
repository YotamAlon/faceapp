from django.db import models
from django.db.models import Count
from faceapp.face import api, TooManyFaces


class FaceRequest(models.Model):
    status = models.CharField(max_length=64, choices=[('New', 'new'), ('Running', 'running'),
                                                      ('Done', 'done'), ('Failed', 'failed')])
    error = models.CharField(max_length=512)
    best_face = models.ForeignKey('Image', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def best_image(self):
        if self.best_face:
            return self.best_face.url
        return None

    @property
    def image_urls(self):
        return [image.url for image in self.image_set.all()]

    def execute(self):
        self.status = 'Running'
        self.save()

        try:
            for image in self.image_set.all():
                image.face_id, image.size = api.submit_image(image.url)
                image.save()
        except TooManyFaces as e:
            self.status = 'Failed'
            self.error = str(e)
            self.save()

        for image in self.image_set.all():
            if not image.similar_faces.count():
                face_ids = self.image_set.exclude(face_id=image.face_id).values_list('face_id', flat=True)
                same_face_face_ids = api.get_same_faces(image.face_id, face_ids)
                image.similar_faces.add(*self.image_set.filter(face_id__in=same_face_face_ids))

        most_common_face = sorted(self.image_set.all(), key=lambda x: x.similar_faces.count(), reverse=True)[0]
        largest_common_face = sorted(list(most_common_face.similar_faces.all()) + [most_common_face],
                                     key=lambda x: x.size, reverse=True)[0]

        self.best_face = largest_common_face
        self.status = 'Done'
        self.save()


class Image(models.Model):
    request = models.ForeignKey(FaceRequest, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    face_id = models.CharField(max_length=64, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    similar_faces = models.ManyToManyField('Image')