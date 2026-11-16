from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from .forms import ErrandFilterForm, ErrandForm
from .models import ErrandRequest

MEMBER = User.Role.MEMBER
ADMIN = User.Role.ADMIN
Status = ErrandRequest.Status

SORT_ORDER = {
    'newest': '-created_at',
    'reward_high': '-reward',
    'reward_low': 'reward',
    'deadline': 'deadline',
}


def paginate(request, queryset, per_page=9):
    page_obj = Paginator(queryset, per_page).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return page_obj, params.urlencode()


@role_required(MEMBER)
def errand_list(request):
    errands = (
        ErrandRequest.objects
        .filter(status=Status.OPEN, deadline__gt=timezone.now())
        .exclude(owner=request.user)
        .select_related('category', 'owner')
    )
    form = ErrandFilterForm(request.GET or None)
    sort = 'newest'

    if form.is_valid():
        data = form.cleaned_data
        if data.get('q'):
            q = data['q']
            errands = errands.filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
            )
        if data.get('category'):
            errands = errands.filter(category=data['category'])
        if data.get('min_reward') is not None:
            errands = errands.filter(reward__gte=data['min_reward'])
        if data.get('max_reward') is not None:
            errands = errands.filter(reward__lte=data['max_reward'])
        sort = data.get('sort') or 'newest'

    errands = errands.order_by(SORT_ORDER[sort])
    page_obj, querystring = paginate(request, errands)
    return render(request, 'errands/errand_list.html', {
        'filter_form': form,
        'page_obj': page_obj,
        'querystring': querystring,
    })


@role_required(MEMBER)
def errand_create(request):
    if request.method == 'POST':
        form = ErrandForm(request.POST)
        if form.is_valid():
            errand = form.save(commit=False)
            errand.owner = request.user
            errand.save()
            messages.success(request, 'Your errand has been posted.')
            return redirect('errand_detail', pk=errand.pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ErrandForm()
    return render(request, 'errands/errand_form.html', {
        'form': form,
        'page_title': 'Post an Errand',
        'submit_label': 'Post errand',
    })


@login_required
def errand_detail(request, pk):
    errand = get_object_or_404(
        ErrandRequest.objects.select_related('category', 'owner', 'taker'), pk=pk
    )
    user = request.user
    is_owner = errand.owner_id == user.id
    is_taker = errand.taker_id == user.id
    is_admin = user.role == ADMIN

    # Only the owner, the taker and admins can see errands that are no longer open
    if errand.status != Status.OPEN and not (is_owner or is_taker or is_admin):
        messages.error(request, 'That errand is no longer available.')
        return redirect('errand_list')

    can_accept = (
        user.role == MEMBER
        and not is_owner
        and errand.status == Status.OPEN
        and errand.deadline > timezone.now()
    )
    return render(request, 'errands/errand_detail.html', {
        'errand': errand,
        'is_owner': is_owner,
        'is_taker': is_taker,
        'is_admin': is_admin,
        'can_accept': can_accept,
    })


@role_required(MEMBER)
def errand_edit(request, pk):
    errand = get_object_or_404(ErrandRequest, pk=pk, owner=request.user)
    if errand.status != Status.OPEN:
        messages.error(request, 'You can only edit errands that are still open.')
        return redirect('errand_detail', pk=pk)

    if request.method == 'POST':
        form = ErrandForm(request.POST, instance=errand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Errand updated successfully.')
            return redirect('errand_detail', pk=pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ErrandForm(instance=errand)
    return render(request, 'errands/errand_form.html', {
        'form': form,
        'page_title': 'Edit Errand',
        'submit_label': 'Save changes',
    })


@role_required(MEMBER)
def errand_delete(request, pk):
    errand = get_object_or_404(ErrandRequest, pk=pk, owner=request.user)
    if errand.status != Status.OPEN:
        messages.error(request, 'You can only delete errands that are still open.')
        return redirect('errand_detail', pk=pk)

    if request.method == 'POST':
        errand.delete()
        messages.success(request, 'Errand deleted.')
        return redirect('my_requests')
    return render(request, 'errands/errand_confirm_delete.html', {'errand': errand})


@role_required(MEMBER)
def my_requests(request):
    errands = (
        ErrandRequest.objects.filter(owner=request.user).select_related('category', 'taker')
    )
    current_status = request.GET.get('status', '')
    if current_status in Status.values:
        errands = errands.filter(status=current_status)
    page_obj, querystring = paginate(request, errands, 10)
    return render(request, 'errands/my_requests.html', {
        'page_obj': page_obj,
        'querystring': querystring,
        'statuses': Status.choices,
        'current_status': current_status,
        'mode': 'requests',
    })