from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from .models import Product,ReviewRating,ProductGallery,Specification,SeoKeyword,RecentlyVisited
from django.contrib import messages
from .forms import ReviewForm
from category.models import Category
from brand.models import Brand
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from carts.models import CartItem
from carts.views import _cart_id
from django.http import Http404
from orders.models import Order
from django.db.models import Avg
from accounts.models import UserProfile
from django.db.models import Avg
from django.db.models import Count
from django.utils import timezone

# Create your views here.

def store(request):
    query = request.GET.get('q')
    orderby = request.GET.get('orderby')
    selected_brands = request.GET.getlist('brand')  # Extract list of selected brands

    products = Product.objects.filter(is_available=True)

    # Filter products by selected brand
    if selected_brands:
        products = products.filter(brand__brand_name__in=selected_brands)

    if query:
        products = products.filter(
            Q(seokeyword__seo_keyword__icontains=query) |
            Q(seo_description__icontains=query) |
            Q(category__category_name__icontains=query) |
            Q(brand__brand_name__icontains=query) |
            Q(product_name__icontains=query)
        ).distinct()

    product_count = products.count()
    show_sorting = products.count() > 1

    if orderby == 'popularity':
        products = products.order_by('-is_featured')
    elif orderby == 'date':
        products = products.order_by('-created_at')
    elif orderby == 'price-low':
        products = products.order_by('price')
    elif orderby == 'price-high':
        products = products.order_by('-price')

    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    for index, product in enumerate(paginated_products):
        product.index = (paginated_products.number - 1) * paginator.per_page + index + 1

    # Fetch brands associated with filtered products
    all_brands = Brand.objects.filter(product__in=products).annotate(
        num_products=Count('product')).order_by('-num_products')

    context = {
        'products': paginated_products,
        'query': query,
        'product_count': product_count,
        'orderby': orderby,
        'show_sorting': show_sorting,
        'all_brands': all_brands,
        'selected_brands': selected_brands
    }

    return render(request, 'store/store.html', context)





def category(request):
    categories = Category.objects.all()
    return render(request,'category/cat_list.html',{'categories':categories})

def category_product(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category,is_available=True)

    product_count = products.count()

    context = {
        'category'     : category,
        'products'     : products,
        'product_count': product_count,
    }
    return render(request, 'category/cat_product.html',context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug,is_available=True)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        related_products = single_product.related_products()
        specifications = Specification.objects.filter(product=single_product).order_by('created_at')
        has_specifications = specifications.exists()
        current_url = request.build_absolute_uri()
        seo_keywords = SeoKeyword.objects.filter(product=single_product)
        recently_visited_products = None
        if request.user.is_authenticated:
            recently_visited, created = RecentlyVisited.objects.get_or_create(user=request.user, products=single_product)
            recently_visited.last_visited = timezone.now()
            recently_visited.save()
            recently_visited_products = RecentlyVisited.objects.filter(user=request.user).exclude(products=single_product).order_by('-last_visited')
    except Product.DoesNotExist:
        return render(request, 'store/404.html')

    # Get the user's IP address
    user_ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

    # Check if the user has purchased the product
    has_purchased = False
    form = None
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user, orderproduct__product=single_product, status='DELIVERED')
        if orders.exists():
            has_purchased = True

    # Check if the user has already reviewed the product
    existing_review = None
    if has_purchased:
        existing_review = ReviewRating.objects.filter(user=request.user, product=single_product).first()

    # Review Form Handling
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            if has_purchased:
                review = form.save(commit=False)
                review.product = single_product
                review.user = request.user
                review.ip = user_ip
                
                if existing_review:
                    # Update existing review
                    existing_review.subject = review.subject
                    existing_review.review = review.review
                    existing_review.rating = review.rating
                    existing_review.save()
                    messages.success(request, "Your review has been updated successfully.")
                else:
                    # Create new review
                    review.save()
                    messages.success(request, "Thank you for your review!")
            else:
                messages.warning(request, "You can only review products you have purchased.")
        else:
            messages.error(request, "There was an error processing your review.")
        
        return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)
    else:
        form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()

     # Get review count for the product
    review_count = ReviewRating.objects.filter(product=single_product).count()

    # Calculate average rating for the product
    average_rating = ReviewRating.objects.filter(product=single_product).aggregate(Avg('rating'))['rating__avg']
    # Fetch product reviews
    product_reviews = ReviewRating.objects.filter(product=single_product)
    for review in product_reviews:
        if review.rating:
            rating_percentage = (review.rating / 5) * 100
            review.rating_percentage = rating_percentage
        else:
            review.rating_percentage = 0

        # Load profile picture for each user who left a review
        try:
            user_profile = UserProfile.objects.get(user=review.user)
            review.user_profile_picture = user_profile.profile_picture.url
        except UserProfile.DoesNotExist:
                # Use a default profile picture URL if UserProfile does not exist
            review.user_profile_picture = None


    # Convert average rating to a scale of 5
    if average_rating:
        average_rating_5star = (average_rating / 5) * 100
    else:
        average_rating_5star = 0

    product_gallery=ProductGallery.objects.filter(product_id=single_product.id)
    

    context = {
        "single_product": single_product,
        'in_cart': in_cart,
        'form': form,
        'average_rating_5star': average_rating_5star,
        'review_count': review_count,
        'product_reviews': product_reviews,
        'has_purchased': has_purchased,
        'product_gallery': product_gallery,
        'related_products': related_products,
        'specifications': specifications,
        'has_specifications': has_specifications,
        'current_url':current_url,
        'seo_keywords': seo_keywords,
        'recently_visited_products': recently_visited_products,
    }
    return render(request, 'store/product_detail.html', context)
