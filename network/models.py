from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userID")
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/project4/', blank=True, null=True) # esto de imagenes aun no lo he puesto
    

    def __str__(self):
        return f"Post {self.id} by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")
    
    def __str__(self):
        return f"{self.user} is following{self.user_follower}"
    
    # desde like no lo he terminado    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} liked {self.post}"
