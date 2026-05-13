from django.db import models
from authapp.models import CustomUser


DATA_STATUS_CHOICES = [
        ("UP", "Uploaded"),
        ("AN", "Analyzing"),
        ("FN", "Finished"),
        ("ER", "Error"),
    ]

class Email(models.Model):
    analys_sid = models.CharField(max_length=30, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    hash_sha256 = models.CharField(max_length=64)
    # Email fields - to let user identify his analyses
    email_from = models.CharField(max_length=100, null=True)
    email_to = models.CharField(max_length=150, null=True)
    email_subject = models.CharField(max_length=100, null=True)
    file = models.FileField(upload_to='emails/', null=True)
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)
    author = models.ManyToManyField(CustomUser, related_name="up_emails")

    def __str__(self):
        return self.analys_sid
    
class Link(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    vt_url_id = models.CharField(max_length=300)
    analysis_id = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.url
    
class Attachment(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/', null=True)
    analysis_id = models.CharField(max_length=200, null=True)
    hash_sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=2, choices=DATA_STATUS_CHOICES, default='UP')
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return self.hash_sha256