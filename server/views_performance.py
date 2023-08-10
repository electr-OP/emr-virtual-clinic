from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect

from server.forms import PerformanceReviewForm
from server.models import Action, Account, PerformanceReview
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
    template_data['query'] = PerformanceReview.objects.all()
    return render(request, 'virtualclinic/PerformanceReview/list.html', template_data)



def create_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN, Account.ACCOUNT_LAB]
    )
    if authentication_result is not None:
        return authentication_result
    # get template data from session
    template_data = views.parse_session(request, {'form_button': "Add Performance Review"})
    # proceed with rest of the view
    default = {}

    request.POST._mutable = True
    request.POST.update(default)
    form = PerformanceReviewForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            leave_request = form.generate()
            leave_request.save()
            logger.log(Action.ACTION_MEDTEST, 'Performance Review Created', request.user.account)
            form = PerformanceReviewForm(default)  # clean form data
            form._errors = {}
            template_data['alert_success'] = "Successfully Added Performance Review"
    else:
        form._errors = {}
    template_data['form'] = form
    return render(request, 'virtualclinic/PerformanceReview/create.html', template_data)


def update_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None:
        return authentication_result
    # Validation check. Make sure a medical test exists for given pk.
    pk = request.GET['pk']
    try:
        leave_request = PerformanceReview.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested Performance ReviewF does not exist"
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
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     request.POST['doctor'] = request.user.account.pk
    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST)
        if form.is_valid():
            form.assign(leave_request)
            leave_request.save()
            logger.log(Action.ACTION_MEDTEST, 'Payroll Updated', request.user.account)
            template_data['alert_success'] = "Payroll has been updated"
            template_data['form'] = form
    else:
        form = PerformanceReviewForm(leave_request.get_populated_fields())
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     form.disable_field('doctor')
    template_data['form'] = form
    return render(request, 'virtualclinic/PerformanceReview/update.html', template_data)
