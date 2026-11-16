from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from errands.models import ErrandRequest
from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User

Status = ErrandRequest.Status


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    return redirect('member_dashboard')


@role_required(User.Role.MEMBER)
def member_dashboard(request):
    posted = ErrandRequest.objects.filter(owner=request.user)
    tasks = ErrandRequest.objects.filter(taker=request.user)
    context = {
        'posted_open': posted.filter(status=Status.OPEN).count(),
        'posted_in_progress': posted.filter(status=Status.ACCEPTED).count(),
        'needs_confirmation': posted.filter(status=Status.COMPLETED).count(),
        'posted_done': posted.filter(status=Status.CONFIRMED).count(),
        'tasks_active': tasks.filter(status__in=[Status.ACCEPTED, Status.COMPLETED]).count(),
        'tasks_done': tasks.filter(status=Status.CONFIRMED).count(),
        'total_earned': tasks.filter(status=Status.CONFIRMED).aggregate(total=Sum('reward'))['total'] or 0,
        'recent_posted': posted.select_related('category')[:5],
        'recent_tasks': tasks.select_related('category', 'owner')[:5],
    }
    return render(request, 'accounts/member_dashboard.html', context)


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    errands = ErrandRequest.objects.all()
    context = {
        'total_users': User.objects.count(),
        'total_members': User.objects.filter(role=User.Role.MEMBER).count(),
        'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
        'total_errands': errands.count(),
        'errands_open': errands.filter(status=Status.OPEN).count(),
        'errands_active': errands.filter(status__in=[Status.ACCEPTED, Status.COMPLETED]).count(),
        'errands_done': errands.filter(status=Status.CONFIRMED).count(),
        'latest_users': User.objects.order_by('-date_joined')[:5],
        'latest_errands': errands.select_related('owner', 'category')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})