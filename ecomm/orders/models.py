from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
from accounts.models import Account
from store.models import Product,Variation
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from twilio.rest import Client

# Create your models here.
class Payment(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100,null=True)
    payment_method= models. CharField(max_length=100)
    amount_paid= models. CharField(max_length=100) # this is the total amount paid
    status= models.CharField(max_length=100)
    created_at =models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS = [
        ('PROCESSING', 'Processing'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out For Delivery'),
        ('DELIVERED', 'Delivered'),
    ]

    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True,null=True)
    order_number=models.CharField(max_length=20)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=50)
    house_no=models.CharField(max_length=50)
    area=models.CharField(max_length=50,blank=True)
    landmark=models.CharField(max_length=300,blank=True)
    country=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    pincode=models.CharField(max_length=50)
    order_note=models.CharField(max_length=100,blank=True)
    order_total=models.FloatField()
    tax=models.FloatField()
    shipping_cost=models.FloatField()
    status=models.CharField(choices=STATUS,max_length=20, default='PROCESSING')
    ip=models.CharField(blank=True,max_length=20)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    expected_delivery_date = models.DateTimeField(blank=True, null=True)
    tracking_id = models.CharField(max_length=50, blank=True, null=True)
    courier_company_name = models.CharField(max_length=100, blank=True, null=True)




    def send_status_update_email(self):
        subject = 'Order Status Update'
        html_content = render_to_string('orders/order_status_email.html', {'order': self})
        text_content = f"Your order status has been updated to {self.get_status_display()}."
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [self.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


    def send_status_update_sms(self):
            try:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message_body = f"\n\nHi {self.first_name},\n\n"
                message_body += f"Your order {self.order_number} is {self.get_status_display()}.\n"
                message_body += f"The total price of your order is ${'{:.2f}'.format(self.order_total)}.\n\n"

                current_timezone = timezone.get_current_timezone()
                if self.status in ['SHIPPED', 'OUT_FOR_DELIVERY']:
                    message_body += f" The tracking ID is {self.tracking_id} and it's being shipped via {self.courier_company_name}.\n\n"
                if self.order_note:
                    message_body += f"Order Note: {self.order_note}\n\n"
                if self.status != 'DELIVERED' and self.expected_delivery_date:
                    expected_delivery_date_formatted = self.expected_delivery_date.strftime('%d %B %Y')
                    message_body += f"Expected delivery date: {expected_delivery_date_formatted}\n\n"
                if self.status == 'DELIVERED':
                    delivery_date_time = timezone.now().astimezone(current_timezone).strftime('%d-%m-%Y %I:%M %p')
                    message_body += f"Your order was delivered at {delivery_date_time}.\n"
                    message_body += "Please add a review of the product.\n\n"
                message_body += "Thank you for your recent order with us. We truly appreciate your business and the trust you've placed in our products/services.\n\n"
                message_body += "Please visit our website for more information: https://www.example.com\n\n"
                message = client.messages.create(
                    body=message_body,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=self.phone
                )
                print("SMS sent successfully! SID:", message.sid)
            except Exception as e:
                print("Failed to send SMS:", str(e))


    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    def __str__(self):
        return self.order_number
    

    
@receiver(pre_save, sender=Order)
def order_status_updated(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return  # New object, no need to check for status change

    if old_instance.status != instance.status:
        instance.send_status_update_email()
        instance.send_status_update_sms()

@receiver(pre_save, sender=Order)
def set_expected_delivery_date(sender, instance, **kwargs):
    if not instance.id:  # If the object is being created for the first time
        if instance.status != 'DELIVERED':
            instance.expected_delivery_date = timezone.now() + timedelta(days=5)
    elif instance.status == 'DELIVERED':
        instance.expected_delivery_date = timezone.now()

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey (Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey (Account, on_delete=models.CASCADE)
    product = models.ForeignKey (Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField (Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name