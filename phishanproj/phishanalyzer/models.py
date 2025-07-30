from django.db import models


class Email(models.Model):
    EMAIL_STATUS_CHOICES = [
        ("UP", "Uploaded"),
        ("AN", "Analyzing"),
        ("FN", "Finished"),
        ("ER", "Error"),
    ]

    analys_sid = models.CharField(max_length=30, unique=True)
    hash_sha256 = models.CharField(max_length=64)
    file = models.FileField(upload_to='emails/')
    status = models.CharField(max_length=2, choices=EMAIL_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.analys_sid