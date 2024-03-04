from django.db import models
from django.contrib.auth.models import User
from team.models import Team
from product.models import Product
# Create your models here.


class Client(models.Model):

    team = models.ForeignKey(Team, related_name='clients', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='clients', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True, null= True)
    product_line = models.ForeignKey(Product, related_name='clients', on_delete=models.CASCADE)
    company = models.CharField(max_length=100, blank=True, null= True)
    job = models.CharField(max_length=100, blank=True, null= True)

    
    class Meta:
        ordering = ('name',)

    def  __str__(self):
        return self.name

class ClientFile(models.Model):
    team = models.ForeignKey(Team, related_name='client_files', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name= 'files', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='client_files', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='clientfiles')

    def __str__(self):
        return self.created_by.username
    

    
class Comment(models.Model):
    team = models.ForeignKey(Team, related_name='client_comments', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name= 'comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='client_comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField( null=True,)

    def __str__(self):
        return self.created_by.username





