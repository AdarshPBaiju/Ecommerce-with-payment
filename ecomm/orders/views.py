from django.shortcuts import render,redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from store.models import  Product
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings

# Create your views here.
def payments(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

        # Store transaction details inside payment model
        payment = Payment(
            user=request.user,
            payment_id=body['transID'],
            payment_method=body['payment_method'],
            amount_paid=order.order_total,
            status=body['status'],
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart item to order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price * item.quantity
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variation.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variation.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the product in stock and add the quantity of the product sold
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.total_product_saled += item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order received email and sms to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = order.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.content_subtype = "html"
        send_email.send()

        if order.is_ordered:
            try:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message_body = f"\n\nHi {order.first_name},\n\n"
                message_body += f"Your order {order.order_number} has been received. "
                message_body += f"The total price of your order is ${'{:.2f}'.format(order.order_total)}. Thank you!\n\n"
                message_body += "We appreciate your business.\n\n"
                message_body += "Please visit our website for more information: https://www.example.com\n\n"
                message = client.messages.create(
                    body=message_body,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=order.phone
                )
                print("SMS sent successfully! SID:", message.sid)
            except Exception as e:
                print("Failed to send SMS:", str(e))

        # Send order number and transaction id back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    except (Order.DoesNotExist, Exception) as e:
        print("Error processing payment:", str(e))
        return redirect('home')


def place_order(request, total=0, quantity=0):
    try:
        current_user = request.user

        # if the cart count is less than or equal to 0, then return redirect back to home
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')

        grand_total = 0
        tax = 0
        shipping_cost = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (3 * total) / 100

        # Calculate shipping cost based on total
        if total > 100:
            shipping_cost = 0
        elif total == 0:
            shipping_cost = 0
        else:
            shipping_cost = 10

        grand_total = total + tax + shipping_cost

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                # Store all the billing information inside order table
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.house_no = form.cleaned_data['house_no']
                data.area = form.cleaned_data['area']
                data.landmark = form.cleaned_data['landmark']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.pincode = form.cleaned_data['pincode']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = grand_total
                data.tax = tax
                data.shipping_cost = shipping_cost
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                # Generate order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()
                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_item': cart_items,
                    'total': total,
                    'tax': tax,
                    'shipping_cost': shipping_cost,
                    'grand_total': grand_total,
                }
                return render(request, 'orders/payments.html', context)
            else:
                return redirect('checkout')
    except Exception as e:
        print("Error placing order:", str(e))
        return redirect('home')


def order_complete(request):
    try:
        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        total = 0
        for i in ordered_products:
            total += i.product_price

        tax = (3 * total) / 100

        # Calculate shipping cost based on total
        if total > 100:
            shipping_cost = 0
        elif total == 0:
            shipping_cost = 0
        else:
            shipping_cost = 10

        grand_total = total + tax + shipping_cost

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': total,  # Using total as subtotal
            'tax': tax,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total,  # Add grand_total to the context
        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist, Exception) as e:
        print("Error completing order:", str(e))
        return redirect('home')