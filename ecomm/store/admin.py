from django.contrib import admin
from django import forms
from .models import Product,Variation,ReviewRating,ProductGallery,Specification,SeoKeyword,RecentlyVisited
from django.core.exceptions import ValidationError
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
class SeoKeywordInline(admin.TabularInline):
    model = SeoKeyword
    extra = 1

class VideoFileField(forms.FileField):
    def clean(self, value, initial=None):
        video = super().clean(value, initial)
        if video:
            if not video.name.endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv')):
                raise ValidationError("Only MP4, MOV, AVI, MKV, and WMV files are allowed.")
        return video

class ProductAdminForm(forms.ModelForm):
    video = VideoFileField(label='Video', required=False)
    class Meta:
        model = Product
        fields = '__all__'

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    search_fields = ['product_name']
    inlines = [ProductGalleryInline, SpecificationInline,SeoKeywordInline]


class VariationAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_value','is_active','created_at')
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_value','is_active')


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display=('user','subject','product','rating','created_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating,ReviewRatingAdmin)
admin.site.register(ProductGallery)
admin.site.register(RecentlyVisited)