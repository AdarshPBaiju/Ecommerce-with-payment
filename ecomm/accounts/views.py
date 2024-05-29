from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm ,UserForm, UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from carts.models import Cart
from orders.models import Order,OrderProduct
from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests
from django.http import JsonResponse
from .utils import send_otp_email, send_otp_sms
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.urls import reverse_lazy
from django.conf import settings
from twilio.rest import Client
import random
import base64
import time
import random
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from  django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from urllib.parse import unquote


# Create your views here.

def generate_otp(length=4, expiration_time=300):
    otp = ''.join(random.choices('0123456789', k=length))
    encoded_otp = base64.b64encode(otp.encode()).decode()
    expiration_time = int(time.time()) + expiration_time
    return otp, encoded_otp, expiration_time

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulation Your account is activated. Now you can login')
        return redirect('login')
    else:
        messages.error(request,'Invalind activation link')
        return redirect('register')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email

            # Adding +91 to the phone number
            phone_number = phone_number.strip()
            if not phone_number.startswith('+91'):
                phone_number = '+91' + phone_number
            

            # Check if user with the given phone number already exists or not
            if Account.objects.filter(phone_number=phone_number).exists():
                # Add an error message to the form
                form.add_error('phone_number', 'Phone number is already registered!')
                return render(request, 'accounts/register.html', {'form': form})

            # Create the new user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                username=username,
                password=password
            )

            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/img_avatar.png'
            profile.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Activate Your Account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = "html"
            send_email.send()

            # Redirect to login page with a success message
            return redirect('/account/login/?command=verification&email=' + email)
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)



def handle_cart_merge(request, user):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(cart=cart)
            user_cart_items = CartItem.objects.filter(user=user)
            for cart_item in cart_items:
                if user_cart_items.filter(product=cart_item.product).exists():
                    user_cart_item = user_cart_items.get(product=cart_item.product)
                    user_cart_item.quantity += cart_item.quantity
                    user_cart_item.save()
                else:
                    cart_item.cart = None
                    cart_item.user = user
                    cart_item.save()
            cart.delete()
    except Cart.DoesNotExist:
        pass


def login(request):
    if request.user.is_authenticated:  
        return redirect('home')
    
    url = request.META.get('HTTP_REFERER')
    nextPage = None 
    try:
        query = requests.utils.urlparse(url).query
        params = dict(x.split('=') for x in query.split('&'))
        if 'next' in params:
            nextPage = params['next']
    except:
        pass
    if request.method == 'POST':
        email_or_phone = request.POST.get('email_or_phone')
        password = request.POST.get('password')

        # Check if email_or_phone is phone number and add country code if missing
        if email_or_phone.isdigit():
            email_or_phone = '+91' + email_or_phone

        # Authenticate user
        user = authenticate(username=email_or_phone, password=password)

        if user is not None:
            if user.is_active:
                if user.is_two_factor:
                    otp, encoded_otp, expiration_time = generate_otp()
                    if nextPage:
                        encoded_data = f"{user.id}:{encoded_otp}:{expiration_time}:{nextPage}"  
                    else:
                        encoded_data = f"{user.id}:{encoded_otp}:{expiration_time}"
                    request.session['otp_data'] = encoded_data
                    # Send OTP to email
                    send_otp_email(user.email, otp)
                    # Send OTP to phone number using Twilio
                    send_otp_sms(user.phone_number, otp)
                    return redirect('enter-otp')
                else:
                    handle_cart_merge(request, user)
                    auth_login(request, user)
                    messages.success(request, 'You are logged in.')
                    if nextPage:
                        return redirect(nextPage)
                    else:
                        return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Please check your mailbox or contact us.')
        else:
            messages.error(request, 'Invalid email/phone or password.')

    return render(request, 'accounts/login.html')


def enter_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        encoded_data = request.session.get('otp_data')

        if not encoded_data:
            messages.error(request, "OTP data not found in session.")
            return redirect('login')

        data_parts = encoded_data.split(':')
        user_id = data_parts[0]
        stored_encoded_otp = data_parts[1]
        stored_expiration_time = data_parts[2]
        nextPage = unquote(data_parts[3]) if len(data_parts) > 3 else None

        if not user_id:
            messages.error(request, "No user ID found.")
            return redirect('login')

        user = get_object_or_404(Account, pk=user_id)

        # Check if OTP has expired
        current_time = int(time.time())
        expiration_time = int(stored_expiration_time)
        if current_time > expiration_time:
            messages.error(request, "OTP has expired. Please request a new OTP.")
            del request.session['otp_data']
            return redirect('login')

        stored_otp = base64.b64decode(stored_encoded_otp.encode()).decode()

        if entered_otp != stored_otp:
            messages.error(request, "OTP doesn't match.")
            return redirect('enter-otp')

        # Handle successful OTP verification
        del request.session['otp_data']
        handle_cart_merge(request, user)
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'You are logged in.')
        if nextPage:
            return redirect(nextPage)
        else:
            return redirect('dashboard')
    else:
        # Check if the user came from the login page
        referer = request.META.get('HTTP_REFERER')
        if referer and 'login' in referer:
            return render(request, 'accounts/otp_enter.html')
        else:
            # If user didn't come from the login page, redirect to login
            messages.error(request, "Unauthorized access.")
            return redirect('login')


@login_required(login_url = 'login')
def logout(request):
    auth_logout(request)
    messages.success(request, "You are Logged out")
    return redirect('login')


@login_required(login_url = 'login')
def dashboard(request):
    orders=Order.objects.filter(user_id=request.user.id, is_ordered=True)
    orders_count=orders.count()

    userprofile=UserProfile.objects.get(user_id=request.user.id)
    context={
        'orders_count':orders_count,
        'userprofile':userprofile,
    }
    return render(request,'accounts/dashboard.html',context)

def forgotPassword(request):
    if request.method=='POST':
        email=request.POST['email']
        if  Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # send the mail with reset password link
            current_site=get_current_site(request)
            mail_subject='Reset Your Password'
            message=render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to= [to_email])
            send_email.content_subtype="html"
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request,'Account Does Not Exist')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been already expired')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.is_active=True
            user.save()
            messages.success(request,'Password reset successful. Please login with new password')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetPassword')
    return render(request,"accounts/resetPassword.html")

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal += i.product_price
    context={
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request, 'accounts/order_detail.html',context)


@login_required(login_url='login')
def validate_phone_number(request):
    if request.method == 'GET' and 'phone_number' in request.GET:
        phone_number = request.GET.get('phone_number')
        
        # Check if the phone number already exists in the database
        phone_number_exists = Account.objects.exclude(pk=request.user.pk).filter(phone_number=phone_number).exists()
        return JsonResponse({'phone_number_exists': phone_number_exists})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required(login_url='login')
def toggle_two_factor(request):
    if request.method == 'GET':
        user = request.user
        user.is_two_factor = not user.is_two_factor
        user.save()
        if user.is_two_factor:
            message = "Two-factor authentication has been enabled for your account."
        else:
            message = "Two-factor authentication has been disabled for your account."

        send_sms(user.phone_number, message)
        return redirect(reverse_lazy('dashboard'))
    
def send_sms(to_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        # Send SMS
        client.messages.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=message
        )
        print("SMS sent successfully.")
    except Exception as e:
        print("Failed to send SMS:", str(e))
