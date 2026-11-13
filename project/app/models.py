from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal

class Employee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employeeid = models.CharField(max_length=50, unique=True)
    phonenumber = models.CharField(max_length=10, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=200, blank=True)
    joiningdate = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.employeeid




class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave'),
    ]

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE
    )

    date = models.DateField(default=timezone.localdate)

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Present'
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_attendance_per_day'
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.date}"


class Leave(models.Model):

    LEAVE_TYPES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Emergency Leave', 'Emergency Leave'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE
    )

    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPES
    )

    from_date = models.DateField()

    to_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    applied_on = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"




class SalaryIncrement(models.Model):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='salary_increments'
    )

    increment_type = models.CharField(
        max_length=20,
        choices=[
            ('COMMON', 'Common Increment'),
            ('PERSONAL', 'Personal Increment'),
        ]
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    old_salary = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0
    )

    increment_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    new_salary = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    effective_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.increment_type}"


class PayrollBonus(models.Model):
    BONUS_CHOICES = [
    ('Onam', 'Onam'),
    ('Deepavali', 'Deepavali'),
    ('Christmas', 'Christmas'),
    ('Ramzan', 'Ramzan'),
    ('Other', 'Other'),
]

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='bonuses'
    )

    bonus_type = models.CharField(
        max_length=20,
        choices=BONUS_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    description = models.CharField(
        max_length=255, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.bonus_type}"


class Payroll(models.Model):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='payrolls'
    )

    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    # Salary snapshot when payroll is generated
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0
    )

    bonus_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0
    )

    payroll_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"

