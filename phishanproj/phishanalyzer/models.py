from django.db import models


DATA_STATUS_CHOICES = [
        ("UP", "Uploaded"),
        ("AN", "Analyzing"),
        ("FN", "Finished"),
        ("ER", "Error"),
    ]

class Email(models.Model):
    analys_sid = models.CharField(max_length=30, unique=True)
    hash_sha256 = models.CharField(max_length=64)
    file = models.FileField(upload_to='emails/')
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.analys_sid
    
class Link(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    hash_sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.url
    
class Attachment(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    hash_sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.hash_sha256