from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
# Create your models here.


class CustomAccountManager(BaseUserManager):
    def create_superuser(self,email,username,first_name,password,**kwargs):
        kwargs.setdefault('is_staff',True)
        kwargs.setdefault('is_superuser',True)
        kwargs.setdefault('is_active',True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('superuser must be assigned to is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('superuser must be assigned to is_superuser=True')
        return self.create_user(email,username,first_name,password,**kwargs)
    
    def create_user(self,email,username,first_name,password,**kwargs):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email,username=username,first_name=first_name,**kwargs)
        user.set_password(password)
        user.save()
        return user
    

class NewUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(_('email address'),unique=True)
    username = models.CharField(max_length=100,unique=True)
    first_name = models.CharField(max_length=150,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    joined_at = models.DateTimeField(default=timezone.now)
    about = models.TextField(_('about'),max_length=500,blank=True,null=True)
    photo = models.ImageField(null=True,blank=True,upload_to='users/')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name']

    def __str__(self):
        return self.username