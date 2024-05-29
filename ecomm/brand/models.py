from django.db import models

# Create your models here.
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os

# Create your models here.
class Brand(models.Model):
    brand_name=models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    brand_image= models.ImageField(upload_to='photos/brand', blank=True)


    def __str__(self):
        return self.brand_name
    

    def save(self, *args, **kwargs):
        # Delete old image file if a new one is uploaded
        try:
            this = Brand.objects.get(id=self.id)
            if this.brand_image != self.brand_image:
                if os.path.isfile(this.brand_image.path):
                    os.remove(this.brand_image.path)
        except:
            pass

        super().save(*args, **kwargs)

@receiver(pre_delete, sender=Brand)
def delete_brand_image(sender, instance, **kwargs):
    # Delete the image file before deleting the category
    if instance.brand_image:
        if os.path.isfile(instance.brand_image.path):
            os.remove(instance.brand_image.path)