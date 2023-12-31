from datetime import datetime

import requests
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from server import views
from .models import Account
from .forms import DiagnosisForm

def get_token():
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '3dc12fda-0dcb-448b-80c8-c5cfd60524f7_20c9745a-402c-42b7-ba68-1fe60a107788'
    client_secret = 'KmwBZPjU5CsSMuCpanNrQYdlGiAPQdafIuYDxl6ZMQg='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    # get the OAUTH2 token

    # set data to post
    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'scope': scope,
               'grant_type': grant_type}

    # make request
    r = requests.post(token_endpoint, data=payload, verify=False).json()
    token = r['access_token']
    return token


@api_view(['POST'])  # Specify the HTTP methods that are allowed
def get_entity_search(request):
    print(request.data)
    try:
        search_string = request.data['q']
        if not search_string:
            data = {'message': 'missing argument "q"'}
            return Response(data)
        token = get_token()

        # access ICD API
        uri = 'https://id.who.int/icd/entity/search'

        # HTTP header fields to set
        headers = {'Authorization': 'Bearer ' + token,
                   'Accept': 'application/json',
                   'Accept-Language': 'en',
                   'API-Version': 'v2'}

        payload = {'q': "fever",
                   'useFlexisearch': 'false',
                   "flatResults": 'false'
                   }

        # make request
        r = requests.post(uri, headers=headers, verify=False, data=payload)

        # print the result
        # print(r.json()['destinationEntities'])
        data = r.json()['destinationEntities']
        return Response(data)
    except Exception as E:
        data = {'message': 'missing argument "q"'}
        return Response(data)


def get_entity_search_2(string):
    # try:
    token = get_token()

    # access ICD API
    uri = 'https://id.who.int/icd/entity/search'

    # HTTP header fields to set
    headers = {'Authorization': 'Bearer ' + token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    payload = {'q': string,
               'useFlexisearch': 'false',
               "flatResults": 'false'
               }

    # make request
    r = requests.post(uri, headers=headers, verify=False, data=payload)

    # print the result
    # print(r.json()['destinationEntities'])
    data = r.json()['destinationEntities']
    return data
    # except Exception as E:
    #     # data = {'message': 'missing argument "q"'}
    #     return Response(data)



def get_entity(link):
    token = get_token()
    print(token)

    # access ICD API

    # uri = 'https://id.who.int/icd/entity'

    # HTTP header fields to set
    headers = {'Authorization': 'Bearer ' + token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    # make request
    r = requests.get(link, headers=headers, verify=False)

    # print the result
    # print(r.text)
    data = r.json()
    return data

# get_entity_search()


def search_view(request):
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    template_data = views.parse_session(request, {'form_button': "Add Employee"})
    if authentication_result is not None:
        return authentication_result
    if request.method == 'POST':
        search_string = request.POST.get('q')
        template_data['alert_success'] = "Successfully Gotten an Search"
        template_data['query'] = get_entity_search_2(search_string)
        # print(template_data['query'])
    # template_data = views.parse_session(request)
    # Proceed with rest of the view
    # template_data['query'] = Account.objects.exclude(role=Account.ACCOUNT_PATIENT)
    return render(request, 'virtualclinic/ICD/search_list.html', template_data)


def get_fields(template_data):
    fields = ['title', 'definition', 'longdefinition']

    for field in fields:
        try:
            template_data['query'][f'{field}'] = template_data['query'][f'{field}']['@value']
        except Exception as E:
            template_data['query'][f'{field}'] = ""

    return template_data


def view_entity(request):
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_ADMIN]
    )
    template_data = views.parse_session(request, {'form_button': "Add Employee"})
    link = request.GET['pk']
    if authentication_result is not None:
        return authentication_result
    if request.method == 'GET':
        template_data['alert_success'] = "Successfully Gotten an Entity"
        get_entity(link)
        template_data['query'] = get_entity(link)
        template_data = get_fields(template_data)

    return render(request, 'virtualclinic/ICD/view_entity.html', template_data)


def create_icd_diagnosis_view(request):
    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_DOCTOR, Account.ACCOUNT_LAB, Account.ACCOUNT_ADMIN]
    )

    if authentication_result is not None:
        return authentication_result

    if request.method == 'GET':
        link = request.GET['pk']
        template_data = views.parse_session(request, {'form_button': "Add Diagnosis"})
        template_data['alert_success'] = "Successfully Gotten an Entity"
        get_entity(link)
        template_data['query'] = get_entity(link)
        template_data = get_fields(template_data)
    # proceed with rest of the view
    default = {}
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    #     default['doctor'] = request.user.account.pk
    # if 'hospital' not in request.POST and request.user.account.profile.prefHospital is not None:
    #     default['hospital'] = request.user.account.profile.prefHospital.pk
    # if 'date' not in request.POST:
    #     default['date'] = datetime.now().strftime("%Y-%m-%d")
    default = {
        "condition": template_data['query']['title'],
        "notes": template_data['query']['definition']
    }
    request.POST._mutable = True
    request.POST.update(default)
    form = DiagnosisForm(request.POST,request.FILES)

    if request.method == 'POST':
        if form.is_valid():
            diagnosis = form.generate()
            diagnosis.save()
            # logger.log(Action.ACTION_MEDTEST,'Patient Diagnosis Created', request.user.account)
            form = DiagnosisForm(default)  # clean form data
            #form.disable_field('doctor')
            form._errors = {}
            template_data['alert_success'] = "Successfully Created Patient Diagnosis"
    else:
        form._errors = {}
    # form.notes.initial = template_data['query']["definition"]
    # form.condition.initial = template_data['query']['title']
    # form.condition.bound_data(template_data['query']["definition"],'')
    # form.notes.bound_data(template_data['query']["title"],'')
    form.condition = template_data['query']['title']
    print(form)
    template_data['form'] = form
    return render(request,'virtualclinic/diagnosis/add_diagnosis.html', template_data)
