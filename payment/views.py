from django.shortcuts import render
from . models import ShippingAddress,Order,OrderItem
from cart.cart import Cart
from django.http import JsonResponse
# razorpay 
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from decimal import Decimal
import json
import math

#authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# Create your views here.
def checkout(request):
    # Users with accounts -- Pre-fill the form
    if request.user.is_authenticated:
        try:
            # Authenticated users WITH shipping information 
            shipping_address = ShippingAddress.objects.get(user=request.user.id)
            context = {'shipping': shipping_address}
            return render(request, 'payment/checkout.html', context=context)
        except:
            # Authenticated users with NO shipping information
            return render(request, 'payment/checkout.html')
    else:
        # Guest users
        return render(request, 'payment/checkout.html')

   # return render(request,'payment/checkout.html')

def payment_success(request):
     # Clear shopping cart
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]
    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    
    return render(request,'payment/payment-failed.html')

def complete_order(request):
     if request.POST.get('action') == 'post':

        name = request.POST.get('name')
        email = request.POST.get('email')

        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')

        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')


        # All-in-one shipping address
        shipping_address = (address1 + "\n" + address2 + "\n" + city + "\n" + state + "\n" + zipcode)
        
        # Shopping cart information 
        cart = Cart(request)
        
        # Get the total price of items
        total_cost = cart.get_total()
        '''
            Order variations
            1) Create order -> Account users WITH + WITHOUT shipping information
            2) Create order -> Guest users without an account
        '''
          # 1) Create order -> Account users WITH + WITHOUT shipping information
        if request.user.is_authenticated:
            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address,
            amount_paid=total_cost, user=request.user)
            order_id = order.pk
            for item in cart:
                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'],
                price=item['price'], user=request.user)
                
         #  2) Create order -> Guest users without an account
        else:
            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address,
            amount_paid=total_cost)
            order_id = order.pk
            
            for item in cart:
                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'],
                price=item['price'])
        order_success = True

        response = JsonResponse({'success':order_success})
        return response
    
def process_payment(request):
    #authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    # Shopping cart information 
    cart = Cart(request)
        
    # Get the total price of items
    total_cost = int(cart.get_total())
    decimal_value = int(Decimal(total_cost))
    json_serializable_value = float(decimal_value)
    json_data = json.dumps(json_serializable_value)
    # print(json_data)
    # print(type(json_data))
    float_value = float(json_data)
    integer_value = int(float_value)
    # print(integer_value)
    # print(type(integer_value))
    
    # converting float to integer
    
    # round_off = math.ceil(json_data)
    # int_val = int(json_data)
    
    currency = 'INR'
    amount = integer_value
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='1'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
    
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'payment/process-payment.html', context=context)

@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = amount  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return redirect('payment/payment-success.html')
                except:
 
                    # if there is an error while capturing payment.
                    return redirect(request, 'payment/payment-failed.html')
            else:
 
                # if signature verification fails.
                return redirect(request, 'payment/payment-failed.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()