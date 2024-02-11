from django.db import models
from django.contrib.auth.models import User
from PIL import Image

LANGS = (
    ('py', 'Python'),
    ('js', 'JavaScript'),
    ('c++', 'C++')
)


class Lang(models.Model):
    shortname = models.TextField(max_length=20)
    fullname = models.TextField(max_length=200)


class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.ForeignKey(to=Lang, blank=True, null=True, on_delete=models.PROTECT, related_name='lang')
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True, related_name='user')

    def __repr__(self):
        return f'Snippet({self.name}, {self.lang})'

    def __str__(self):
        return repr(self)


class Comment(models.Model):
    text = models.TextField(max_length=2500)
    creation_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')
    snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')
    image = models.ImageField(upload_to="images", default=None, blank=True, null=True)

    def __str__(self):
        return f'Comment({self.text})'
