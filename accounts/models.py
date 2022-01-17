import datetime
import os
from datetime import date

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def normalize_phone(self, name):
        return name.lower().strip()

    def __create(self, phone, email, password):
        if not email:
            raise ValueError("Users must have an email address")
        if not phone:
            raise ValueError("Users must have an phone number")
        user = self.model(
            email=self.normalize_email(email), phone=self.normalize_phone(phone),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, email, password=None):
        user = self.__create(phone, email, password)
        user.save()
        return user

    def create_superuser(self, phone, email, password=None):
        user = self.__create(phone, email, password)
        user.is_admin = True
        user.save()
        return user


class MyUser(AbstractBaseUser):
    phone = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin



def upload_image(instance, filename):
    return "accounts/{user}/{batch}/{filename}".format(
        user=instance.batch.user.id, batch = instance.batch.id ,filename=filename
    )



def upload_image_pdf(instance, filename):
    return "pdfs/{user}/{batch}/{filename}".format(
        user=instance.batch.user.id, batch = instance.batch.id ,filename=filename
    )

class Profile(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name


class Batch(models.Model):
    created_date = models.CharField(max_length=20, blank=True, editable=False)
    description = models.CharField(max_length=200,)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.created_date = str(date.today())
        super(Batch, self).save(*args, **kwargs)

    def __str__(self):
        return self.description


key_store = FileSystemStorage(location='account/files/')

def key_store_upload_to(instance, path):
    # prepend date to path
    return os.path.join(
        datetime.date.today().isoformat(),
        path
    )

class File(models.Model):
    file_path = models.FileField(upload_to=upload_image,null=False)
    # pdf_path = models.FileField(upload_to=upload_image_pdf, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.batch.user, self.batch)


class Pdf_Bundels(models.Model):
    pdf_paths = models.FileField(upload_to='pdfs')

    class Meta:
        db_table = "Pdf_Bundels"

