from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class QualificationDetails(models.Model):
    tensname = models.CharField(max_length=30)
    tengrade = models.CharField(max_length=10)
    tenpsyr = models.CharField(max_length=15)
    tencertificate = models.FileField(upload_to='uploads/', storage=S3Boto3Storage())
    twelvesname = models.CharField(max_length=30)
    twelvegrade = models.CharField(max_length=10)
    twelvepsyr = models.CharField(max_length=15)
    twelvecertificate = models.FileField(upload_to='uploads/', storage=S3Boto3Storage())
    mbbsinstitution = models.CharField(max_length=25)
    mbbsgrade = models.CharField(max_length=10)
    mbbspsyr = models.CharField(max_length=10)
    mbbsmarksheet = models.FileField(upload_to='uploads/', storage=S3Boto3Storage())
    mbbsdegree = models.FileField(upload_to='uploads/', storage=S3Boto3Storage())
    mdinstitution = models.CharField(max_length=25)
    mdgrade = models.CharField(max_length=10)
    mdpsyr = models.CharField(max_length=10)
    mddegree = models.FileField(upload_to='uploads/', storage=S3Boto3Storage())
