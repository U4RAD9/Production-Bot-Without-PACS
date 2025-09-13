# Let's enhance your ticket system with task assignment and admin email notifications only.
# Here's the minimal clean setup, from model to view to template:

# =======================
# 1. models.py (in tickets or separate task module)
# =======================
from django.db import models
from django.contrib.auth.models import User
from tickets.models import Tickets

class TaskAssignment(models.Model):
    ticket = models.OneToOneField(Tickets, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    due_minutes = models.IntegerField(choices=[
        (10, '10 minutes'), (15, '15 minutes'), (30, '30 minutes'),
        (60, '1 hour'), (240, '4 hours'), (1440, '1 day')
    ])
    # assigned_at = models.DateTimeField(auto_now_add=True)

    assigned_att = models.DateTimeField(null=True, blank=True)
    reassigned_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"#{self.ticket.id} to {self.assigned_to}"
