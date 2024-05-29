from django.shortcuts import render
from category.models import Category
from brand.models import Brand
from store.models import Product,RecentlyVisited


def home(request):
    category=Category.objects.all()
    brand=Brand.objects.all()
    product=Product.objects.all().filter(is_available=True,is_featured=True)
    product_sale=Product.objects.filter(is_available=True,total_product_saled__gte=1).order_by('-total_product_saled')
    recently_visited_products = None
    if request.user.is_authenticated:
        recently_visited_products = RecentlyVisited.objects.filter(user=request.user).order_by('-last_visited')

    context={
        'category':category,
        'product':product,
        'brand':brand,
        'product_sale':product_sale,
        'recently_visited_products': recently_visited_products,
    }
    return render(request,'index.html',context)