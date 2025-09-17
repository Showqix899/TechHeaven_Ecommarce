from django.urls import path

from .views import (
    post_review,
    edit_review,
    delete_review,
    view_feedbacks,
    submit_feedback,
)

urlpatterns = [
    path('post_review/<uuid:product_id>/', post_review, name='post_review'),
    path('edit_review/<uuid:review_id>/', edit_review, name='edit_review'),
    path('delete_review/<uuid:review_id>/', delete_review, name='delete_review'),
    path('view_feedbacks/', view_feedbacks, name='view_feedbacks'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
]