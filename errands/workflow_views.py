from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User
from .models import ErrandRequest
from .views import paginate

MEMBER = User.Role.MEMBER
ADMIN = User.Role.ADMIN
Status = ErrandRequest.Status


def _change_status(request, pk, required_status, role_field, new_values, success_msg, error_msg):
    """Change the status only if the errand is in the right state and belongs to this user."""
    filters = {'pk': pk, 'status': required_status, role_field: request.user}
    updated = ErrandRequest.objects.filter(**filters).update(**new_values)
    if updated:
        messages.success(request, success_msg)
    else:
        messages.error(request, error_msg)
    return redirect('errand_detail', pk=pk)


@require_POST
@role_required(MEMBER)
def errand_accept(request, pk):
    errand = get_object_or_404(ErrandRequest, pk=pk)
    if errand.owner_id == request.user.id:
        messages.error(request, 'You cannot accept your own errand.')
    elif errand.deadline <= timezone.now():
        messages.error(request, 'This errand has already passed its deadline.')
    else:
        # The filter on status=OPEN stops two people from accepting the same errand
        updated = ErrandRequest.objects.filter(pk=pk, status=Status.OPEN).update(
            status=Status.ACCEPTED, taker=request.user, accepted_at=timezone.now()
        )
        if updated:
            messages.success(request, 'You accepted this errand. Contact the owner and get it done!')
        else:
            messages.error(request, 'Sorry, someone else already accepted this errand.')
    return redirect('errand_detail', pk=pk)


@require_POST
@role_required(MEMBER)
def errand_withdraw(request, pk):
    return _change_status(
        request, pk, Status.ACCEPTED, 'taker',
        {'status': Status.OPEN, 'taker': None, 'accepted_at': None},
        'You withdrew from this errand. It is open again.',
        'You cannot withdraw from this errand.',
    )


@require_POST
@role_required(MEMBER)
def errand_complete(request, pk):
    return _change_status(
        request, pk, Status.ACCEPTED, 'taker',
        {'status': Status.COMPLETED, 'completed_at': timezone.now()},
        'Marked as completed. Waiting for the owner to confirm your reward.',
        'You cannot complete this errand.',
    )


@require_POST
@role_required(MEMBER)
def errand_confirm(request, pk):
    return _change_status(
        request, pk, Status.COMPLETED, 'owner',
        {'status': Status.CONFIRMED, 'confirmed_at': timezone.now()},
        'Reward confirmed. This errand is now closed.',
        'You cannot confirm this errand.',
    )


@role_required(MEMBER)
def my_tasks(request):
    errands = (
        ErrandRequest.objects.filter(taker=request.user).select_related('category', 'owner')
    )
    current_status = request.GET.get('status', '')
    if current_status in Status.values:
        errands = errands.filter(status=current_status)
    page_obj, querystring = paginate(request, errands, 10)
    return render(request, 'errands/my_tasks.html', {
        'page_obj': page_obj,
        'querystring': querystring,
        'statuses': [s for s in Status.choices if s[0] != Status.OPEN],
        'current_status': current_status,
        'mode': 'tasks',
    })


@role_required(ADMIN)
def manage_errands(request):
    errands = ErrandRequest.objects.select_related('category', 'owner', 'taker')
    current_status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    if current_status in Status.values:
        errands = errands.filter(status=current_status)
    if q:
        errands = errands.filter(
            Q(title__icontains=q) | Q(owner__username__icontains=q) | Q(taker__username__icontains=q)
        )
    page_obj, querystring = paginate(request, errands, 15)
    return render(request, 'errands/manage_errands.html', {
        'page_obj': page_obj,
        'querystring': querystring,
        'statuses': Status.choices,
        'current_status': current_status,
        'q': q,
    })


@role_required(ADMIN)
def admin_errand_delete(request, pk):
    errand = get_object_or_404(ErrandRequest, pk=pk)
    if request.method == 'POST':
        errand.delete()
        messages.success(request, 'Errand deleted by admin.')
        return redirect('manage_errands')
    return render(request, 'errands/errand_confirm_delete.html', {'errand': errand})