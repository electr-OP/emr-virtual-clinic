from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect

from server.forms import LeaveRequestForm
from server.models import Action, Account, LeaveRequest
from server import logger
from server import views


def list_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with rest of the view
    template_data['query'] = LeaveRequest.objects.all()
    return render(request, 'virtualclinic/LeaveRequest/list.html', template_data)


def create_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN, Account.ACCOUNT_LAB]
    )
    if authentication_result is not None:
        return authentication_result
    # get template data from session
    template_data = views.parse_session(request, {'form_button': "Request Leave"})
    # proceed with rest of the view
    default = {}
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     default['doctor'] = request.user.account.pk
    # if 'hospital' not in request.POST and request.user.account.profile.prefHospital is not None:
    #     default['hospital'] = request.user.account.profile.prefHospital.pk
    # if 'date' not in request.POST:
    #     default['date'] = datetime.now().strftime("%Y-%m-%d")

    request.POST._mutable = True
    request.POST.update(default)
    form = LeaveRequestForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            leave_request = form.generate()
            if leave_request.clean():
                template_data['alert_danger'] = "Start date cannot be after end date."
                form = LeaveRequestForm(leave_request.get_populated_fields())
                template_data['form'] = form
                return render(request, 'virtualclinic/LeaveRequest/create.html', template_data)
            leave_request.save()
            logger.log(Action.ACTION_MEDTEST, 'Leave Request Created', request.user.account)
            form = LeaveRequestForm(default)  # clean form data
            form._errors = {}
            template_data['alert_success'] = "Successfully Leave Request"
    else:
        form._errors = {}
    template_data['form'] = form
    return render(request, 'virtualclinic/LeaveRequest/create.html', template_data)


def update_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None:
        return authentication_result
    # Validation check. Make sure a medical test exists for given pk.
    pk = request.GET['pk']
    try:
        leave_request = LeaveRequest.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested Leave Request does not exist"
        return HttpResponseRedirect('/error/denied')
    # Get the template data from the session
    template_data = views.parse_session(
        request,
        {
            'form_button': "Update Leave Request",
            'form_action': "?pk=" + pk,
            'diagnosis': leave_request
        })
    # Proceed with rest of view
    request.POST._mutable = True
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            form.assign(leave_request)
            leave_request.save()
            logger.log(Action.ACTION_MEDTEST, 'Leave Request Updated', request.user.account)
            template_data['alert_success'] = "Leave Request has been updated"
            template_data['form'] = form
    else:
        form = LeaveRequestForm(leave_request.get_populated_fields())
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     form.disable_field('doctor')
    template_data['form'] = form
    return render(request, 'virtualclinic/LeaveRequest/update.html', template_data)


def leave_status_update_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    if authentication_result is not None:
        return authentication_result
    template_data = views.parse_session(request)
    try:
    # if request.method == 'POST':
        pk = request.GET['pk']
        status = request.GET['status']
        leaverequest = LeaveRequest.objects.get(pk=pk)
        if status in ['approve', 'reject']:
            leaverequest.status = status
            leaverequest.save()
            template_data['alert_success'] = "Leave Request has been updated"
        elif status == 'delete':
            leaverequest.delete()
        else:
            leaverequest.status = "pending"
            leaverequest.save()

    except Exception:
        pass
    # Get the template data from the session
    # template_data = views.parse_session(request)
    # Proceed with rest of the view
    template_data['query'] = LeaveRequest.objects.all()
    return render(request, 'virtualclinic/LeaveRequest/list.html', template_data)
