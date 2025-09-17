from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()
# Create your models here.


class ProductReview(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - Rating: {self.rating}"
    
    



class Feedback(models.Model):


    CATEGORY_CHOICES = [
        ("complaint", "Complaint"),
        ("improvement", "Improvement"),
    ]
    ABOUT_CHOICES = [
        ("feature", "Feature"),
        ("user", "User"),
        ("product", "Product"),
        ("bug_report", "Bug Report"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    comment = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,null=True, blank=True)
    about = models.CharField(max_length=20, choices=ABOUT_CHOICES,null=True, blank=True)
    to_user=models.CharField(max_length=200,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback from {self.user.username} at {self.created_at}"
