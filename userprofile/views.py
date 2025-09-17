from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUserProfile, UserAddress
from .forms import CustomUserProfileForm, UserAddressForm
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.core.cache import cache
#import cache


# Create your views here.



# Profile detail view
@login_required
def profile_detail(request):
    user = request.user

    # Try cache first
    profile = cache.get(f'profile_{user.id}')
    addresses = cache.get(f'addresses_{user.id}')

    # If not cached, fetch from DB
    if not profile:
        profile = get_object_or_404(CustomUserProfile, user=user)
        cache.set(f'profile_{user.id}', profile, timeout=60*5)

    if not addresses:
        addresses = UserAddress.objects.filter(profile=profile)
        cache.set(f'addresses_{user.id}', addresses, timeout=60*5)

    return render(request, 'userprofile/profile_detail.html', {
        'profile': profile,
        'addresses': addresses
    })
    







#profile update
@login_required
def profile_update(request):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = CustomUserProfileForm(instance=profile)
    return render(request, 'userprofile/profile_form.html', {'form': form})



#address update

@login_required
def address_create(request):
    if request.method == 'POST':
        form = UserAddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = request.user.profile
            address.save()
            return redirect('profile_detail')
        
    else:
        form = UserAddressForm(user=request.user)
    return render(request, 'userprofile/address_form.html', {'form': form})




# Update Address
@login_required
def address_update(request, pk):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    address = get_object_or_404(UserAddress, pk=pk, profile=profile)
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')  # Change to your profile page name
    else:
        form = UserAddressForm(instance=address)
    return render(request, 'userprofile/address_update.html', {'form': form})

# Delete Address
@login_required
def address_delete(request, pk):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    address = get_object_or_404(UserAddress, pk=pk, profile=profile)
    if request.method == 'POST':
        address.delete()
        return redirect('profile_detail')  # Change to your profile page name
    return render(request, 'userprofile/address_delete.html', {'address': address})


@admin_required
def user_profile_list(request):

    try:

        profiles=cache.get('admin_user_profile_list')

        if not profiles:

            profiles = CustomUserProfile.objects.all()
            cache.set('admin_user_profile_list', profiles, timeout=60*5)
        return render(request, 'userprofile/user_profile_list.html', {'profiles': profiles})
    except CustomUserProfile.DoesNotExist:
        profiles = None
    return render(request, 'userprofile/user_profile_list.html', {'profiles': profiles})


#admin profile detail view
@admin_required
def admin_profile_detail(request, pk):

    try:

        profile = cache.get('profile_'+str(pk))

        if not profile:


            profile = CustomUserProfile.objects.get(pk=pk)
            addresses = UserAddress.objects.filter(profile=profile)
            cache.set('profile_'+str(pk), profile, timeout=60*5)



        return render(request, 'userprofile/profile_detail.html', {
                'profile': profile,
                'addresses': addresses
        })
    except CustomUserProfile.DoesNotExist:
        profile = None
    return render(request, 'userprofile/profile_detail.html', {'profile': profile})


#admin profile update
@admin_required
def admin_profile_update(request, pk):
    try:
        profile = CustomUserProfile.objects.get(pk=pk)
        if request.method == 'POST':
            form = CustomUserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('user_profile_detail', pk=profile.pk)
        else:
            form = CustomUserProfileForm(instance=profile)
        return render(request, 'userprofile/profile_form.html', {'form': form})
    except CustomUserProfile.DoesNotExist:
        profile = None
    return render(request, 'userprofile/profile_form.html', {'form': None})