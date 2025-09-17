from django.db import models
import uuid
from django.contrib.auth import get_user_model


User=get_user_model()

# Create your models here.
class ActivityLog(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event=models.CharField(max_length=255,null=True,blank=True)
    action=models.CharField(max_length=255,null=tuple,blank=True)
    payload=models.JSONField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)



