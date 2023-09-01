from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect

from server.forms import MedicalInfoForm, DiagnosisForm, AccountForm
from server.models import Action, Account, MedicalInfo, Diagnosis
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
    template_data['query'] = Account.objects.exclude(role=Account.ACCOUNT_PATIENT)
    return render(request,'virtualclinic/Employee/list.html',template_data)


def create_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    if authentication_result is not None:
        return authentication_result
    # get template data from session
    template_data = views.parse_session(request, {'form_button': "Add Employee"})
    # proceed with rest of the view
    default = {}
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     default['doctor'] = request.user.account.pk
    # if 'hospital' not in request.POST and request.user.account.profile.prefHospital is not None:
    #     default['hospital'] = request.user.account.profile.prefHospital.pk
    if 'date' not in request.POST:
        default['date'] = datetime.now().strftime("%Y-%m-%d")

    request.POST._mutable = True
    request.POST.update(default)
    form = AccountForm(request.POST,request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            account = form.generate()
            account.save()
            logger.log(Action.ACTION_MEDTEST,'Employee Created', request.user.account)
            form = DiagnosisForm(default)  # clean form data
            #form.disable_field('doctor')
            form._errors = {}
            template_data['alert_success'] = "Successfully Created an Employee"
    else:
        form._errors = {}
    #form.disable_field('doctor')
    template_data['form'] = form
    return render(request,'virtualclinic/Employee/create.html', template_data)


def update_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    if authentication_result is not None:
        return authentication_result

    # Validation check. Make sure a medical test exists for given pk.
    pk = request.GET['pk']
    try:
        account = Account.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested employee does not exist"
        return HttpResponseRedirect('/error/denied')
    # Get the template data from the session
    template_data = views.parse_session(
        request,
        {
            'form_button':"Update Employee",
            'form_action':"?pk="+pk,
            'diagnosis':account
        })
    # Proceed with rest of view
    request.POST._mutable = True
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     request.POST['doctor'] = request.user.account.pk
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.assign(account)
            account.save()
            logger.log(Action.ACTION_MEDTEST, 'Diagnosis Updated', request.user.account)
            template_data['alert_success'] = "Diagnosis has been updated"
            template_data['form'] = form
    else:
        form = AccountForm(account.get_populated_fields())
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     form.disable_field('doctor')
    template_data['form'] = form
    return render(request,'virtualclinic/Employee/update.html', template_data)