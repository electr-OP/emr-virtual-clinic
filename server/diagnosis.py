from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect

from server.forms import MedicalInfoForm, DiagnosisForm
from server.models import Action, Account, MedicalInfo, Diagnosis
from server import logger
from server import views


def list_view_diagnosis(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_DOCTOR]
    )
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with rest of the view
    template_data['query'] = Diagnosis.objects.all()
    return render(request,'virtualclinic/diagnosis/diagnosis.html',template_data)


def create_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_DOCTOR, Account.ACCOUNT_LAB]
    )
    if authentication_result is not None:
        return authentication_result
    # get template data from session
    template_data = views.parse_session(request, {'form_button': "Upload"})
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
    form = DiagnosisForm(request.POST,request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            diagnosis = form.generate()
            diagnosis.save()
            logger.log(Action.ACTION_MEDTEST,'Patient Diagnosis Created', request.user.account)
            form = DiagnosisForm(default)  # clean form data
            #form.disable_field('doctor')
            form._errors = {}
            template_data['alert_success'] = "Successfully Created Patient Diagnosis"
    else:
        form._errors = {}
    #form.disable_field('doctor')
    template_data['form'] = form
    return render(request,'virtualclinic/diagnosis/add_diagnosis.html', template_data)


def update_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None:
        return authentication_result
    # Validation check. Make sure a medical test exists for given pk.
    pk = request.GET['pk']
    try:
        diagnosis = Diagnosis.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested medical test does not exist"
        return HttpResponseRedirect('/error/denied')
    # Get the template data from the session
    template_data = views.parse_session(
        request,
        {
            'form_button':"Update Diagnosis Test",
            'form_action':"?pk="+pk,
            'diagnosis':diagnosis
        })
    # Proceed with rest of view
    request.POST._mutable = True
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     request.POST['doctor'] = request.user.account.pk
    if request.method == 'POST':
        form = Diagnosis(request.POST)
        if form.is_valid():
            form.assign(diagnosis)
            diagnosis.save()
            logger.log(Action.ACTION_MEDTEST, 'Diagnosis Updated', request.user.account)
            template_data['alert_success'] = "Diagnosis has been updated"
            template_data['form'] = form
    else:
        form = DiagnosisForm(diagnosis.get_populated_fields())
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     form.disable_field('doctor')
    template_data['form'] = form
    return render(request,'virtualclinic/diagnosis/update.html', template_data)