from django.shortcuts import render,redirect,HttpResponse
from Management.presentation.ViewModels.TaskInformationviewmodel import TaskForm
from Management.presentation.ViewModels.registrationviewmodel import RegisterForm
from Management.presentation.ViewModels.loginviewmodel import LoginForm
from Management.presentation.ViewModels.assignedviewmodel import assignedviewmodel
from Management.presentation.ViewModels.CommentViewModel import CommentViewModel
from Management.presentation.ViewModels.TaskViewModel import TaskViewModel
from Management.presentation.ViewModels.Updateviewmodel import UpdateTaskForm,UpdateStatusForm
from Management.presentation.ViewModels.addcommentsviewmodel import CommentsForm
from Management.presentation.ViewModels.assignedtasksviewmodel import assignedForm
from Management.Services.ServiceModels.UsersServices import UsersServices
from Management.Services.ServiceModels.TaskInformationServices import TaskInformationServices
from Management.Services.ServiceModels.TaskDataServices import TaskDataServices
from ..Services.Services import *
from django.core.exceptions import ValidationError


from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Management.presentation.ViewModels.assigntasks import TaskAssignment
from tickets.models import Tickets
from django.contrib.auth.models import User
from Management.presentation.ViewModels.assignforms import TaskAssignForm
from Management.DAL.Entities import Users  
from django.conf import settings


def landing_page(request):
    return render(request, 'landing.html')

def dashboard(request):
    return render(request, 'Homepage.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned_data=form.cleaned_data
            user=UsersServices(
                UserID=None,
                firstname=cleaned_data['firstname'],
                lastname=cleaned_data['lastname'],
                UserName=cleaned_data['UserName'],
                Password=cleaned_data['Password'],  
            )
            

            InsertUser(user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['UserName']
            password = form.cleaned_data['Password']
        
            user = Users.objects.filter(UserName=username,Password=password).first()
            if user:
                user_id = user.UserID
                request.session['user_id'] = user_id
                return redirect('TaskManagement')  
            else:
                error_message = 'Invalid username or password.'
                return render(request, 'Homepage.html', {'error_message': error_message})
        
    else:
        form = LoginForm()  
    return render(request, 'Homepage.html', {'form': form})



def Home(request):
    
   tickets = Tickets.objects.select_related('user', 'category', 'taskassignment').order_by('-created')  
   users = User.objects.filter(is_staff=True, is_superuser=False, is_active=True)

   return render(request, 'TaskManagement.html', {
        'tickets': tickets,  # not assignments
        'users': users
    })
    


def addTask(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            priority_obj = viewID(cleaned_data['PriorityID'], 'Priority')

            if priority_obj is None:
                return HttpResponse("Error: Priority does not exist", status=400)

            task = TaskInformationServices(
                TaskID=None,
                Title=cleaned_data['Title'],
                Description=cleaned_data['Description'],
                DueDate=cleaned_data['DueDate'],
                Assignedby=request.user,  # Ensure Assignedby is set correctly
                Status=cleaned_data['Status'],
                Priority=priority_obj,
            )

            InsertTask(task)
            return redirect('task_list')  # Adjust as needed

    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form})

def updateTask(request,pk):
    data=viewID(pk,"TaskInformation")
    userid=request.session.get('user_id')
    user=viewID(userid,'Users')
    if request.method == 'POST':
        taskform=UpdateTaskForm(request.POST)
        statusform=UpdateStatusForm(request.POST)
        if  taskform.is_valid() and statusform.is_valid():
            task=taskform.cleaned_data
            data=statusform.cleaned_data
            priority= viewID(data['Priority'],'Priority')
            status= viewID(data['Status'],'Status')
            updatedtask=TaskInformationServices(
                TaskID=None,
                Title=task['Title'],
                Description=task['Description'],
                StartDate=None,
                DueDate=data['DueDate'],
                Assignedby=user, 
                Status=status,
                Priority=priority,
            )
            TaskUpdate(updatedtask,pk)
            return redirect('TaskManagement')
    else:
        taskform=UpdateTaskForm()
        statusform=UpdateStatusForm()
    return render(request, 'update.html', {'task': taskform,'status':statusform,'data':data})



def UpdateStatus(request, pk):
    if request.method == 'POST':
        form =UpdateStatusForm(request.POST)
        
        if form.is_valid():
            form=form.cleaned_data
            status= viewID(form['Status'],'Status')
            priority= viewID(form['Priority'],'Priority')
            task = TaskDataServices(
                AssignedID=None,
                TaskID=None,
                AssignedTo=None,
                PriorityID=priority,
                Status=status,
                DueDate=form['DueDate'],
            )
            Statusupdate(task,pk)
            return redirect('TaskManagement')
        
    else:
        form =UpdateStatusForm()
    return render(request, 'UpdateStatus.html', {'form': form})


def assign(request, pk):
    task = viewID(pk,'TaskInformation')
    if request.method == 'POST':
        form = assignedForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # print(cleaned_data)
            assigned_users = form.cleaned_data['AssignedTo']
            priority= viewID(cleaned_data['PriorityID'],'Priority')
            status= viewID(cleaned_data['Status'],'Status')
            # print(assigned_users,priority,status)
            for user_id in assigned_users:
                user=viewID(user_id,'Users')
                
                try:
                    assigned_task = TaskDataServices(
                        AssignedID=None,
                        TaskID=task,
                        AssignedTo=None,
                        PriorityID=priority,
                        Status=status,
                        DueDate=cleaned_data['DueDate']
                    )
                    assignTask(assigned_task,user)
                except ValidationError as e:
                    form.add_error('AssignedTo', e)

            return redirect('TaskManagement')
    else:
        form = assignedForm()

    return render(request, 'Assign.html', {'form': form})

# def Tasks(request):
#     user_id = request.session.get('user_id')
#     user=viewID(user_id,'Users')
#     data=TaskData.objects.select_related('TaskID')
#     for i in data:
#         print(i.AssignedTo.firstname)
#     assignedlist=TaskDataDetails()
#     print(assignedlist[2].AssignedTo)
#     return render(request, 'mytasks.html',{'form':assignedlist})



def Tasks(request):
    user_id = request.session.get('user_id')
    
    assignedlist=TaskDataDetails(user_id)
    Task_view=[]
    for task in assignedlist:
        task_vm = assignedviewmodel(
            AssignedID=task.AssignedID,
            TaskID=task.TaskID,  
            AssignedTo=task.AssignedTo,  
            PriorityID=task.PriorityID,  
            Status=task.Status,  
            DueDate=task.DueDate,
            
        ) 
        Task_view.append(task_vm)
    return render(request,'mytasks.html',{'form':Task_view})

def AssignedTasks(request):
    assignedlist=TaskDataDetails()
    Task_view=[]
    for task in assignedlist:
        task_vm = assignedviewmodel(
            AssignedID=task.AssignedID,
            TaskID=task.TaskID,  
            AssignedTo=task.AssignedTo,  
            PriorityID=task.PriorityID,  
            Status=task.Status,  
            DueDate=task.DueDate,
            
        ) 
        Task_view.append(task_vm)
    return render(request,'AssignedTasks.html',{'form':Task_view})

def comments(request,pk):
    commentlist=CommentsDetails(pk)
    Comments=[]
    for data in commentlist:
        comment = CommentViewModel(
            TaskID = data.TaskID,
            comment=data.Content,
            Date = data.Date,
            UserID = data.UserID,
            
        ) 
        Comments.append(comment)

    user_id = request.session.get('user_id')
    user=viewID(user_id,'Users')
    # print(user_id)
    # print(user)
    if request.method=='POST':
        form=CommentsForm(request.POST)
        if  form.is_valid():
            comment=CommentsServices(
                CommentID=None,
                Content=form.cleaned_data['content'],
                Date=None,
                UserID=user,
                TaskID=None,
            )
            addcomment(comment,pk)
            return redirect('TaskManagement')
    else:
        form=CommentsForm()
    return render(request, "comments.html", {'form':form,'Content':Comments})





def assign_task(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)

    if request.method == 'POST':
        form = TaskAssignForm(request.POST)
        if form.is_valid():
            assigned_to = form.cleaned_data['assigned_to']
            due_minutes = form.cleaned_data['due_minutes']

            TaskAssignment.objects.update_or_create(
                ticket=ticket,
                defaults={
                    'assigned_to': assigned_to,
                    'due_minutes': due_minutes
                }
            )

            # ticket.status = "Assigned"
            ticket.status = "Pending"
            ticket.save()
            ticket_link = request.build_absolute_uri(f"/Management/tickets/{ticket.id}/")
            login_url = request.build_absolute_uri(f"/Management/user/login/")


            management_emails = list(Users.objects.values_list('UserName', flat=True))
            send_mail(
                subject=f"You have been assigned Ticket #{ticket.id}",
                message=f"""
Hi {assigned_to.get_full_name() or assigned_to.username},

You have been assigned a new ticket:

━━━━━━━━━━━━━━━━━━━
Subject: {ticket.subject}
Description: {ticket.description}
Due In: {due_minutes} minutes
━━━━━━━━━━━━━━━━━━━

Please check the system to take necessary action.
Link: {login_url}

- HelpDesk Admin
""",
                
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[assigned_to.email],
                fail_silently=False
            )

            send_mail(
                subject=f"Update on your Ticket #{ticket.id}",
                message=f"""
Hi {ticket.user}, your issue has been assigned to {assigned_to}.
                
━━━━━━━━━━━━━━━━━━━
Subject: {ticket.subject}
Description: {ticket.description}
Estimated Resolving Time: {due_minutes} minutes
━━━━━━━━━━━━━━━━━━━

- HelpDesk Admin
Created by Gautam""",
             
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ticket.user.email],
                fail_silently=False
            )

            messages.success(request, f"Task assigned to {assigned_to.username} and emails sent.")
            return redirect('TaskManagement')  



from django.views.decorators.http import require_POST
@require_POST
def revert_ticket(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    message_text = request.POST.get('feedback') 
    management_emails = list(Users.objects.values_list('UserName', flat=True))
    if not message_text:
        messages.warning(request, "No message provided.")
    else:
        try:
            send_mail(
                subject=f"Revert on Ticket #{ticket.id}",
                message=f"""
Hello {ticket.user.get_full_name() or ticket.user.username},

Your submitted ticket has been reverted for the following reason:

━━━━━━━━━━━━━━━━━━━
{message_text}
━━━━━━━━━━━━━━━━━━━

Please review and make changes to your ticket accordingly.

- HelpDesk Admin
""",
                
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ticket.user.email],
                fail_silently=False
            )
            messages.success(request, f"Revert email sent to {ticket.user.username}.")
        except Exception as e:
            messages.warning(request, f"Failed to send revert email: {str(e)}")

    return redirect('TaskManagement')  


# tickets/views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import date



def todays_tickets_pdf(request):
    today = date.today()
    tickets = Tickets.objects.filter(created__date=today)

    context = {'tickets': tickets}
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="tickets_{today}.pdf"'
    response['Content-Disposition'] = f'inline; filename="tickets_{today}.pdf"'

    template = get_template('tickets_pdf.html')  # ✅ CORRECT


    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
