from django.shortcuts import render, redirect, get_object_or_404;
from django.contrib.auth.decorators import login_required,user_passes_test;
from .models import Tickets,Comment,Category;
from .forms import CommentForm, TicketForm,CategoryForm;
from django.contrib.auth.models import User;
from django import forms;
from django.core.paginator import Paginator,PageNotAnInteger;
from django.contrib import messages;
from django.utils.text import slugify;
from user.auth import checkIfAdmin,checkIfTech,checkIfCustomer,checkIfAdminOrTech
from .Calculation import num_of_priority,num_of_category,num_of_general;
from .utils import render_to_pdf;
from django.http import HttpResponse;
import csv;
import datetime;

from django.http import HttpResponseForbidden
from .models import Tickets, Comment, Category
from .forms import CommentForm, TicketForm

from django.utils.timezone import localtime
from django.utils.formats import date_format
from django.core.mail import send_mail

from django.conf import settings
from Management.DAL.Entities import Users  

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tickets.models import Tickets


# @login_required
# def render_pdf(request):
# 	tickets,cat_none = tickets_filter(request);
# 	data = [];
# 	for ticket in tickets:
# 		obj = {	"user":ticket.user.username,
# 				"subject":ticket.subject,
# 				"department":ticket.name,
# 				"status":ticket.status,
# 				"priority":ticket.priority,
# 				"category":ticket.category,
# 				"date":ticket.created,
# 		}
# 		data.append(obj);

# 	tickets = {"tickets":data};

# 	pdf = render_to_pdf('tickets/tickets_pdf.html',tickets);
# 	return HttpResponse(pdf,content_type="application/pdf")

@login_required
def render_pdf(request):
	tickets, cat_none = tickets_filter(request)
	data = []
	for ticket in tickets:
		assigned_to = None
		if hasattr(ticket, 'taskassignment') and ticket.taskassignment:
			assigned_to = (
				ticket.taskassignment.assigned_to.get_full_name()
				or ticket.taskassignment.assigned_to.username
			)
		
		obj = {
			"user": ticket.user.username,
			"subject": ticket.subject,
			"department": ticket.name,
			"status": ticket.status,
			"priority": ticket.priority,
			"category": ticket.category,
			"date": ticket.created,
			"assigned_to": assigned_to,
		}
		data.append(obj)

	context = {"tickets": data}
	pdf = render_to_pdf('tickets/tickets_pdf.html', context)
	return HttpResponse(pdf, content_type="application/pdf")



# @login_required
# def render_pdf(request):
#     tickets, cat_none = tickets_filter(request)
#     data = []

#     for ticket in tickets:
#         # Default value
#         resolved_by = "Not Resolved Yet"

#         if ticket.status.lower() in ["resolved", "closed"]:
#             try:
#                 assigned_to = ticket.taskassignment.assigned_to
#                 resolved_by = assigned_to.get_full_name() or assigned_to.username
#             except:
#                 resolved_by = "Not Resolved Yet"

#         obj = {
#             "user": ticket.user.username,
#             "subject": ticket.subject,
#             "department": ticket.name,
#             "status": ticket.status,
#             "priority": ticket.priority,
#             "category": ticket.category.name if ticket.category else "None",
#             "date": ticket.created,
#             "resolved_by": resolved_by,
#         }
#         data.append(obj)

#     pdf = render_to_pdf('tickets/tickets_pdf.html', {"tickets": data})
#     return HttpResponse(pdf, content_type="application/pdf")


@login_required
def export_csv(request):
	response = HttpResponse(content_type='text/csv');
	response['Content-Disposition'] ='attachment; filename = ticket-list-for-'+ str(datetime.date.today())+'.csv';
	writer = csv.writer(response);
	writer.writerow(['User','Title','Department','Status','Priority','Category','Date']);
	tickets,cat_none=tickets_filter(request);
	for ticket in tickets:
		writer.writerow([
			ticket.user.username,
			ticket.subject,
			ticket.name,
			ticket.status,
			ticket.priority,
			ticket.category,
			ticket.created,
		])
	return response;


def ticket_detail_pdf(request,id):
	ticket = Tickets.objects.get(pk=id);
	ticket_obj = {
		"id":ticket.id,
		"user":ticket.user,
		"category":ticket.category,
		"name":ticket.name,
		"subject":ticket.subject,
		"description":ticket.description,
		"status":ticket.status,
		"priority":ticket.priority,
		"created":ticket.created,
		"updated":ticket.updated,
	}
	pdf = render_to_pdf('tickets/ticket_detail_pdf.html',ticket_obj)
	return HttpResponse(pdf,content_type='application/pdf');



@login_required
def dashboard(request):
	open=0;closed =0;pending = 0;
	categories = Category.objects.all();

	if request.user.is_superuser or request.user.is_staff:
		if request.user.is_staff and not request.user.is_superuser:
			if request.user.profile.category:
				tickets = Tickets.objects.filter(category = request.user.profile.category).order_by('-created');
			else:
				tickets =  Tickets.objects.all().order_by('-created');
		else:
			tickets = Tickets.objects.all().order_by('-created');
	else:
		tickets = Tickets.objects.filter(user=request.user).order_by('-created');
	
	for ticket in tickets:
		if ticket.status == 'Open':
			open = open + 1;
		elif ticket.status == 'Closed':
			closed = closed + 1;
		elif ticket.status == 'Pending':
			pending = pending +1;


	critical,urgent,normal,not_important = num_of_priority();

	cat_number = num_of_category();

	#paginator function
	paginator,page_obj,tickets,page = paginated(request,tickets,10);

	total_tickets,admin,technician,customer  = num_of_general();	
	print('tickets::',tickets)


	return render(request,'user/dashboard.html',{'tickets':tickets,
												 'open':open,
												 'closed':closed,
												 'pending':pending,
												 'page_obj':page_obj,
												 'dashboard':'active',
												 'critical':critical,
												 'urgent':urgent,
												 'normal':normal,
												 'not_important':not_important,
												 'categories':categories,
												 'cat_number':cat_number,
												 'total_tickets':total_tickets,
												 'admin':admin,
												 'technician':technician,
												 'customer':customer,
												 'tot_tech':admin+technician,
												 'paginator':paginator,
												 'page':int(page),
												});




# def ticket_detail(request, id):
#     # ✅ Allow access if user is logged in OR management user is in session
#     if not request.user.is_authenticated and not request.session.get('user_id'):
#         return redirect('login')

#     ticket = get_object_or_404(Tickets, pk=id)
#     categories = Category.objects.all()

#     pri_design = ''
#     priority = ''
#     if ticket.priority == 'critical':
#         pri_design = 'btn btn-danger rounded-pill'
#         priority = "Critical"
#     elif ticket.priority == 'urgent':
#         pri_design = 'btn btn-warning rounded-pill'
#         priority = 'Urgent'
#     elif ticket.priority == 'normal':
#         pri_design = 'btn btn-info rounded-pill'
#         priority = "Normal"
#     else:
#         pri_design = 'btn btn-success rounded-pill'
#         priority = "Not Important"

#     comments = Comment.objects.filter(ticket=ticket)

#     if request.method == 'POST':
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden("Users cannot comment or edit.")

#         comment_form = CommentForm(data=request.POST)
#         ticket_form = TicketForm(instance=ticket, data=request.POST, files=request.FILES)

#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.ticket = ticket
#             new_comment.user = request.user
#             new_comment.save()
#             comment_form = CommentForm()

#         if ticket_form.is_valid():
#             # 🔒 Prevent ticket editing if it's closed by the user who created it
#             if ticket.status == 'Closed' and request.user == ticket.user:
#                 messages.error(request, "You cannot edit a closed ticket.")
#             else:
#                 ticket_form.save()
#                 messages.success(request, "Ticket updated successfully.")


# 				supervisor = User.objects.filter(is_superuser=True).first()
#                 if supervisor and supervisor.email:
#                     edited_time = date_format(localtime(ticket.updated), "l, F j, Y \\a\\t h:i A")
#                     ticket_link = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")

#                     subject = f"[TICKET UPDATED] #{ticket.id} - {ticket.subject}"
#                     message = f"""
# Hi {supervisor.get_full_name() or supervisor.username},

# Ticket #{ticket.id} has been updated by {request.user.get_full_name() or request.user.username} ({request.user.email}) on {edited_time}.

# ━━━━━━━━━━━━━━━━━━━━━━
# Subject: {ticket.subject}
# Priority: {ticket.priority.title()}
# Category: {ticket.category.name if ticket.category else 'None'}
# ━━━━━━━━━━━━━━━━━━━━━━

# You can view the updated ticket here:
# {ticket_link}

# Best regards,  
# HelpDesk System
# """
#             try:
#                 send_mail(
#                     subject=subject,
#                     message=message,
#                     from_email=None,
#                     recipient_list=[supervisor.email],
#                     fail_silently=False
#                 )
#             except Exception as e:
#                 print("❌ Error sending edit email:", e)




#     else:
#         comment_form = CommentForm()
#         ticket_form = TicketForm(instance=ticket)

#     return render(request, 'tickets/ticket_detail.html', {
#         'ticket': ticket,
#         'comment_form': comment_form,
#         'comments': comments,
#         'pri_design': pri_design,
#         'priority': priority,
#         'nav_ticket': 'active',
#         'categories': categories,
#         'ticket_form': ticket_form
#     })


# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponseForbidden
# from django.contrib import messages
# from .models import Tickets, Comment, Category
# from .forms import CommentForm, TicketForm
# from django.core.mail import send_mail
# from django.utils.timezone import localtime
# from django.utils.formats import date_format
# from django.contrib.auth.models import User

# def ticket_detail(request, id):
#     if not request.user.is_authenticated and not request.session.get('user_id'):
#         return redirect('login')

#     ticket = get_object_or_404(Tickets, pk=id)
#     categories = Category.objects.all()

#     pri_design = ''
#     priority = ''
#     if ticket.priority == 'critical':
#         pri_design = 'btn btn-danger rounded-pill'
#         priority = "Critical"
#     elif ticket.priority == 'urgent':
#         pri_design = 'btn btn-warning rounded-pill'
#         priority = 'Urgent'
#     elif ticket.priority == 'normal':
#         pri_design = 'btn btn-info rounded-pill'
#         priority = "Normal"
#     else:
#         pri_design = 'btn btn-success rounded-pill'
#         priority = "Not Important"

#     comments = Comment.objects.filter(ticket=ticket)

#     if request.method == 'POST':
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden("Users cannot comment or edit.")

#         comment_form = CommentForm(data=request.POST)
#         ticket_form = TicketForm(instance=ticket, data=request.POST, files=request.FILES)

#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.ticket = ticket
#             new_comment.user = request.user
#             new_comment.save()
#             comment_form = CommentForm()

#         if ticket_form.is_valid():
#             if ticket.status == 'Closed' and request.user == ticket.user:
#                 messages.error(request, "You cannot edit a closed ticket.")
#             else:
#                 updated_ticket = ticket_form.save()
#                 messages.success(request, "Ticket updated successfully.")

#                 # supervisor = User.objects.filter(is_superuser=True).first()
# 				management_emails = list(Users.objects.values_list('UserName', flat=True))

#                 if management_emails:
#                     edited_time = date_format(localtime(updated_ticket.updated), "l, F j, Y \\a\\t h:i A")
#                     ticket_link = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")

#                     subject = f"[TICKET UPDATED] #{ticket.id} - {ticket.subject}"
#                     message = f"""
# Hi Management Team,

# Ticket #{ticket.id} has been updated by {request.user.get_full_name() or request.user.username} ({request.user.email}) on {edited_time}.

# ━━━━━━━━━━━━━━━━━━━━━━
# Subject: {ticket.subject}
# Priority: {ticket.priority.title()}
# Category: {ticket.category.name if ticket.category else 'None'}
# ━━━━━━━━━━━━━━━━━━━━━━

# You can view the updated ticket here:
# {ticket_link}

# Best regards,  
# HelpDesk System
# """
#                     try:
#                         send_mail(
#                             subject=subject,
#                             message=message,
#                             from_email=settings.DEFAULT_FROM_EMAIL, 
#                             recipient_list=management_emails,
#                             fail_silently=False
#                         )
#                     except Exception as e:
#                         print("❌ Error sending edit email:", e)
#     else:
#         comment_form = CommentForm()
#         ticket_form = TicketForm(instance=ticket)

#     return render(request, 'tickets/ticket_detail.html', {
#         'ticket': ticket,
#         'comment_form': comment_form,
#         'comments': comments,
#         'pri_design': pri_design,
#         'priority': priority,
#         'nav_ticket': 'active',
#         'categories': categories,
#         'ticket_form': ticket_form
#     })



def ticket_detail(request, id):
    if not request.user.is_authenticated and not request.session.get('user_id'):
        return redirect('login')

    ticket = get_object_or_404(Tickets, pk=id)
    categories = Category.objects.all()

    # Priority design and label
    pri_design = ''
    priority = ''
    if ticket.priority == 'critical':
        pri_design = 'btn btn-danger rounded-pill'
        priority = "Critical"
    elif ticket.priority == 'urgent':
        pri_design = 'btn btn-warning rounded-pill'
        priority = 'Urgent'
    elif ticket.priority == 'normal':
        pri_design = 'btn btn-info rounded-pill'
        priority = "Normal"
    else:
        pri_design = 'btn btn-success rounded-pill'
        priority = "Not Important"
    is_technician = request.user.groups.filter(name__iexact='technician').exists()

    comments = Comment.objects.filter(ticket=ticket)
	

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Users cannot comment or edit.")

        comment_form = CommentForm(data=request.POST)
        ticket_form = TicketForm(instance=ticket, data=request.POST, files=request.FILES)

        # Save comment
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.ticket = ticket
            new_comment.user = request.user
            new_comment.save()
            comment_form = CommentForm()

        # Save ticket update
        if ticket_form.is_valid():
            if ticket.status == 'Closed' and request.user == ticket.user:
                messages.error(request, "You cannot edit a closed ticket.")
            else:
                ticket_form.save()
                messages.success(request, "Ticket updated successfully.")

                # Send email to management
                management_emails = list(Users.objects.values_list('UserName', flat=True))
			
                if management_emails:
                    edited_time = date_format(localtime(ticket.updated), "l, F j, Y \\a\\t h:i A")
                    ticket_link = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")

                    subject = f"[TICKET UPDATED] #{ticket.id} - {ticket.subject}"
                    message = f"""
Hi Management Team,

Ticket #{ticket.id} has been updated by {request.user.get_full_name() or request.user.username} ({request.user.email}) on {edited_time}.

━━━━━━━━━━━━━━━━━━━━━━
Subject: {ticket.subject}
Priority: {ticket.priority.title()}
Category: {ticket.category.name if ticket.category else 'None'}
━━━━━━━━━━━━━━━━━━━━━━

You can view the updated ticket here:
{ticket_link}

Best regards,  
HelpDesk System
"""
                    try:
						
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=management_emails,
                            fail_silently=False
                        )
                    except Exception as e:
                        print("❌ Error sending edit email:", e)

    else:
        comment_form = CommentForm()
        ticket_form = TicketForm(instance=ticket)

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comment_form': comment_form,
        'comments': comments,
        'pri_design': pri_design,
        'priority': priority,
        'nav_ticket': 'active',
        'categories': categories,
        'ticket_form': ticket_form,
		'is_technician': is_technician  
    })



@user_passes_test(checkIfAdminOrTech,login_url='error')
@login_required
def change_status(request,id,status):
	ticket = Tickets.objects.get(pk = id);
	if status == 'open':
		ticket.status = 'Open';
	elif status == 'pending':
		ticket.status = 'Pending';
	else:
		ticket.status = 'Closed';

	# pending # must be key (Pending)
	ticket.save();
	messages.success(request,"Status have been change successfully");
	return redirect('ticket-detail',id=id);


@user_passes_test(checkIfAdminOrTech,login_url='error')
@login_required
def change_status(request,id,status):
	ticket = Tickets.objects.get(pk = id);
	if status == 'open':
		ticket.status = 'Open';
	elif status == 'pending':
		ticket.status = 'Pending';
	else:
		ticket.status = 'Closed';

	# pending # must be key (Pending)
	ticket.save();
	messages.success(request,"Status have been change successfully");
	return redirect('ticket-detail',id=id);

@user_passes_test(checkIfAdmin,login_url='error')
@login_required
def change_category(request,id,category):
	ticket = Tickets.objects.get(pk = id);
	cat = Category.objects.get(slug = category);
	ticket.category = cat;
	ticket.save();
	messages.success(request,"Category have been Assigned successfully");
	return redirect('ticket-detail',id = id);




@user_passes_test(checkIfCustomer, login_url='error')
@login_required
def create_ticket(request):
    if request.method == 'POST':
        new_form = TicketForm(data=request.POST, files=request.FILES)
        if new_form.is_valid():
            new_ticket = new_form.save(commit=False)
            new_ticket.user = request.user
            new_ticket.save()

            # supervisor = User.objects.filter(is_superuser=True).first()
            management_emails = list(Users.objects.values_list('UserName', flat=True))
            # print("Supervisor:", supervisor)
            # print("Supervisor Email:", supervisor.email if supervisor else None)

            if  management_emails:
                formatted_time = date_format(localtime(new_ticket.created), "l, F j, Y \\a\\t h:i A")  # Example: Wednesday, June 25, 2025 at 04:10 PM
                ticket_link = request.build_absolute_uri(f"/Management/tickets/{new_ticket.id}/")

                subject = f"[NEW TICKET] #{new_ticket.id} - {new_ticket.subject}"
                message = f"""
Hi Management Team,

A new support ticket has been raised by {request.user.get_full_name() or request.user.username} ({request.user.email}) on {formatted_time}.

━━━━━━━━━━━━━━━━━━━━━━
Subject: {new_ticket.subject}
Description:
{new_ticket.description}
━━━━━━━━━━━━━━━━━━━━━━

You can view and manage the ticket using the link below:
{ticket_link}

Thank you for your attention.

Best regards,  
HelpDesk System
"""

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list= management_emails,
                        fail_silently=False
                    )
                    print("Email sent successfully")
                except Exception as e:
                    print("Error sending email:", e)

            messages.success(request, 'Successfully created ticket')
            return redirect('dashboard')
    else:
        new_form = TicketForm()

    return render(request, 'tickets/create_ticket.html', {
        'new_form': new_form,
        'new_ticket': 'active',
    })



@login_required
def status_view(request,status):
	if status == 'recent':
		return redirect('dashboard');

	tickets = Tickets.objects.filter(status = status.capitalize()).order_by('-created');

	if not request.user.is_superuser and not request.user.is_staff:
		tickets = tickets.filter(user= request.user).order_by('-created');

	number = 0;
	# Key <Open, Closed , Pending>
	for _ in tickets:
		number = number+1; #tickets.count

	paginator,page_obj,tickets,page = paginated(request,tickets,3);

	return render(request,'tickets/status_view.html',{'tickets':tickets,
													  'status':status,
													  'number':number,
													  'page_obj':page_obj,
													  'dashboard':'active',
													  'paginator':paginator,
													  'page':int(page),
														});
#category
@user_passes_test(checkIfAdminOrTech,login_url='error')
@login_required
def new_category(request):
	if request.method == 'POST' and request.user.is_superuser:
		category_form = CategoryForm(data=request.POST);
		if category_form.is_valid():
			new_category = category_form.save(commit=False);
			new_category.slug = slugify(new_category.name);
			new_category.save();
			messages.success(request,"Category added successfully");
			category_form = CategoryForm();
		else:
			messages.error(request,"Cannot add category, try again!");
	else:
		category_form= CategoryForm();

	categories = Category.objects.all();

	return render(request,'tickets/new_category.html',{ 'category':'active',
														'category_form':category_form,
														'categories':categories,
														});

@user_passes_test(checkIfAdmin,login_url='error')
def delete_category(request,cat):
	category = Category.objects.get(slug=cat);
	category.delete();
	messages.success(request,"successfully delete category!")
	return redirect('new-category');


@user_passes_test(checkIfAdmin,login_url='error')
def edit_category(request,cat):
	category = Category.objects.get(slug=cat);
	name = request.GET.get('name');
	category.name = name;
	category.slug = slugify(name);
	category.save();
	messages.success(request,"Successfully edit Category");
	return redirect('new-category');



find = {
	'status':'all',
	'priority':'all',
	'category':'all',
	'cat_none':False,
	'sort':'none',
	'order':'descending',
}

date = {
	'start-date':None,
	'end-date':None,
}


def tickets_filter(request):
	status = request.GET.get('status'); #all
	priority = request.GET.get('priority'); # none
	category = request.GET.get('category'); # all,.......
	sort = request.GET.get('sort');
	order = request.GET.get('order');

	start_date = request.GET.get('start-date'); # date, null
	end_date = request.GET.get('end-date');
	# date >> dirct
	# null >> 
	if start_date and end_date:
		date['start-date'] = start_date;
		date['end-date'] = end_date;
	elif start_date:
		date['start-date'] = start_date;
		date['end-date'] = datetime.date.today();

	# SORTING # sort not by user id
	if sort:
		find['sort'] = sort;
	if order:
		find['order'] = order;
	if find['order'] == 'ascending':
		if find['sort'] == 'date':
			tickets =Tickets.objects.all().order_by('created');
		elif find['sort'] == 'user':
			tickets = Tickets.objects.all().order_by('user__username');
		elif find['sort'] == 'department':
			tickets = Tickets.objects.all().order_by('name');
		else:
			tickets = Tickets.objects.all();
	elif find['order'] == 'descending':
		if find['sort'] == 'date':
			tickets =Tickets.objects.all().order_by('-created');
		elif find['sort'] == 'user':
			tickets = Tickets.objects.all().order_by('-user__username');
		elif find['sort'] == 'department':
			tickets = Tickets.objects.all().order_by('-name');

		else:
			tickets = Tickets.objects.all();

	#SEARCHING
	search_txt = request.GET.get('search');
	#print("SEARCH_TXT",search_txt)
	if search_txt:
		tickets = tickets & Tickets.objects.filter(subject__icontains = search_txt);

	# STATUS FILTER
	if (status and status != 'all') or (find['status'] != 'all' and status != 'all'):
		if status:
			find['status'] = status;
		tickets = tickets & Tickets.objects.filter(status=find['status'].capitalize());#status=all
	else:
		find['status'] = 'all';


	# PRIORITY FILTER
	if (priority and priority != 'all') or (find['priority'] != 'all' and priority != 'all'):
		if priority:
			find['priority'] = priority;
		tickets = tickets & Tickets.objects.filter(priority=find['priority']);
	else:
		find['priority'] = 'all';

	# CATEGORY FILTER
	if (category and category != 'all' and category != 'none') or (find['category'] != 'all' and category != 'all' and category != 'none'):
		if category:
			find['category'] = category;

		cat = Category.objects.get(slug = find['category']); #####Not None
		tickets = tickets & Tickets.objects.filter(category = cat);
	else:
		find['category'] = 'all';


	# FILTER FOR CATEGORY NONE

	# category != Null && category != none
	# must reset mem when category == all, other cat.....
	if (category and category != 'none'):
		find['cat_none'] = False;


	# exclude all category # exclude(category = 'computer-error');
	cat_none  = False;
	if (category == 'none' or find['cat_none'] == True):
		if category == 'none':
			find['cat_none'] = True; # Must be false if 

		categories = Category.objects.all();
		for cat in categories:
			tickets = tickets & Tickets.objects.exclude(category = cat);
		cat_none = True;


	if date['start-date'] and date['end-date']:
		tickets = tickets & Tickets.objects.filter(created__range = [date['start-date'],date['end-date']])


	return tickets,cat_none;


#tickets
@login_required
def tickets(request):
	categories = Category.objects.all();
	tickets,cat_none = tickets_filter(request);
	clear = False;

	if date['start-date'] and date['end-date']:
		clear = True;
	else:
		clear = False;



	paginator,page_obj,tickets,page = paginated(request,tickets,5);

	return render(request,'tickets/tickets.html',{'nav_ticket':'active',
												  'categories':categories,
												  'tickets':tickets,
												  'find':find,
												  'cat_none':cat_none,
												  'page_obj':page_obj,
												  'paginator':paginator,
												  'page':int(page),
												  'clear':clear,
													});


def clear_date(request):
	date['start-date'] = None;
	date['end-date'] = None;
	return redirect('tickets');

def paginated(request,objects,number):
	paginator = Paginator(objects,number);
	try:
		page = request.GET.get('page'); # page no variable 
		page_obj =paginator.get_page(page);
		objects = paginator.page(page);
	except PageNotAnInteger:
		page = 1;
		page_obj = paginator.get_page(1);
		objects = paginator.page(1);

	return paginator,page_obj,objects,page;

# @login_required
# def close_ticket(request, ticket_id):
#     if request.method == 'POST':
#         ticket = get_object_or_404(Tickets, id=ticket_id, user=request.user)
#         if ticket.status != 'Closed':
#             ticket.status = 'Closed'
#             ticket.save()
#             messages.success(request, f'Ticket #{ticket.id} has been closed successfully.')
#         else:
#             messages.info(request, f'Ticket #{ticket.id} is already closed.')
#     return redirect(request.META.get('HTTP_REFERER', '/'))





@login_required
def close_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Tickets, id=ticket_id, user=request.user)

        if ticket.status != 'Closed':
            ticket.status = 'Closed'
            ticket.save()

            management_emails = list(Users.objects.values_list('UserName', flat=True))

            if management_emails:
                closed_time = date_format(localtime(ticket.updated), "l, F j, Y \\a\\t h:i A")
                ticket_link = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")

                subject = f"[TICKET CLOSED] #{ticket.id} - {ticket.subject}"
                message = f"""
Hi Anisha Goyal,

The following ticket has been closed by the user who created it ({request.user.get_full_name() or request.user.username} - {request.user.email}) on {closed_time}:

━━━━━━━━━━━━━━━━━━━━━━
Subject: {ticket.subject}
Priority: {ticket.priority.title()}
Category: {ticket.category.name if ticket.category else 'None'}
━━━━━━━━━━━━━━━━━━━━━━

You can review the closed ticket here:
{ticket_link}

Best regards,  
HelpDesk System
"""

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL, 
                        recipient_list=management_emails,
                        fail_silently=False
                    )
                except Exception as e:
                    print("❌ Error sending close ticket email:", e)

            messages.success(request, f'Ticket #{ticket.id} has been closed successfully.')
        else:
            messages.info(request, f'Ticket #{ticket.id} is already closed.')

    return redirect(request.META.get('HTTP_REFERER', '/'))
