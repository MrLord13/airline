from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from appuser.models import AdminUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator

@login_required
def admins(request):
    if request.user.is_superuser:
        data = {}
        data['page_title'] = 'Admins'
        data['breadcrumbs'] = [{'text': 'Admins', 'url': '/dashboard/admins/'}]
        return render(request, 'panel/admins.html', data)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

@login_required
def admin_data(request):
    if request.user.is_superuser:
        admins = AdminUser.objects.all()
        paginator = Paginator(admins, 10)  # Show 10 admins per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        data = {
            "data": [
                {
                    'ID': admin.id,
                    'First Name': admin.first_name,
                    'Last Name': admin.last_name,
                    'Username': admin.username,
                    'Email': admin.email,
                    'Status': 'Active' if admin.is_active else 'Disabled'
                } for admin in page_obj
            ],
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "page": page_obj.number,
            "pages": paginator.num_pages
        }
        return JsonResponse(data, content_type='application/json', status=200)
    else:
        return HttpResponseForbidden("You don't have permission to access this data.")

@csrf_exempt
@login_required
def create_admin(request):
    if request.method == 'POST' and request.user.is_superuser:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if not username or not email:
            return JsonResponse({'message': 'Username and email are required.'}, status=400)

        if password != password_confirm:
            return JsonResponse({'message': 'Passwords do not match.'}, status=400)

        if AdminUser.objects.filter(username=username).exists() or AdminUser.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Username or email already exists.'}, status=400)

        admin = AdminUser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=make_password(password)
        )
        admin.save()
        return JsonResponse({'message': 'Admin created successfully.'}, status=201)
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@csrf_exempt
@login_required
def update_admin(request):
    if request.method == 'POST' and request.user.is_superuser:
        try:
            admin_id = request.POST.get('id')
            if not admin_id:
                return JsonResponse({'message': 'Admin ID is required.'}, status=400)

            try:
                admin = AdminUser.objects.get(id=admin_id)
            except AdminUser.DoesNotExist:
                return JsonResponse({'message': 'Admin not found.'}, status=404)

            new_username = request.POST.get('username')
            new_email = request.POST.get('email')

            # Check if username exists for other users
            if AdminUser.objects.exclude(id=admin_id).filter(username=new_username).exists():
                return JsonResponse({'message': 'Username already exists.'}, status=400)

            # Check if email exists for other users
            if AdminUser.objects.exclude(id=admin_id).filter(email=new_email).exists():
                return JsonResponse({'message': 'Email already exists.'}, status=400)

            admin.first_name = request.POST.get('first_name', admin.first_name)
            admin.last_name = request.POST.get('last_name', admin.last_name)
            admin.username = new_username
            admin.email = new_email

            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password:
                if password != password_confirm:
                    return JsonResponse({'message': 'Passwords do not match.'}, status=400)
                admin.password = make_password(password)

            admin.save()
            return JsonResponse({'message': 'Admin updated successfully.'}, status=200)
            
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}'}, status=500)
            
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@csrf_exempt
@login_required
def delete_admin(request):
    if request.method == 'POST' and request.user.is_superuser:  
        admin_id = request.POST.get('id') 
        admin = AdminUser.objects.get(id=admin_id) 
        try:
            admin = AdminUser.objects.get(id=admin_id)
            admin.delete()
            return JsonResponse({'message': 'Admin deleted successfully.'}, status=200)
        except AdminUser.DoesNotExist: 
            return JsonResponse({'message': 'Admin not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@login_required
def get_admin_details(request):
    if request.method == 'GET' and request.user.is_superuser:
        admin_id = request.GET.get('id')
        try:
            admin = AdminUser.objects.get(id=admin_id)
            data = {
                'ID': admin.id,
                'First Name': admin.first_name,
                'Last Name': admin.last_name,
                'Username': admin.username,
                'Email': admin.email,
                'Status': 'Active' if admin.is_active else 'Disabled'
            }
            return JsonResponse(data, status=200)
        except AdminUser.DoesNotExist:
            return JsonResponse({'message': 'Admin not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request.'}, status=400) 