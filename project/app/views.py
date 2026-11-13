from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Employee, Attendance, Leave, SalaryIncrement, Payroll, PayrollBonus
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from datetime import time
from django.db.models import Q
from django.db.models import Sum
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from django.db import transaction
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST



def home(request):
    return render(request,'home.html')

def register(request):
    if request.method == 'POST':

        employeeid = request.POST.get('employeeid', '').strip()
        employeename = request.POST.get('employeename', '').strip().lower()
        email = request.POST.get('email', '').strip()
        phonenumber = request.POST.get('phonenumber', '').strip()
        department = request.POST.get('department', '').strip()
        joiningdate = request.POST.get('joiningdate', '').strip()
        salary = request.POST.get('salary', '').strip()
        designation = request.POST.get('designation', '').strip()
        password = request.POST.get('password', '')

        # Basic validation
        if not employeeid:
            messages.error(request, "Please enter Employee ID.")
            return render(request, 'register.html')
        
        if not employeename:
            messages.error(request, "Please enter your full name.")
            return render(request, "register.html")

        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "register.html")

        if not password:
            messages.error(request, "Please enter a password.")
            return render(request, "register.html")

        # Check email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        

        # Create User
        user = User.objects.create_user(
            username=employeeid,
            first_name=employeename,
            email=email,
            password=password
        )
        

        # Create Candidate Profile
        profile = Employee.objects.create(
            user=user,
            employeeid=employeeid,
            phonenumber=phonenumber,
            department=department,
            joiningdate=joiningdate,
            salary=salary,
            designation=designation,            
        )


        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'register.html')



def login(request):

    if request.method == 'POST':

        employeeid = request.POST.get('employeeid', '').strip()
        password = request.POST.get('password', '')

        try:
            employee = Employee.objects.get(
                employeeid=employeeid
            )

            user = authenticate(
                request,
                username=employee.user.username,
                password=password
            )

            if user is not None:

                auth_login(request, user)

                request.session['employeeid'] = employee.employeeid

                messages.success(request, "Login successful!")

                return redirect('dashboard')

            else:
                messages.error(request, "Invalid password")

        except Employee.DoesNotExist:
            messages.error(request, "Employee not found")

    return render(request, 'login.html')


@login_required
def dashboard(request):

    employee = Employee.objects.get(user=request.user)

    # Present Days (Present + Late)
    working_days = Attendance.objects.filter(
        employee=employee,
        status__in=['Present', 'Late']
    ).count()

    # Leave Balance (Approved Leaves)
    leave_balance = Leave.objects.filter(
        employee=employee,
        status='Approved'
    ).count()

    context = {
        'employee': employee,
        'working_days': working_days,
        'leave_balance': leave_balance,
    }

    return render(request, 'dashboard.html', context)

@login_required
def edit_profile(request):

    employeeid = request.session.get('employeeid')

    if not employeeid:
        return redirect('login')

    employee = Employee.objects.get(employeeid=employeeid)

    if request.method == 'POST':

        employeename = request.POST.get('employeename', '').strip()
        email = request.POST.get('email', '').strip()
        phonenumber = request.POST.get('phonenumber').strip()
        department = request.POST.get('department', '').strip()
        joiningdate = request.POST.get('joiningdate').strip()
        salary = request.POST.get('salary').strip()
        designation = request.POST.get('designation', '')

        if User.objects.filter(email=email).exclude(
            pk=employee.user_id
        ).exists():

            messages.error(request, "Email already exists!")

        else:
            employee.user.first_name = employeename
            employee.user.email = email
            employee.user.save()

            employee.phonenumber=phonenumber
            employee.department = department
            employee.joiningdate=joiningdate
            employee.salary=salary
            employee.designation = designation
            employee.save()

            messages.success(request, "Profile updated successfully!")

            return redirect('dashboard')

    return render(request, 'edit_profile.html', {
        'employee': employee
    })


@login_required
def attendance(request):

    employee = Employee.objects.get(
        user=request.user
    )

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # Yesterday attendance check
    Attendance.objects.get_or_create(
        employee=employee,
        date=yesterday,
        defaults={
            'status': 'Absent'
        }
    )

    attendance_records = Attendance.objects.filter(
        employee=employee
    ).order_by('-date')

    present_days = attendance_records.filter(
        status='Present'
    ).count()

    absent_days = attendance_records.filter(
        status='Absent'
    ).count()

    late_days = attendance_records.filter(
        status='Late'
    ).count()

    leave_days = attendance_records.filter(
        status='Leave'
    ).count()

    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'leave_days': leave_days,
    }

    return render(
        request,
        'attendance.html',
        context
    )
@login_required
def mark_attendance(request):

    if request.method == "POST":

        employee = get_object_or_404(
            Employee,
            user=request.user
        )

        today = timezone.localdate()
        current_time = timezone.localtime().time()

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'status': 'Present'
            }
        )

        if attendance.check_in is None:

            attendance.check_in = current_time
            if current_time > time(9, 0):
                attendance.status = 'Late'
            else:
                attendance.status = 'Present'

            attendance.save()

            messages.success(request, "Check In Successful!")

        

        else:

            messages.warning(
                request,
                "Today's attendance is already completed!"
            )

    return redirect("attendance")


@login_required
def apply_leave(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    today = timezone.localdate()

    leave_records = Leave.objects.filter(
        employee=employee
    ).order_by('-id')

    leave_summary = get_monthly_leave_summary(
        employee,
        today.year,
        today.month
    )

    context = {
        'employee': employee,
        'leave_records': leave_records,
        'leave_summary': leave_summary,
        'current_month': today.strftime('%B %Y'),
    }

    return render(
        request,
        'apply_leave.html',
        context
    )



@login_required
def apply_leave_form(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    if request.method == "POST":

        leave_type = request.POST.get('leave_type')
        from_date = parse_date(request.POST.get('from_date', ''))
        to_date = parse_date(request.POST.get('to_date', ''))
        reason = request.POST.get('reason', '').strip()

        if not all([leave_type, from_date, to_date, reason]):

            messages.error(request, "Please fill all fields.")

        elif leave_type not in dict(Leave.LEAVE_TYPES):

            messages.error(request, "Invalid leave type.")

        elif from_date > to_date:

            messages.error(request, "Invalid leave dates!")

        else:

            allowed = True

            if leave_type in ['Casual Leave', 'Sick Leave']:

                current = from_date

                while current <= to_date:

                    month_start = date(
                        current.year,
                        current.month,
                        1
                    )

                    if current.month == 12:
                        next_month = date(current.year + 1, 1, 1)
                    else:
                        next_month = date(
                            current.year,
                            current.month + 1,
                            1
                        )

                    month_end = next_month - timedelta(days=1)

                    period_end = min(to_date, month_end)

                    requested_days = (
                        period_end - current
                    ).days + 1

                    summary = get_monthly_leave_summary(
                        employee,
                        current.year,
                        current.month
                    )

                    leave_info = next(
                        item for item in summary
                        if item['leave_type'] == leave_type
                    )

                    if requested_days + leave_info['used'] > 1:

                        messages.error(
                            request,
                            f"{leave_type} limit exceeded for "
                            f"{current.strftime('%B %Y')}. "
                            f"Only {leave_info['remaining']} day(s) remaining."
                        )

                        allowed = False
                        break

                    current = period_end + timedelta(days=1)

            if allowed:

                Leave.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    from_date=from_date,
                    to_date=to_date,
                    reason=reason,
                    status='Pending'
                )

                messages.success(
                    request,
                    "Leave application submitted successfully!"
                )

                return redirect('apply_leave')

    return render(
        request,
        'apply_leave_form.html',
        {'employee': employee}
    )


@login_required
def check_out(request):

    if request.method == "POST":

        employee = request.user.employee

        today = timezone.localdate()

        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()

        if attendance and attendance.check_out is None:

            attendance.check_out = timezone.localtime().time()
            attendance.save()

            messages.success(request, "Check Out Successful!")

        else:
            messages.error(
                request,
                "Please mark attendance first or Check Out already completed."
            )

    return redirect('attendance')

def adminlogin(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('admindashboard')

        else:
            messages.error(
                request,
                "Invalid credentials or not authorized as admin"
            )

    return render(request, 'adminlogin.html')



@login_required
def admindashboard(request):

    today = timezone.localdate()

    # Total Employees
    total_employees = Employee.objects.count()

    # Working Employees (Present + Late)
    working_employees = Attendance.objects.filter(
        date=today,
        status__in=['Present', 'Late']
    ).count()
    

    # Absent Employees
    absent_today = Attendance.objects.filter(
        date=today,
        status='Absent'
    ).count()

    # Leave Employees
    leave_today = Attendance.objects.filter(
        date=today,
        status='Leave'
    ).count()

    context = {
        'total_employees': total_employees,
        'working_employees': working_employees,
        'absent_today': absent_today,
        'leave_today': leave_today,
    }

    return render(request, 'admindashboard.html', context)




# Employee Management

def manage_employee(request):

    search = request.GET.get('search', '').strip()

    employees = Employee.objects.select_related('user').all().order_by('employeeid')

    if search:
        employees = employees.filter(
            Q(employeeid__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(department__icontains=search)
        )

    context = {
        'employees': employees,
        'search': search,
        'total_employees': Employee.objects.count(),
    }

    return render(request, 'manage_employee.html', context)





# Delete Employee


def delete_employee(request, id):

    employee = get_object_or_404(Employee, id=id)

    employee.delete()

    messages.success(
        request,
        'Employee deleted successfully!'
    )

    return redirect('manage_employee')




def get_monthly_leave_summary(employee, year, month):

    first_day = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = next_month - timedelta(days=1)

    summary = []

    for leave_type in ['Casual Leave', 'Sick Leave']:

        used = 0

        approved_leaves = Leave.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status='Approved',
            from_date__lte=last_day,
            to_date__gte=first_day
        )

        for leave in approved_leaves:

            start = max(leave.from_date, first_day)
            end = min(leave.to_date, last_day)

            used += (end - start).days + 1

        summary.append({
            'leave_type': leave_type,
            'allowed': 1,
            'used': used,
            'remaining': max(0, 1 - used),
        })

    return summary

# ==========================================
# ADMIN MONTHLY LEAVE MANAGEMENT
# ==========================================

def get_approved_leave_days(employee, leave_type, year, month, exclude_id=None):

    first_day = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = next_month - timedelta(days=1)

    leaves = Leave.objects.filter(
        employee=employee,
        leave_type=leave_type,
        status='Approved',
        from_date__lte=last_day,
        to_date__gte=first_day
    )

    if exclude_id:
        leaves = leaves.exclude(id=exclude_id)

    used = 0

    for leave in leaves:
        start = max(leave.from_date, first_day)
        end = min(leave.to_date, last_day)
        used += (end - start).days + 1

    return used


@login_required
def manage_leave(request):
    total_employees = Employee.objects.count()
    if not request.user.is_staff:
        messages.error(request, "Admin access required.")
        return redirect('adminlogin')

    today = timezone.localdate()

    employees = Employee.objects.select_related(
        'user'
    ).all().order_by('employeeid')

    monthly_balances = []

    for employee in employees:

        for leave_type in ['Casual Leave', 'Sick Leave']:

            used = get_approved_leave_days(
                employee,
                leave_type,
                today.year,
                today.month
            )

            monthly_balances.append({
                'employeeid': employee.employeeid,
                'name': employee.user.first_name,
                'leave_type': leave_type,
                'allowed': 1,
                'used': used,
                'remaining': max(0, 1 - used)
            })

    leave_records = Leave.objects.select_related(
        'employee',
        'employee__user'
    ).all().order_by('-applied_on')

    context = {
        'total_employees': total_employees,
        'monthly_balances': monthly_balances,
        'leave_records': leave_records,
        'current_month': today.strftime('%B %Y'),
        'total_requests': leave_records.count(),
        'pending_count': leave_records.filter(
            status='Pending'
        ).count(),
        'approved_count': leave_records.filter(
            status='Approved'
        ).count(),
        'rejected_count': leave_records.filter(
            status='Rejected'
        ).count(),
    }

    return render(
        request,
        'manage_leave.html',
        context
    )


# ==========================================
# ADMIN APPROVE / REJECT LEAVE
# ==========================================

@login_required
@require_POST
def admin_leave_action(request, id):

    if not request.user.is_staff:
        messages.error(request, "Admin access required.")
        return redirect('adminlogin')

    action = request.POST.get('action')

    if action not in ['approve', 'reject']:
        messages.error(request, "Invalid action.")
        return redirect('admin_leave_management')

    with transaction.atomic():

        leave = get_object_or_404(
            Leave.objects.select_related('employee'),
            id=id
        )

        # Lock employee row during quota validation
        employee = Employee.objects.select_for_update().get(
            id=leave.employee_id
        )

        if leave.status != 'Pending':

            messages.warning(
                request,
                "This leave request has already been processed."
            )

        elif action == 'reject':

            leave.status = 'Rejected'
            leave.save(update_fields=['status'])

            messages.success(
                request,
                "Leave request rejected successfully!"
            )

        else:

            allowed = True

            if leave.leave_type in [
                'Casual Leave',
                'Sick Leave'
            ]:

                current = leave.from_date

                while current <= leave.to_date:

                    if current.month == 12:
                        next_month = date(
                            current.year + 1, 1, 1
                        )
                    else:
                        next_month = date(
                            current.year,
                            current.month + 1,
                            1
                        )

                    month_end = next_month - timedelta(days=1)

                    period_end = min(
                        leave.to_date,
                        month_end
                    )

                    requested_days = (
                        period_end - current
                    ).days + 1

                    used = get_approved_leave_days(
                        employee,
                        leave.leave_type,
                        current.year,
                        current.month,
                        exclude_id=leave.id
                    )

                    if used + requested_days > 1:

                        messages.error(
                            request,
                            f"Cannot approve. "
                            f"{leave.leave_type} monthly quota "
                            f"exceeded for {current.strftime('%B %Y')}."
                        )

                        allowed = False
                        break

                    current = period_end + timedelta(days=1)

            if allowed:

                leave.status = 'Approved'
                leave.save(update_fields=['status'])

                messages.success(
                    request,
                    "Leave approved successfully!"
                )

    return redirect('manage_leave')

@transaction.atomic
def apply_common_increment(percentage):
    percentage = Decimal(str(percentage))

    if percentage <= 0:
        raise ValueError("Percentage must be greater than zero")

    employees = Employee.objects.select_for_update().all()

    for employee in employees:
        old_salary = Decimal(str(employee.salary))

        increment = (
            old_salary * percentage / Decimal('100')
        ).quantize(Decimal('0.01'))

        new_salary = old_salary + increment

        SalaryIncrement.objects.create(
            employee=employee,
            increment_type='COMMON',
            old_salary=old_salary,
            percentage=percentage,
            increment_amount=increment,
            new_salary=new_salary,
            effective_date=timezone.localdate()
        )

        
        





@transaction.atomic
def apply_personal_increment(employee_id, percentage, reason):
    employee = Employee.objects.select_for_update().get(
        pk=employee_id
    )

    percentage = Decimal(str(percentage))

    if percentage <= 0:
        raise ValueError("Percentage must be greater than zero")

    old_salary = Decimal(str(employee.salary))

    increment = (
        old_salary * percentage / Decimal('100')
    ).quantize(Decimal('0.01'))

    new_salary = old_salary + increment

    SalaryIncrement.objects.create(
        employee=employee,
        increment_type='PERSONAL',
        old_salary=old_salary,
        percentage=percentage,
        increment_amount=increment,
        new_salary=new_salary,
        reason=reason,
        effective_date=timezone.localdate()
    )

    

@transaction.atomic
def generate_monthly_payroll(month, year):

    for employee in Employee.objects.all():

        basic_salary = Decimal(str(employee.salary))

        bonus = PayrollBonus.objects.filter(
            employee=employee,
            month=month,
            year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total = basic_salary + bonus

        Payroll.objects.update_or_create(
            employee=employee,
            month=month,
            year=year,
            defaults={
                'basic_salary': basic_salary,
                'bonus_amount': bonus,
                'payroll_amount': total,
            }
        )










@login_required
def manage_salary(request):

    search = request.GET.get('search', '').strip()
    today = timezone.localdate()

    employees = Employee.objects.select_related(
        'user'
    ).all().order_by('employeeid')

    if search:
        employees = employees.filter(
            Q(employeeid__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(department__icontains=search) |
            Q(designation__icontains=search)
        )

    for employee in employees:

        # Basic Salary
        basic_salary = Decimal(str(employee.salary or '0'))

        # Common Increment
        employee.common_increment = (
            SalaryIncrement.objects.filter(
                employee=employee,
                increment_type='COMMON'
            ).aggregate(
                total=Sum('increment_amount')
            )['total'] or Decimal('0.00')
        )

        # Personal Increment
        employee.personal_increment = (
            SalaryIncrement.objects.filter(
                employee=employee,
                increment_type='PERSONAL'
            ).aggregate(
                total=Sum('increment_amount')
            )['total'] or Decimal('0.00')
        )

        # Festival Bonus
        employee.festival_bonus = (
            PayrollBonus.objects.filter(
                employee=employee,
                month=today.month,
                year=today.year
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
        )

        # Total Salary = All Four Amounts
        employee.monthly_payroll = (
            basic_salary
            + employee.common_increment
            + employee.personal_increment
            + employee.festival_bonus
        )

    context = {
        'employees': employees,
        'total_employees': Employee.objects.count(),
        'search': search,
    }

    return render(request, 'manage_salary.html', context)


@login_required
@require_POST
@transaction.atomic
def common_increment_view(request):

    try:
        percentage = Decimal(request.POST.get('percentage'))

        if percentage <= 0 or percentage > 100:
            raise ValueError

    except (TypeError, ValueError, InvalidOperation):
        messages.error(request, 'Invalid percentage.')
        return redirect('manage_salary')

    employees = Employee.objects.select_for_update().all()

    for employee in employees:

        old_salary = Decimal(str(employee.salary or '0'))

        increment = (
            old_salary * percentage / Decimal('100')
        ).quantize(Decimal('0.01'))

        SalaryIncrement.objects.create(
            employee=employee,
            increment_type='COMMON',
            reason='Common Yearly Increment',
            old_salary=old_salary,
            percentage=percentage,
            increment_amount=increment,
            new_salary=old_salary + increment,
            effective_date=timezone.localdate()
        )

    messages.success(request, 'Common increment applied successfully!')

    return redirect('manage_salary')




@login_required
@require_POST
@transaction.atomic
def personal_increment_view(request):

    employee_id = request.POST.get('employee_id')
    reason = request.POST.get('reason', '').strip()

    try:
        percentage = Decimal(request.POST.get('percentage'))

        if percentage <= 0 or percentage > 100:
            raise ValueError

    except (TypeError, ValueError, InvalidOperation):
        messages.error(request, 'Invalid increment percentage.')
        return redirect('manage_salary')

    if not reason:
        messages.error(request, 'Please select a reason.')
        return redirect('manage_salary')

    employee = get_object_or_404(
        Employee.objects.select_for_update(),
        pk=employee_id
    )

    old_salary = Decimal(str(employee.salary or '0'))

    increment = (
        old_salary * percentage / Decimal('100')
    ).quantize(Decimal('0.01'))

    new_salary = old_salary + increment

    SalaryIncrement.objects.create(
        employee=employee,
        increment_type='PERSONAL',
        reason=reason,
        old_salary=old_salary,
        percentage=percentage,
        increment_amount=increment,
        new_salary=new_salary,
        effective_date=timezone.localdate()
    )

    messages.success(request, 'Special increment added successfully!')

    return redirect('manage_salary')





@login_required
@transaction.atomic
def add_festival_bonus(request):

    if request.method == 'POST':

        festival = request.POST.get('festival')

        try:
            amount = Decimal(request.POST.get('amount'))

            if amount <= 0:
                raise ValueError

        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, 'Invalid bonus amount.')
            return redirect('manage_salary')

        valid_festivals = [
            'Onam', 'Deepavali', 'Christmas',
            'Ramzan', 'Other'
        ]

        if festival not in valid_festivals:
            messages.error(request, 'Invalid festival.')
            return redirect('manage_salary')

        today = timezone.localdate()
        # Check whether bonus is already given this month
        already_given = PayrollBonus.objects.filter(
        month=today.month,
        year=today.year).exists()

        if already_given:
            messages.error(request, 'Festival bonus has already been given this month!')
            return redirect('manage_salary')

        for employee in Employee.objects.all():

            PayrollBonus.objects.create(
                employee=employee,
                bonus_type=festival,
                amount=amount,
                month=today.month,
                year=today.year,
                description=f'{festival} Festival Bonus'
            )

        messages.success(request, 'Festival bonus added to all employees.')

    return redirect('manage_salary')


@login_required
def manage_attendance(request):

    if not request.user.is_staff:
        messages.error(request, "Admin access required.")
        return redirect('adminlogin')

    search = request.GET.get('search', '').strip()
    selected_date = request.GET.get('date', '')

    attendance_records = Attendance.objects.select_related(
        'employee',
        'employee__user'
    ).all().order_by('-date')

    if search:
        attendance_records = attendance_records.filter(
            Q(employee__employeeid__icontains=search) |
            Q(employee__user__first_name__icontains=search)
        )

    if selected_date:
        parsed_date = parse_date(selected_date)

        if parsed_date:
            attendance_records = attendance_records.filter(
                date=parsed_date
            )

    context = {
        'attendance_records': attendance_records,
        'search': search,
        'selected_date': selected_date,
        'total_records': attendance_records.count(),
        'total_employees': Employee.objects.count(),
    }

    return render(request, 'manage_attendance.html', context)






@login_required
def salary(request):

    employee = get_object_or_404(
        Employee.objects.select_related('user'),
        user=request.user
    )

    today = timezone.localdate()

    # Basic Salary
    basic_salary = employee.salary or Decimal('0.00')

    # Common Yearly Increment
    common_increment = SalaryIncrement.objects.filter(
        employee=employee,
        increment_type='COMMON'
    ).aggregate(
        total=Sum('increment_amount')
    )['total'] or Decimal('0.00')

    # Special Individual Increment
    personal_increment = SalaryIncrement.objects.filter(
        employee=employee,
        increment_type='PERSONAL'
    ).aggregate(
        total=Sum('increment_amount')
    )['total'] or Decimal('0.00')

    # Current Month Festival Bonus
    festival_bonus = PayrollBonus.objects.filter(
        employee=employee,
        month=today.month,
        year=today.year
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    # Total Monthly Salary
    monthly_payroll = (
        basic_salary
        + common_increment
        + personal_increment
        + festival_bonus
    )

    context = {
        'employee': employee,
        'basic_salary': basic_salary,
        'common_increment': common_increment,
        'personal_increment': personal_increment,
        'festival_bonus': festival_bonus,
        'monthly_payroll': monthly_payroll,
    }

    return render(request, 'salary.html', context)


def logout_employee(request):
    logout(request)
    return redirect('login')
def logout_admin(request):
    logout(request)
    return redirect('adminlogin')