from django.shortcuts import render,redirect
from . forms import UserRegistrationForm,ProfileForm,UserForm,CustomerRegistrationForm,CustomerProfile,LoginForm ,ProfileEditForm    ;
from django.contrib.auth.decorators import login_required,user_passes_test;
from django.contrib import messages;
from django.contrib.auth.models import User;
from tickets.views import paginated;
from .auth import checkIfAdmin,checkIfTech,checkIfCustomer
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
# from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from Management.DAL.Entities import Users
from tickets.models import Tickets

from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils.timezone import localtime

# from .forms import LoginForm


# from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from django.core.mail import send_mail
# from django.conf import settings
# from django.shortcuts import get_object_or_404, redirect
# from Management.DAL.Entities import Users  
# from tickets.models import Tickets
# from django.contrib.auth.decorators import login_required



@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def register(request):
	if request.method == 'POST':
		user_form = UserRegistrationForm(data=request.POST);
		user_profile = ProfileForm(data=request.POST, files=request.FILES);

		if user_form.is_valid() and user_profile.is_valid():
			new_user = user_form.save(commit=False);
			new_user.set_password(user_form.cleaned_data['password1']);
			new_user.is_staff = True;
			new_user.save();

			new_profile = user_profile.save(commit=False);
			new_profile.user = new_user;

			if new_profile.gender == 'female':
				new_profile.photo = 'default_female.jpg';
			new_profile.save();

			messages.success(request,"Technican created successfully");
			return redirect('dashboard');
	else:
		user_form = UserRegistrationForm();
		user_profile = ProfileForm();
	return render(request,'user/register.html',{'user_form':user_form,
												'user_profile':user_profile,
												'tech':'active',
		});



@login_required
def edit(request):
	if request.method == "POST":
		user_form = UserForm(instance= request.user,data=request.POST);
		profile_form = ProfileEditForm(instance=request.user.profile,data=request.POST,files=request.FILES);
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save();
			profile_form.save();
			messages.success(request,"Your Profile have been change successfully");
		else:
			messages.error(request,"Your Profile have not been change successfully. Try Again");
	else:
		user_form = UserForm(instance = request.user);
		profile_form = ProfileEditForm(instance= request.user.profile);
	return render(request,"user/edit.html",{"profile_form":profile_form,
											"user_form":user_form,
		})


@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def tech_view(request):
	users = User.objects.filter(is_staff = True);
	admin = 0;techs = 0;

	for user in users:
		if user.is_superuser:
			admin = admin+1;
		else:
			techs = techs+1;

	#pagination
	paginator,page_obj,users,page = paginated(request,users,3);

	return render(request,'user/tech_view.html',{'tech':'active',
												 'users':users,
												 'admin':admin,
												 'techs':techs,
												 'page_obj':page_obj,
												 'paginator':paginator,
												 'page':int(page)
													});

@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def role_view(request,role):
	if role == 'admin':
		users = User.objects.filter(is_superuser = True);
	else:
		users = User.objects.filter(is_staff = True,is_superuser=False);
	return render(request,'user/role_view.html',{'users':users,
												 'tech':'active',
												});


@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def user_detail_view(request,id):
	d_user = User.objects.get(pk=id);
	tech = '';
	customer = '';
	if d_user.is_superuser or d_user.is_staff:
		tech = 'active';
	else:
		customer='active';


	if request.method == "POST":
		user_form = UserForm(instance=d_user,data=request.POST);
		profile_form = ProfileForm(instance=d_user.profile,data=request.POST,files=request.FILES);
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save();
			profile_form.save();
			messages.success(request,"User data have been changed successfully");
		else:
			messages.error(request,"Cannot changed used data, try again!");
	else:
		user_form = UserForm(instance=d_user);
		profile_form = ProfileForm(instance=d_user.profile);

	return render(request,'user/user_detail_view.html',{'tech':tech,
														'customer':customer,
														'd_user':d_user,
														'user_form':user_form,
														'profile_form':profile_form,
														});

@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def customer_view(request):
	users = User.objects.filter(is_superuser=False,is_staff=False);
	paginator,page_obj,users,page = paginated(request,users,3);
	return render(request,'user/customer_view.html',{ 'customer':'active',
													  'users':users,
													  'paginator':paginator,
													  'page_obj':page_obj,
													  'page':int(page),
														});

@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def new_customer(request):
	if request.method == 'POST':
		customer_form = CustomerRegistrationForm(data=request.POST);
		profile_form = CustomerProfile(data=request.POST,files = request.FILES);
		if customer_form.is_valid() and profile_form.is_valid():
			new_customer = customer_form.save(commit = False);
			new_profile = profile_form.save(commit=False);
			new_customer.set_password(customer_form.cleaned_data['password1']);
			new_profile.user = new_customer;

			if new_profile.gender == 'female':
				new_profile.photo = 'default_female.jpg';

			new_customer.save();
			new_profile.save();
			messages.success(request,"Technican created successfully");
			return redirect('dashboard');
	else:
		customer_form = CustomerRegistrationForm();
		profile_form = CustomerProfile();

	return render(request,'user/new_customer.html',{ 'customer':'active',
													 'profile_form':profile_form,
													 'customer_form':customer_form,
														});


@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def user_delete(request,id):
	user = User.objects.get(pk=id);

	role = user.is_staff; # true / false

	user.delete();
	messages.success(request,"User delete successful!");

	if role:
		return redirect('tech-view');
	else:
		return redirect('customer-view');

def error(request):
	return render(request,'user/error.html');


def contactus(request):
	technicians = User.objects.filter(is_superuser=False,is_staff=True);
	return render(request,'user/contact_us.html',{'contact_us':'active',
												  'technicians':technicians,
		});

@csrf_protect
@require_POST
def custom_logout(request):
    logout(request)
    # return redirect('login')
    return redirect(reverse('user-login'))






from django.contrib.auth.decorators import login_required
from Management.presentation.ViewModels.assigntasks import TaskAssignment 

@login_required
def technic_dashboard(request):
    if not request.user.is_staff:
        return redirect('error')  # Optional: restrict to technicians only

    # Get assigned tickets
    assigned_tasks = TaskAssignment.objects.filter(assigned_to=request.user).select_related('ticket').order_by('-ticket__created')  

    return render(request, 'tickets/technic_dashboard.html',{
        'assigned_tasks': assigned_tasks,
        'dashboard': 'active',
    })



# # Technician-side revert
@login_required
@csrf_exempt

@csrf_exempt
def revert_ticket_from_technician(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if reason:
            # ✅ FIX: update the status back to 'Pending' or 'Open'
            ticket.status = 'Pending'
            ticket.save()
            ticket_url = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")
            management_emails = list(Users.objects.values_list('UserName', flat=True))
            message = (
                f"{request.user.username} has reverted ticket #{ticket.id}.\n\n"
                f"Subject: {ticket.subject}\n\n"
                f"Reason:\n{reason}\n\n"
                f"Link: {ticket_url}"
            )

            try:
                send_mail(
                    subject=f"Ticket #{ticket.id} Reverted by {request.user.username} ",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=management_emails,
                    fail_silently=False
                )
                messages.success(request, f"Ticket #{ticket.id} reverted and email sent to management.")
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        else:
            messages.error(request, "Please enter a reason to revert.")

    return redirect('technic-dashboard')

# def revert_ticket_from_technician(request, ticket_id):
#     ticket = get_object_or_404(Tickets, id=ticket_id)

#     if request.method == 'POST':
#         reason = request.POST.get('reason', '').strip()
#         if reason:
#             management_emails = list(Users.objects.values_list('UserName', flat=True))
#             message = (
#                 f"{request.user.username} has reverted ticket #{ticket.id}.\n\n"
#                 f"Subject: {ticket.subject}\n\n"
#                 f"Reason:\n{reason}\n\n"
#                 f"Link: http://127.0.0.1:8000/Management/tickets/{ticket.id}/"
#             )

#             try:
#                 send_mail(
#                     subject=f"Ticket #{ticket.id} Reverted by {request.user.username} ",
#                     message=message,
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=management_emails,
#                     fail_silently=False
#                 )
#                 messages.success(request, f"Ticket #{ticket.id} reverted and email sent to management.")
#             except Exception as e:
#                 messages.error(request, f"Failed to send email: {str(e)}")
#         else:
#             messages.error(request, "Please enter a reason to revert.")
#     return redirect('technic-dashboard')



@login_required
@csrf_exempt
def resolve_ticket(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
 
    if request.method == 'POST' and ticket.status != 'Closed':
        ticket.status = 'Resolved'  
        # resolved_time = localtime(ticket.resolved_at).strftime('%Y-%m-%d %H:%M')
        ticket.save()

        management_emails = list(Users.objects.values_list('UserName', flat=True))

        ticket_url = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")
        login_url = request.build_absolute_uri(f"/Management/user/login/")
		


        try:
            send_mail(
                subject=f"Ticket #{ticket.id} Marked as Resolved",
                message=(
                    f"{request.user.username} has marked ticket #{ticket.id} as resolved.\n\n"
                    f"Subject: {ticket.subject}\n"
                    f"Description: {ticket.description}\n"
					# f"Resolved At: {resolved_time}\n"

                    # f"Resolved At: {ticket.resolved_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"You can check using the system:"
				    f"Link: {ticket_url}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=management_emails,
                fail_silently=False
            )
        except Exception as e:
            messages.error(request, f"Failed to send email to management: {str(e)}")

        # Send mail to ticket creator
        if ticket.user and ticket.user.email:
            try:
                send_mail(
                    subject=f"Your Ticket #{ticket.id} has been Resolved",
                    message=(
                        f"Hi {ticket.user.username},\n\n"
                        f"Your support ticket has been marked as resolved by {request.user.username}.\n"
                        f"You may review the resolution and close the ticket if you're satisfied.\n\n"
                        f"Subject: {ticket.subject}\n"
                        # f"Resolved At: {ticket.resolved_at.strftime('%Y-%m-%d %H:%M')}\n"
						f"Kindly check it using the system:"
                        f"Link to Ticket: {login_url}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.user.email],
                    fail_silently=False
                )
            except Exception as e:
                messages.error(request, f"Failed to notify user: {str(e)}")

        messages.success(request, f"Ticket #{ticket.id} marked as resolved. Emails sent.")
    else:
        messages.warning(request, "Invalid request or ticket already closed.")

    return redirect('technic-dashboard')



class CustomLoginView(LoginView):
    authentication_form = LoginForm
    
    def get_success_url(self):
        user = self.request.user
        print("LOGGED IN USER:", user.username)
        print("GROUPS:", list(user.groups.values_list("name", flat=True)))

        if user.is_staff and user.groups.filter(name__iexact='technician').exists():
            print("🔁 Redirecting to technician-dashboard")
            return reverse('technic-dashboard')
        print("➡ Redirecting to dashboard")
        return reverse('dashboard')

