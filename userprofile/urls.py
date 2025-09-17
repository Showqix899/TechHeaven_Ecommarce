from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    profile_detail, profile_update, address_create,
    address_update,address_delete,user_profile_list,
    admin_profile_update,admin_profile_detail
)

urlpatterns = [
        path('profile/', profile_detail, name='profile_detail'),
        path('profile/edit/', profile_update, name='profile_update'),
        path('address/add/', address_create, name='address_create'),
        path('address/edit/<int:pk>/', address_update, name='address_update'),  # Assuming you want to edit addresses too
        path('address/delete/<int:pk>/',address_delete,name='address_delete'),# Assuming you want to edit addresses too
        path('profiles/', user_profile_list, name='user_profile_list'),
        path('profile/admin/update/<int:pk>/',admin_profile_update,name="admin_profile_update"),
        path('profile/admin/detail/<int:pk>/',admin_profile_detail,name="admin_profile_detail"),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)