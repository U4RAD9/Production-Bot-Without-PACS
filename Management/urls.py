from django.urls import path
from django.contrib.auth import views as auth
from user.forms import LoginForm

from Management.presentation import UI as ui_views
from tickets import views as ticket_views
from user import views as user_views

# from user.admin import custom_admin_site


from user.views import CustomLoginView


urlpatterns = [

    path('dashboard/create/',ticket_views.create_ticket,name='dashboardsnewcreate'),
    path('dashboard/create/create',ticket_views.create_ticket,name='dashboardsnewcreate'),


    path('task/assign/<int:ticket_id>/', ui_views.assign_task, name='assign-task'),

    path('user/dashboard/', user_views.technic_dashboard, name='technic-dashboard'),

    # path('admin/', custom_admin_site.urls),  # <== now only superusers can log in


    # urls.py

    # path('task/taskmanagement/', ui_views.task_management_view, name='taskmanagement'),
    path('task/revert/<int:ticket_id>/', ui_views.revert_ticket, name='revert-ticket'),
    
    path('ticket/resolve-ticket/<int:ticket_id>/', user_views.resolve_ticket, name='resolve-ticket'),


    path('tickets/<int:ticket_id>/revert/', user_views.revert_ticket_from_technician, name='revert-ticket-technician'),


    # -------------------- UI TASK MANAGEMENT --------------------
    path('', ui_views.landing_page, name='management-home'),
    # path('task/', ui_views.dashboard, name='Dashboard'),
    path('task/', ui_views.dashboard, name='Dashboard'),

    path('task/register/', ui_views.register, name='register'),
    path('task/login/', ui_views.user_login, name='login'),
    path('task/HomePage/', ui_views.Home, name='TaskManagement'),
    
    path('pdf/today/', ui_views.todays_tickets_pdf, name='todays-tickets-pdf'),

    
    path('task/CreateTask/', ui_views.addTask, name='CreateTask'),
    path('task/mytasks/', ui_views.Tasks, name='mytask'),
    path('task/alltasks/', ui_views.AssignedTasks, name='allAssignedTasks'),
    path('task/update/<int:pk>/', ui_views.updateTask, name="update"),
    path('task/updatestatus/<int:pk>/', ui_views.UpdateStatus, name="updatestatus"),
    path('task/assigntask/<int:pk>/', ui_views.assign, name="AssignTask"),
    path('task/comments/<int:pk>/', ui_views.comments, name="Comments"),

    # -------------------- TICKET MANAGEMENT --------------------
    path('dashboard/',ticket_views.dashboard,name='dashboard'),
    path('tickets/<int:id>/', ticket_views.ticket_detail, name='ticket-detail'),
    path('tickets/<int:id>/<str:status>/', ticket_views.change_status, name='change-status'),
    path('tickets/close/<int:ticket_id>/', ticket_views.close_ticket, name='close_ticket'),
    path('tickets/<int:id>/category/<slug:category>/', ticket_views.change_category, name='change-category'),
    path('tickets/create/', ticket_views.create_ticket, name='create-ticket'),
    path('tickets/status/<str:status>/', ticket_views.status_view, name='status-view'),
    path('tickets/category/new/', ticket_views.new_category, name='new-category'),
    path('tickets/category/delete/<slug:cat>/', ticket_views.delete_category, name='delete-category'),
    path('tickets/category/edit/<slug:cat>/', ticket_views.edit_category, name='edit-category'),
    path('tickets/', ticket_views.tickets, name='tickets'),
    path('tickets/tickets/pdf/', ticket_views.render_pdf, name='render-pdf'),
    path('tickets/tickets/csv/', ticket_views.export_csv, name='export-csv'),
    path('tickets/date/clear/', ticket_views.clear_date, name='clear-date'),
    path('tickets/tickets/pdf/<int:id>/', ticket_views.ticket_detail_pdf, name='ticket-detail-pdf'),

    # -------------------- AUTH & USER MANAGEMENT --------------------
    path('task/login/', ui_views.user_login, name='login'),
    # path('user/login/', auth.LoginView.as_view(authentication_form=LoginForm), name='user-login'),
    # path('user/login/', user_views.login_view, name='user-login'),
    

    path('user/login/', CustomLoginView.as_view(), name='user-login'),


    
    path('user/logout/', user_views.custom_logout, name='logout'),
    path('user/password_change/', auth.PasswordChangeView.as_view(), name='password_change'),
    path('user/password_change/done/', auth.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('user/password_reset/', auth.PasswordResetView.as_view(), name='password_reset'),
    path('user/password_reset/done/', auth.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', auth.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user/register/', user_views.register, name='user-register'),
    path('user/edit/', user_views.edit, name='edit'),

    # -------------------- TECH --------------------
    path('tech/', user_views.tech_view, name='tech-view'),
    path('tech/<str:role>/', user_views.role_view, name='role-view'),
    path('tech/detail/<int:id>/', user_views.user_detail_view, name='user-detail-view'),
    path('tech/detail/delete/<int:id>/', user_views.user_delete, name='user-delete'),

    # -------------------- CUSTOMER --------------------
    path('customer/', user_views.customer_view, name='customer-view'),
    path('customer/new/', user_views.new_customer, name='new-customer'),

    # -------------------- SYSTEM --------------------
    path('system/error/', user_views.error, name='error'),
    path('system/contact-us/', user_views.contactus, name='contact-us'),

    path('dashboard/user/system/contact-us', user_views.contactus, name='contact-us'),
]
