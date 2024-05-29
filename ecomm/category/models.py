from django.db import models

# Create your models here.
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    cat_image= models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name='category'
        verbose_name_plural= 'categories'

    def __str__(self):
        return self.category_name
    

    def save(self, *args, **kwargs):
        # Delete old image file if a new one is uploaded
        try:
            this = Category.objects.get(id=self.id)
            if this.cat_image != self.cat_image:
                if os.path.isfile(this.cat_image.path):
                    os.remove(this.cat_image.path)
        except:
            pass

        super().save(*args, **kwargs)

@receiver(pre_delete, sender=Category)
def delete_category_image(sender, instance, **kwargs):
    # Delete the image file before deleting the category
    if instance.cat_image:
        if os.path.isfile(instance.cat_image.path):
            os.remove(instance.cat_image.path)