from django.shortcuts import render,HttpResponse
from order.models import Order
from django.contrib.auth.decorators import login_required

import stripe
from django.conf import settings

from cart.models import Cart, CartItem  # Adjust as needed
from cart.views import get_cart  # Assuming you use this helper
from django.shortcuts import redirect,get_object_or_404
from .tasks import send_payment_confirmation_email,cart_item_deletion,stock_updation
from .models import PaymentHistory
from userprofile.models import CustomUserProfile

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY #stripe secret key


@login_required
def select_payment_method(request,order_id):

    # Fetch the order based on the provided order_id and the logged-in user
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        

        


        if request.method == 'POST':

            method = request.POST.get('payment_method')

            if method == 'stripe':
                # Redirect to Stripe payment page
                return render(request, 'payment/stripe_payment.html', {'order': order,})
            elif method == 'ssl_commerz':
                # Redirect to SSL Commerz payment page
                return render(request, 'payment/ssl_commerz_payment.html', {'order': order,})
        
        # Render the payment method selection page
        return render(request, 'payment/select_payment.html', {'order': order})
            
    except Order.DoesNotExist:

        return render(request,'accounts/error_message.html',{'message':'Order not found or you do not have permission to view this order.'})
    

#stripe payment view
@login_required
def stripe_payment(request,order_id):

    #fetch order based on order_id and user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    user_profile = CustomUserProfile.objects.get(user=request.user)

    # Create a stripe payment intent
    if not order.is_paid:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount* 100),
            currency='bdt',  # Change to your desired currency
            metadata={
                'order_id': str(order.id),
                'user_id': request.user.id,
            }
        )
        order.payment_id = intent.id
        
        order.save()
        
    else:
        intent = stripe.PaymentIntent.retrieve(order.payment_id)

    
    
    return render(request, 'payment/stripe_payment.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Pass the public key to the template
        'client_secret': intent.client_secret,  # Pass the client secret for the payment intent
        'order':order,
        'user_profile':user_profile,
    })

    

#after payment success
def stripe_success(request,order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart=get_cart(request)
    message=""
    payemnt_history,created=PaymentHistory.objects.get_or_create(
        order=order,
        user=request.user,
        total_amount=order.total_amount,
        payment_method='Stripe',
        status='pending'  # Initial status
    )


    if not order.is_paid:
        # Mark the order as paid
        order.is_paid = True
        order.status = 'Paid'
        order.payment_method = 'Stripe'
        order.save()
        payemnt_history.status="success"
        payemnt_history.save()
        user_email=request.user.email
        message=f"payment was successfull. An email has been sent to {request.user.email}"

        stock_updation.delay(order_id) #to update stock
        send_payment_confirmation_email.delay(order.id,cart.id,user_email) #emailing user the payment info

        user_profile = CustomUserProfile.objects.get(user=request.user)
        user_profile.points += int(order.total_amount // 100)  # Assuming 1 point for every 100 currency units spent
        user_profile.save()



        try:
            # If the order is for multiple items, clear the cart
            cart = get_cart(request)
            cart_item_deletion.delay(cart.id)
            print("Cart items deleted successfully.")
            
        except Exception as e:
            print(f"showqi-> deleting cart item: {e}")
        
    else:
        message="Al ready paid"

        
    return render(request, 'payment/success.html', {'order': order,'message':message})


def stripe_cancel(request):
    return render(request, 'payments/cancel.html')


from django.core.paginator import Paginator
from django.http import JsonResponse



# List all payments for admin
@login_required
def payment_list(request):
    if request.user.role != "ADMIN":
        return HttpResponse("Need to be an Admin. You are not allowed")

    # Calculate total sell amount by looping, like you had before

    query = request.GET.get('query', '').strip()

    if query:
        # Filter payment history based on user email
        payment_list = PaymentHistory.objects.filter(user__email__icontains=query).order_by('-created_at')
    else:
        # Fetch all payment history records
        payment_list = PaymentHistory.objects.all().order_by('-created_at')

    
    total_sell_amount = 0
    for item in payment_list:
        total_sell_amount += item.total_amount

    # Pagination: always 5 per page
    paginator = Paginator(payment_list, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'payment/payment_list.html', {
        'total_order_amount': total_sell_amount,
        'orders_item': page_obj,  # paginated items
        'paginator': paginator,
        'page_obj': page_obj,
    })


from decimal import Decimal

@login_required
def redeem_points(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        user_profile = CustomUserProfile.objects.get(user=request.user)

        total_points = user_profile.points
        order_total = order.total_amount  # Decimal

        request.session['total_points']=total_points

        # Case 1: Already paid
        if order.is_paid:
            return render(request, 'accounts/message.html', {
                'message': 'Order is already paid. You cannot redeem points on a paid order.'
            })

        # Case 2: Order too small
        if order_total < Decimal('200'):
            return render(request, 'accounts/message.html', {
                'message': 'Order total must be at least 200 to redeem points.'
            })

        # Case 3: Not enough points
        if total_points < 10:
            return render(request, 'accounts/message.html', {
                'message': 'You need at least 10 points to redeem.'
            })

        # 🔹 Correct discount logic
        # 1 point = 1 BDT, but max discount = 10% of order total
        max_discount = order_total * Decimal('0.10')
        redeemable_amount = min(Decimal(total_points), max_discount)

        # Apply discount
        order.total_amount -= redeemable_amount
        order.save()

        # Deduct redeemed points
        user_profile.points -= int(redeemable_amount)
        user_profile.save()

        # Store discount info in session (as percentage)
        request.session['discount_limit'] =float((redeemable_amount / order_total) * 100)

        return redirect('stripe_payment', order_id=order.id)

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

    

    
