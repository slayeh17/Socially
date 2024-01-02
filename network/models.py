from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Posts(models.Model):
    post = models.CharField(max_length=140)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="post_like")

    def likes_count(self):
        return self.likes.count()
    
    def __str__(self):
        return f"Post {self.id} made by {self.user} at {self.date}"
    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")

    def __str__(self):
        return f"{self.user} follows {self.user_follower}"