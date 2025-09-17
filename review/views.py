from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ProductReview, Feedback
from products.models import Product
from .forms import ProductReviewForm, FeedbackForm
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.



#post a product review
@login_required
def post_review(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()

    return render(request, 'review/post_review.html', {'form': form, 'product': product})


@login_required
def edit_review(request, review_id):

    review = ProductReview.objects.get(id=review_id)

    if request.user.role != 'ADMIN' or request.user != review.user:
        return render(request,'accounts/error_message.html',{'message':"You don't have permission to edit this review."})

    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = ProductReviewForm(instance=review)

    return render(request, 'review/edit_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, review_id):
    
    review = ProductReview.objects.get(id=review_id)

    if request.user.role != 'ADMIN' or request.user != review.user:
        return render(request,'accounts/error_message.html',{'message':"You don't have permission to delete this review."})

    product_id = review.product.id
    review.delete()
    return redirect('product_detail', product_id=product_id)


@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('product_list')  # Redirect to a thank you page or home page
    else:
        form = FeedbackForm()

    return render(request, 'review/submit_feedback.html', {'form': form})



@admin_required
def view_feedbacks(request):
    try:
        # Get filter/search parameters
        category = request.GET.get('category')
        about = request.GET.get('about')
        to_user = request.GET.get('to_user')

        # Build a unique cache key based on filters/search
        cache_key = f"feedbacks_{category}_{about}_{to_user}"

        # Try to get cached feedbacks
        feedbacks = cache.get(cache_key)

        if not feedbacks:
            # Start with all feedbacks
            feedbacks = Feedback.objects.all().order_by('-created_at')

            # Apply filters if present
            if category:
                feedbacks = feedbacks.filter(category=category)
            if about:
                feedbacks = feedbacks.filter(about=about)
            if to_user:
                feedbacks = feedbacks.filter(to_user__icontains=to_user)
            

            # Cache the result for 2 minutes
            cache.set(cache_key, feedbacks, timeout=60*2)

        # Pagination
        paginator = Paginator(feedbacks, 5)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'review/feed_back_list.html', {
            'feedbacks': feedbacks,
            'page_obj': page_obj,
            'paginator': paginator,
        })

    except Feedback.DoesNotExist:
        return render(request, 'accounts/error_message.html', {'message': "No feedbacks available."})



    



