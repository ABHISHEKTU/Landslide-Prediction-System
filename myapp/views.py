from datetime import datetime
from time import timezone
from urllib import request

from django.shortcuts import render
from django.contrib.auth.models import User,Group
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib import messages

from myapp.models import *

# Create your views here.
def admin_home(request):
    return render(request, 'admin_home.html')


def home(request):
    return render(request, 'home.html')

def admin_manage_authority(request):

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        place = request.POST.get('place')
        district = request.POST.get('district')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('authority_registration')

        # Check if email already exists in Authority table
        if Authority.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('authority_registration')

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Add user to authority group
        group, created = Group.objects.get_or_create(name='authority')
        user.groups.add(group)

        # Create Authority profile
        Authority.objects.create(
            USER_ID=user,
            name=name,
            email=email,
            phone=phone,
            district=district,
            place=place,
        )

        messages.success(request, 'Registration Completed.')
        return redirect('admin_view_authority')

    return render(request, 'admin_manage_authority.html')


def admin_view_authority(request):
    authorities = Authority.objects.all()
    return render(request, 'admin_view_authority.html', {'authorities': authorities})

def admin_delete_authority(request, authority_id):
    authority = Authority.objects.get(id=authority_id)
    user = authority.USER_ID
    user.delete()  # This will also delete the associated Authority profile due to OneToOne relationship
    messages.success(request, 'Authority deleted successfully.')
    return redirect('admin_view_authority')

def admin_edit_authority(request, authority_id):
     authority = Authority.objects.get(id=authority_id)
     if request.method == 'POST':
         name=request.POST['authority_name']
         email=request.POST['email']
         phone=request.POST['phone']
         place=request.POST['place']
         district=request.POST['district']


         authority.name=name
         authority.email=email
         authority.phone=phone
         authority.place=place
         authority.district=district
         authority.save()
         messages.success(request, 'Authority updated successfully.')
         return redirect('admin_view_authority')
     return render(request, 'admin_edit_authority.html', {'authority': authority})

@never_cache
@csrf_exempt
def user_registration(request):
    if request.method == "POST":
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone=request.POST['phone']
        place=request.POST['place']
        district=request.POST['district']
        latitude=request.POST['lati']
        longitude=request.POST['longi']
        username=request.POST['username']
        password=request.POST['password']

        # print("USERNAME:", username)
        # print("PASSWORD,email:", password, email)
       
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('user_registration')

        # Create user using Django's auth system
        user = User.objects.create_user(username=username, password=password)
        user.save()

        try:
            group = Group.objects.get(name='user')
        except Group.DoesNotExist:
            group = Group.objects.create(name='user')
        user.groups.add(group)

        # Create care center profile
        UserProfile.objects.create(
            USER_ID=user,
            first_name=first_name,
            last_name=last_name,
            district=district,
            email=email,   
            phone=phone,
            place=place,
            longitude=longitude,
            latitude=latitude,

        )

        messages.success(request, 'Registration Completed. Please wait for the approval.')

    return render(request, 'user_registration.html')


@csrf_exempt
@never_cache
def emergency_notification(request):
    a=EmergencyNotification.objects.all()
    if request.method=='POST':
        title=request.POST['title']
        description=request.POST['description']
        # date=request.POST['date']

        EmergencyNotification.objects.create(
            title=title,
            description=description,
            date=datetime.now().strftime('%d/%m/%Y %I:%M %p'),  # Automatically set to current date and time
            status='pending'
        )
        return redirect('emergency_notification')

        messages.success(request, 'Emergency Notification Sent.')
       
    return render(request, 'emergency_notification.html',{'a':a})

    return render(request, 'view_reporting.html')

@csrf_exempt
@never_cache
def manage_helpline(request):
        b=HelplineNumber.objects.all()
        if request.method == 'POST':
            name = request.POST['helpline_name']
            phone = request.POST['helpline_number']
    
            HelplineNumber.objects.create(
                name=name,
                phone=phone
            )
            messages.success(request, 'Helpline number added successfully.')
            return redirect('manage_helpline')
        return render(request, 'manage_helpline.html',{'b':b})
def authority_home(request):
    return render(request, 'authority_home.html')
def profile(request):
    return render(request, 'profile.html')
def about(request):
    return render(request, 'about.html')
def update_profile(request):
    if request.method == 'POST':
        name = request.POST['authority_name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        district = request.POST['district']

        if 'authority_id' in request.session:
            authority_id = request.session['authority_id']
            authority_profile = Authority.objects.get(id=authority_id)
            authority_profile.name = name
            authority_profile.email = email
            authority_profile.phone = phone
            authority_profile.place = place
            authority_profile.district = district
            authority_profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    authority_profile = Authority.objects.get(id=request.session['authority_id'])
    return render(request, 'update_profile.html', {'authority_profile': authority_profile})


@csrf_exempt
@never_cache    
def report_landslide_authority(request):

    authority_id = User.objects.get(id=request.session['user_id'])
    print("AUTHORITY ID:", authority_id)
    authority = Authority.objects.get(USER_ID=authority_id)
    print("AUTHORITY OBJECT:", authority)
    c=AuthorityLandslideReport.objects.filter(AUTHORITY_ID=authority)  
       
    return render(request, 'report_landslide_authority.html',{ 'reports': c})



def report_landslide_users(request):
   
    # userprofile_id = User.objects.get(id=request.session['userprofile_id'])
    # print(" USERPROFILE ID:", userprofile_id)
    userprofile = UserProfile.objects.get(USER_ID=request.user)
    print("USERPROFILE OBJECT:", userprofile)
    c=UserLandslideReport.objects.filter(userProfile_ID=userprofile)  
       
    return render(request, 'report_landslide_users.html',{ 'reports': c})

def view_reporting_authority(request):
    if 'authority_id' in request.session:
        authority_id = request.session['authority_id']
        authority = Authority.objects.get(id=authority_id)
    c=UserLandslideReport.objects.all()  
    return render(request, 'view_reporting_authority.html', { 'reports': c})
def send_complaint_authority(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']

        a=User.objects.get(id=request.session['user_id'])
        authority = Authority.objects.get(USER_ID=a)
        Complaints.objects.create(
            USER_ID=a,
            title=title,
            description=description,
            date=datetime.now(),
            reply=''
        )
        messages.success(request, 'Complaint sent successfully.')
        return redirect('send_complaint_authority')
    d=Complaints.objects.filter(USER_ID=request.session['user_id'])
    return render(request, 'send_complaint_authority.html',{'complaints': d})
def view_reporting_admin(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
    d=AuthorityLandslideReport.objects.all()
    e=UserLandslideReport.objects.all()
    return render(request, 'view_reporting_admin.html', {'reports': d, 'user_reports': e})
def view_reporting_admin2(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
    e=UserLandslideReport.objects.all()
    return render(request, 'view_reporting_admin2.html', {'user_reports': e})
def user_home(request):
    return render(request, 'user_home.html')
def view_reporting_users(request):
    if 'userprofile_id' in request.session:
        userprofile_id = request.session['userprofile_id']
        userprofile = UserProfile.objects.get(id=userprofile_id)
        d=AuthorityLandslideReport.objects.all()
    return render(request, 'view_reporting_users.html', {'userprofile': userprofile, 'reports': d})
def send_emergency_notification(request):
    return render(request, 'send_emergency_notification.html')

def send_complaint_user(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']

        a=User.objects.get(id=request.session['user_id'])
        userprofile = UserProfile.objects.get(USER_ID=a)
        Complaints.objects.create(
            USER_ID=a,
            title=title,
            description=description,
            date=datetime.now(),
            reply=''
        )
        messages.success(request, 'Complaint sent successfully.')
        return redirect('send_complaint_user')
    c=Complaints.objects.filter(USER_ID=request.session['user_id'])
    return render(request, 'send_complaint_user.html',{'complaints': c})
def view_emergencyNoti_users(request):
    if 'userprofile_id' in request.session:
        userprofile_id = request.session['userprofile_id']
        userprofile = UserProfile.objects.get(id=userprofile_id)
    emergency_notifications = EmergencyNotification.objects.all()
    return render(request, 'view_emergencyNoti_users.html', {'emergency_notifications': emergency_notifications, 'userprofile': userprofile})
def view_emergencyNoti_authority(request):
    if 'authority_id' in request.session:
        authority_id = request.session['authority_id']
        authority = Authority.objects.get(id=authority_id)
    emergency_notifications = EmergencyNotification.objects.all()
    return render(request, 'view_emergencyNoti_authority.html', {'emergency_notifications': emergency_notifications})

def view_helpline_users(request):
    if 'userprofile_id' in request.session:
        userprofile_id = request.session['userprofile_id']
        userprofile = UserProfile.objects.get(id=userprofile_id)
    helpline_numbers = HelplineNumber.objects.all()
    return render(request, 'view_helpline_users.html', {'helpline_numbers': helpline_numbers})

def view_complaints(request):
    if 'userprofile_id' in request.session:
        userprofile_id = request.session['userprofile_id']
        userprofile = UserProfile.objects.get(id=userprofile_id)
    complaints = Complaints.objects.all()
    not_resolved=Complaints.objects.filter(reply='').count();
    resolved=Complaints.objects.exclude(reply='').count();
    return render(request, 'view_complaints.html', {'complaints': complaints, 'not_resolved': not_resolved, 'resolved': resolved})

@csrf_exempt
@never_cache
def login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        password = request.POST['password']
        a = User.objects.filter(username=uname).first()
        if a:
            if uname==a.username:

                user = authenticate(request, username=uname, password=password)
                print("USER : ", user)

                if user is not None:
                    auth_login(request, user)
                    request.session['user_id'] = user.id  # Auth user ID

                    if user.groups.filter(name='admin').exists():
                        return redirect('admin_home')  # Redirect to admin home
                    
                    if user.groups.filter(name='authority').exists():
                        authority = Authority.objects.get(USER_ID=user)
                        request.session['authority_id'] = authority.id
                        return redirect('authority_home')  # Redirect to authority home
                        
                    elif user.groups.filter(name='user').exists():
                        u = UserProfile.objects.get(USER_ID=user)
                        request.session['userprofile_id'] = u.id
                        return redirect('user_home')  # Redirect to user home
       
                    else:
                        messages.error(request, 'Invalid user')
                        return redirect('login')
                else:
                    messages.error(request, 'Username or password incorrect')
            else:
                    messages.error(request, 'Invalid username')
                    return redirect('login')
            
        else:
            messages.error(request, 'No such user exist in this platform')
            return redirect('login')
    return render(request, 'login.html')
def profile(request):
    if 'authority_id' in request.session:
        authority_id = request.session['authority_id']
        authority_id = Authority.objects.get(id=authority_id)
        print("AUTHORITY ID:", authority_id)
    return render(request, 'profile.html', {'user_profile': authority_id})
def reply_complaint(request, complaint_id):
    complaint = Complaints.objects.get(id=complaint_id)
    if request.method == 'POST':
        reply = request.POST['reply']
        complaint.reply = reply
        complaint.save()
        messages.success(request, 'Reply sent successfully.')
        return redirect('view_complaints')
    return render(request, 'reply_complaint.html', {'complaint': complaint})
def logout(request):
    request.session.flush()  # Clear all session data
    return redirect('login')







    # prediction======================================================================================

# =========================
# PAGE
# =========================

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from . import prediction
from .models import Authority, AuthorityLandslideReport


@login_required
def authority_landslide_page(request):
    if not Authority.objects.filter(USER_ID=request.user).exists():
        return redirect("login")
    return render(request, "authority_landslide_page.html")


# @csrf_exempt
# def landslide_predict_view_authority(request):
#     if not Authority.objects.filter(USER_ID=request.user).exists():
#         return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

#     response = prediction.landslide_prediction(request)

#     data = json.loads(response.content)
#     if data.get("status") == "success" and data.get("prediction") == "Landslide Prone":
#         now = timezone.now()
#         authority = Authority.objects.get(USER_ID=request.user)
#         AuthorityLandslideReport.objects.create(
#             AUTHORITY_ID=authority,
#             place=request.POST.get("place", f"{request.POST['latitude']},{request.POST['longitude']}"),
#             latitude=request.POST["latitude"],
#             longitude=request.POST["longitude"],
#             date=now.strftime("%Y-%m-%d"),
#             time=now.strftime("%H:%M:%S"),
#             status="pending"
#         )

#     return response

@csrf_exempt
def landslide_predict_view_authority(request):
    if not Authority.objects.filter(USER_ID=request.user).exists():
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    # Just run prediction, no auto-save
    return prediction.landslide_prediction(request)

@csrf_exempt
@login_required
def save_authority_report(request):
    print("SAVE AUTHORITY REPORT CALLED")
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    if not Authority.objects.filter(USER_ID=request.user).exists():
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    now = timezone.now()
    authority = Authority.objects.get(USER_ID=request.user)
    AuthorityLandslideReport.objects.create(
        AUTHORITY_ID=authority,
        place=request.POST.get("place", f"{request.POST['latitude']},{request.POST['longitude']}"),
        latitude=request.POST["latitude"],
        longitude=request.POST["longitude"],
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        status="pending"
    )
    return JsonResponse({"status": "success", "message": "Report saved."})




@login_required
def user_landslide_page(request):
    if not UserProfile.objects.filter(USER_ID=request.user).exists():
        return redirect("login")
    return render(request, "user_landslide_page.html")


# @csrf_exempt
# @login_required
# def landslide_predict_view(request):
#     if not UserProfile.objects.filter(USER_ID=request.user).exists():
#         return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

#     response = prediction.landslide_prediction(request)

#     data = json.loads(response.content)
#     if data.get("status") == "success" and data.get("prediction") == "Landslide Prone":
#         now = timezone.now()
#         userProfile = UserProfile.objects.get(USER_ID=request.user)
#         UserLandslideReport.objects.create(
#             userProfile_ID=userProfile,
#             place=request.POST.get("place", f"{request.POST['latitude']},{request.POST['longitude']}"),
#             latitude=request.POST["latitude"],
#             longitude=request.POST["longitude"],
#             date=now.strftime("%Y-%m-%d"),
#             time=now.strftime("%H:%M:%S"),
#             status="pending"
#         )

#     return response


@csrf_exempt
@login_required
def landslide_predict_view(request):
    if not UserProfile.objects.filter(USER_ID=request.user).exists():
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    # Just run prediction, no auto-save
    return prediction.landslide_prediction(request)


@csrf_exempt
@login_required
def save_user_report(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    if not UserProfile.objects.filter(USER_ID=request.user).exists():
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    now = timezone.now()
    userProfile = UserProfile.objects.get(USER_ID=request.user)
    UserLandslideReport.objects.create(
        userProfile_ID=userProfile,
        place=request.POST.get("place", f"{request.POST['latitude']},{request.POST['longitude']}"),
        latitude=request.POST["latitude"],
        longitude=request.POST["longitude"],
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        status="pending"
    )
    return JsonResponse({"status": "success", "message": "Report saved."})



def admin_delete_helpline(request, id):
    helpline = HelplineNumber.objects.get(id=id)
    helpline.delete()
    messages.success(request, 'Helpline number deleted successfully.')
    return redirect('manage_helpline')

