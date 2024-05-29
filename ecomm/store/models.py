from django.db import models
from category.models import Category
from brand.models import Brand
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
import os
from accounts.models import Account
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
    description=models.TextField(blank=True)
    video=models.FileField(upload_to='video/products',blank=True)
    video_thumbnail=models.ImageField(upload_to='video/products',blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    images=models.ImageField(upload_to='photos/products')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    is_featured=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    warranty=models.CharField(max_length=50,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    total_product_saled=models.IntegerField(blank=True)

    seo_description=models.TextField(blank=True)

    def related_products(self):
        return Product.objects.filter(category=self.category).exclude(id=self.id)
    

    @property
    def discount_percentage(self):
        if self.old_price:
            discount = self.old_price - self.price
            discount_percentage = (discount / self.old_price) * 100
            return round(discount_percentage)
        else:
            return 0

    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug,self.slug])


    def __str__(self):
        return self.product_name

@receiver(pre_delete, sender=Product)
def delete_product_files(sender, instance, **kwargs):
    if instance.images:
        if os.path.isfile(instance.images.path):
            os.remove(instance.images.path)
    if instance.video:
        if os.path.isfile(instance.video.path):
            os.remove(instance.video.path)
    if instance.video_thumbnail:
        if os.path.isfile(instance.video_thumbnail.path):
            os.remove(instance.video_thumbnail.path)

@receiver(pre_save, sender=Product)
def delete_old_product_files(sender, instance, **kwargs):
    if instance.pk:

        old_product = Product.objects.get(pk=instance.pk)
        if old_product.images != instance.images:
            if old_product.images:
                if os.path.isfile(old_product.images.path):
                    os.remove(old_product.images.path)
        if old_product.video != instance.video:
            if old_product.video:
                if os.path.isfile(old_product.video.path):
                    os.remove(old_product.video.path)
        if old_product.video_thumbnail != instance.video_thumbnail:
            if old_product.video_thumbnail:
                if os.path.isfile(old_product.video_thumbnail.path):
                    os.remove(old_product.video_thumbnail.path)


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)
    
variation_category_choise={
    ('color','color'),
    ('size','size'),
}

class Variation(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choise)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now=True)

    objects=VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,default=None)
    image=models.ImageField(upload_to='store/products',max_length=255)

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name='product gallery'
        verbose_name_plural='product Gallery'


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'attribute',)
        ordering = ['created_at'] 

class SeoKeyword(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seo_keyword=models.CharField(max_length=100,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product','seo_keyword')
        ordering = ['created_at'] 

class RecentlyVisited(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    products = models.ForeignKey(Product, related_name='visited_by', on_delete=models.CASCADE)
    last_visited = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Recently visited by {self.user.username}"

    class Meta:
        verbose_name_plural = "Recently Visited"