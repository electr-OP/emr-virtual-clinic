from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

IND_STATES = (
    ("Andhra Pradesh","Andhra Pradesh"),("Arunchal Pradesh","Arunchal Pradesh"),("Assam","Assam"),("Bihar","Bihar"),
    ("Chhattisghar", "Chhattisghar"), ("Goa","Goa"),("Gujarat","Gujarat"),("Haryana","Haryana"),("Himachal Pradesh","Himachal Pradesh",),
    ("Jammu and Kashmir","Jammu and Kashmir"),("Jharkhand","Jharkhand"),("Karnataka","Karnataka"),("Kerala","Kerala"),
    ("Madhya Pradesh","Madhya Pradesh"),("Maharashtra","Maharashtra"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),
    ("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),("Punjab","Punjab"),("Rajashtan","Rajashtan"),
    ("Sikkim","Sikkim"),("Tamil Nadu","Tamil Nadu"),("Telangana", "Telangana"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),
    ("West Bengal","West Bengal")
)


APPOINTMENT_TYPE = (
    ("Offline", "Offline"), ("Online","Online")
)


class Speciality(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Symptom(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        

class Location(models.Model):
    city = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="India")
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.address

    class Admin:
        list_display = ('city','country')


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    location = models.OneToOneField(Location,on_delete = models.CASCADE )

    def __str__(self):
        return self.name

    class Admin:
        list_display = (
            'name',
            'phone',
            'location'
        )


class Profile(models.Model):
    GENDER = (
        ('M', "Male"),
        ('F', "Female"),
    )

    @staticmethod
    def to_gender(key):
        for item in Profile.GENDER:
            if item[0]==key:
                return item[1]
        return "None"

    firstname = models.CharField(blank=True, max_length=50)
    lastname = models.CharField(blank=True, max_length=50)
    sex = models.CharField(blank=True, max_length=1, choices=GENDER)
    birthday = models.DateField(default=date(1000, 1, 1))
    phone = models.CharField(blank=True, max_length=10)
    allergies = models.CharField(blank=True, max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    prefHospital = models.ForeignKey(Hospital, null=True, related_name="profile_prefhospital", on_delete = models.CASCADE)
    primaryCareDoctor = models.ForeignKey('Account', null=True, related_name="profile_primarycaredoctor", on_delete = models.CASCADE)
    speciality = models.ForeignKey('Speciality', null=True, max_length=250, on_delete = models.CASCADE)

    def get_populated_fields(self):
        """To collect form data"""
        fields = {}
        if self.firstname is not None:
            fields['firstname'] = self.firstname
        if self.lastname is not None:
            fields['lastname'] = self.lastname
        if self.sex is not None:
            fields['sex'] = self.sex
        if not self.birthday.year == 1000:
            fields['birthday'] = self.birthday
        if self.phone is not None:
            fields['phone'] = self.phone
        if self.allergies is not None:
            fields['allergies'] = self.allergies
        if self.prefHospital is not None:
            fields['prefHospital'] = self.prefHospital
        if self.primaryCareDoctor is not None:
            fields['primaryCareDoctor'] = self.primaryCareDoctor
        if self.speciality is not None:
            fields['speciality'] = self.speciality
        return fields

    def __str__(self):
        return self.firstname + " " + self.lastname


class Account(models.Model):
    ACCOUNT_UNKNOWN = 0
    ACCOUNT_PATIENT = 10
    ACCOUNT_DOCTOR = 20
    ACCOUNT_ADMIN = 30
    ACCOUNT_LAB = 40
    ACCOUNT_CHEMIST = 50
    ACCOUNT_NURSE = 60
    ACCOUNT_TYPES = (
        (ACCOUNT_UNKNOWN, "Unknown"),
        (ACCOUNT_PATIENT, "Patient"),
        (ACCOUNT_DOCTOR, "Doctor"),
        (ACCOUNT_ADMIN, "Admin"),
        (ACCOUNT_LAB, "Lab"),
        (ACCOUNT_CHEMIST, "Chemist"),
        (ACCOUNT_NURSE, "Nurse"),
    )
    EMPLOYEE_TYPES = (
        (ACCOUNT_DOCTOR, "Doctor"),
        (ACCOUNT_ADMIN, "Admin"),
        (ACCOUNT_LAB, "Lab"),
        (ACCOUNT_CHEMIST, "Chemist"),
        (ACCOUNT_NURSE, "Nurse"),
    )

    @staticmethod
    def to_name(key):
        """
        Parses an integer value to a string representing an account role.
        :param key: The account role as a int
        :return: The string representation of the name for action
        """
        for item in Account.ACCOUNT_TYPES:
            if item[0]==key:
                return item[1]
        return "None"

    @staticmethod
    def to_value(key):
        """
        Parses an string to a integer representing an account role.
        :param key: The account role as a string
        :return: The integer representation of the account role
        """
        key = key.lower()
        for item in Account.ACCOUNT_TYPES:
            if item[1].lower() == key:
                return item[0]
        return 0

    role = models.IntegerField(default=0, choices=ACCOUNT_TYPES)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    employment_status = models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Pending'), (3, 'Deactivated')], default=1)
    marital_status = models.CharField(max_length=30, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)
    emergency_contact_address = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.role == 20:
            return "Dr. " + self.profile.__str__()
        else:
            return self.profile.__str__()

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'role': self.role,
            'address': self.address,
            'employment_status': self.employment_status,
            'marital_status': self.marital_status,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_email': self.emergency_contact_email,
            'emergency_contact_address': self.emergency_contact_address,
        }
        return fields

    class Admin:
        list_display = (
            'role',
            'profile',
            'user',
            'archive'
        )


class Action(models.Model):
    ACTION_NONE = 0
    ACTION_ACCOUNT = 1
    ACTION_PATIENT = 2
    ACTION_ADMIN = 3
    ACTION_APPOINTMENT = 4
    ACTION_MEDTEST = 5
    ACTION_PRESCRIPTION = 6
    ACTION_MESSAGE = 7
    ACTION_MEDICALINFO = 8
    ACTION_LAB = 9
    ACTION_TYPES = (
        (ACTION_NONE, "None"),
        (ACTION_ACCOUNT, "Account"),
        (ACTION_PATIENT, "Patient"),
        (ACTION_ADMIN, "Admin"),
        (ACTION_APPOINTMENT, "Appointment"),
        (ACTION_MEDTEST, "Medical Test"),
        (ACTION_PRESCRIPTION, "Prescription"),
        (ACTION_MESSAGE,"Message"),
        (ACTION_MEDICALINFO, "Medical Info"),
        (ACTION_LAB, "Lab"),
    )

    @staticmethod
    def to_name(key):
        """
        Parses an integer value to a string representing an action.
        :param key: The action number
        :return: The string representation of the name for action
        """
        for item in Action.ACTION_TYPES:
            if item[0] == key:
                return item[1]
        return "None"

    @staticmethod
    def to_value(key):
        """
         Parses an string to a integer representing an account role.
        :param key: The account role as a string
        :return: The integer representation of the account role
        """
        key = key.lower()
        for item in Action.ACTION_TYPES:
            if item[1].lower() == key:
                return item[0]
        return 0

    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    timePerformed = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)
    account = models.ForeignKey(Account, related_name="actions_account",on_delete = models.CASCADE)


class Appointment(models.Model):
    doctor = models.ForeignKey(Account, related_name="appointment_doctor",on_delete = models.CASCADE)
    patient = models.ForeignKey(Account, related_name="appointment_patient",on_delete = models.CASCADE)
    description = models.CharField(max_length=200)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Active")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    appointment_type = models.CharField(max_length=20, default="Offline")
    meeting_link = models.CharField(max_length=200, null=True, blank=True)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()

    def get_populated_fields(self):
        """used to collect form data"""
        fields = {
            'doctor': self.doctor,
            'patient': self.patient,
            'symptom': self.symptom,
            'description': self.description,
            'hospital': self.hospital,
            'appointment_type': self.appointment_type,
            'startTime': self.startTime,
            'endTime': self.endTime,
        }
        return fields


class Message(models.Model):
    target = models.ForeignKey(Account, related_name="message_target",on_delete= models.CASCADE)
    sender = models.ForeignKey(Account, related_name="message_sender", on_delete= models.CASCADE)
    header = models.CharField(max_length=300)
    body = models.CharField(max_length=1000)
    sender_deleted = models.BooleanField(default=False)
    target_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    account = models.ForeignKey(Account, related_name="notifications_account",on_delete= models.CASCADE)
    message = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    read_timestamp = models.DateTimeField(blank=True, null=True)


class Prescription(models.Model):
    patient = models.ForeignKey(Account, related_name="prescription_patient",on_delete = models.CASCADE)
    doctor = models.ForeignKey(Account, related_name="prescription_doctor",on_delete = models.CASCADE)
    date = models.DateField()
    medication = models.CharField(max_length=100)
    strength = models.CharField(max_length=30)
    instruction = models.CharField(max_length=200)
    refill = models.IntegerField()
    active = models.BooleanField(default=True)

    def get_populated_fields(self):
        """used to collect form data"""
        fields = {
            'patient': self.patient,
            'doctor': self.doctor,
            'date': self.date,
            'medication': self.medication,
            'strength': self.strength,
            'instruction': self.instruction,
            'refill': self.refill,
            'active': self.active,
        }
        return fields


class MedicalInfo(models.Model):
    BLOOD = (
        ('A+', ('A+ Type')),
        ('B+', ('B+ Type')),
        ('AB+', ('AB+ Type')),
        ('O+', ('O+ Type')),
        ('A-', ('A- Type')),
        ('B-', ('B- Type')),
        ('AB-', ('AB- Type')),
        ('O-', ('O- Type')),
    )

    @staticmethod
    def to_blood(key):
        for item in MedicalInfo.BLOOD:
            if item[0] == key:
                return item[1]
        return "None"

    account = models.ForeignKey(Account, related_name="medicalinfo_account",on_delete = models.CASCADE)
    bloodType = models.CharField(max_length=10, choices=BLOOD)
    allergy = models.CharField(max_length=100)
    alzheimer = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    stroke = models.BooleanField(default=False)
    comments = models.CharField(max_length=700)

    def get_populated_fields(self):
        fields = {
            'account':self.account.pk,
            'bloodType':self.bloodType,
            'allergy':self.allergy,
            'alzheimer': self.alzheimer,
            'asthma': self.asthma,
            'diabetes': self.diabetes,
            'stroke': self.stroke,
            'comments': self.comments,
        }
        return fields


class MedicalTest(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    hospital = models.ForeignKey(Hospital,on_delete = models.CASCADE)
    description = models.CharField(max_length=200)
    doctor = models.ForeignKey(Account, related_name="medicaltest_doctor", on_delete = models.CASCADE)
    patient = models.ForeignKey(Account, related_name="medicaltest_patient", on_delete = models.CASCADE)
    private = models.BooleanField(default=True)
    completed = models.BooleanField()
    image1 = models.FileField(blank=True, null=True, upload_to='medicaltests/%Y/%m/%d')
    image2 = models.FileField(blank=True, null=True, upload_to='medicaltests/%Y/%m/%d')
    image3 = models.FileField(blank=True, null=True, upload_to='medicaltests/%Y/%m/%d')
    image4 = models.FileField(blank=True, null=True, upload_to='medicaltests/%Y/%m/%d')
    image5 = models.FileField(blank=True, null=True, upload_to='medicaltests/%Y/%m/%d')

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'name': self.name,
            'date': self.date,
            'hospital': self.hospital,
            'description': self.description,
            'doctor': self.doctor,
            'patient': self.patient,
            'private': self.private,
            'completed': self.completed,
            'image1': self.image1,
            'image2': self.image2,
            'image3': self.image3,
            'image4': self.image4,
            'image5': self.image5,
        }
        return fields


class Statistics(models.Model):
    startDate = models.DateField()
    endDate = models.DateField()

    def get_populated_fields(self):
        """to collect form data"""
        fields = {
            'startDate':self.startDate,
            'endDate':self.endDate,
        }
        return fields


class Diagnosis(models.Model):
    diagnosis_patient = models.ForeignKey(Account, related_name="diagnosis_patient", on_delete=models.CASCADE)
    condition = models.CharField(max_length=100)
    diagnosis_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.diagnosis_patient.__str__() + " - " + self.condition)

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'diagnosis_patient': self.diagnosis_patient,
            'diagnosis_date': self.diagnosis_date,
            'condition': self.condition,
            'notes': self.notes,
        }
        return fields


"""
HRM Models 
"""


class LeaveRequest(models.Model):
    LEAVE_CHOICES = [
        (1,"Annual Leave/Vacation Leave"),
        (2,"Sick Leave"),
        (3,"Maternity Leave"),
        (4,"Paternity Leave"),
        (5,"Parental Leave"),
        (6,"Bereavement Leave"),
        (7,"Personal Leave"),
        (8,"Compensatory Leave"),
        (9,"Public Holidays"),
        (10,"Special Leave"),
        (11,"Sabbatical Leave"),
        (12,"Unpaid Leave"),
        (13,"Family and Medical Leave Act (FMLA) Leave")
    ]

    employee = models.ForeignKey(Account, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    type_of_leave = models.PositiveIntegerField(default=5, choices=LEAVE_CHOICES)
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')])

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'employee': self.employee,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'reason': self.reason,
            'type_of_leave': self.type_of_leave,
            'status': self.status,
        }
        return fields

    def clean(self):
        if self.start_date > self.end_date:
            return True


class Payroll(models.Model):
    PAY_CHOICES = [
        (1, "Monthly"),
        (2, "Bi-Weekly"),
        (3, "Weekly"),
        (4, "Semi-Monthly"),
        (5, "Hourly Wage"),
        (6, "Commission"),
        (7, "Contract/Project-Based"),
        (8, "Annual"),
    ]
    employee = models.OneToOneField(Account, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    pay_type = models.PositiveIntegerField(default=1, choices=PAY_CHOICES)

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'employee': self.employee,
            'salary': self.salary,
            'pay_type': self.pay_type,
        }
        return fields


class PerformanceReview(models.Model):
    employee = models.ForeignKey(Account, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='reviews_given')
    review_date = models.DateField()
    feedback = models.TextField()
    rating = models.PositiveIntegerField(choices=[(1, 'Poor'), (2, 'Average'), (3, 'Good'), (4, 'Excellent'), (5, 'Outstanding')])

    def get_populated_fields(self):
        """To collect form data"""
        fields = {
            'employee': self.employee,
            'reviewer': self.reviewer,
            'review_date': self.review_date,
            'feedback': self.feedback,
            'rating': self.rating,
        }
        return fields

# class Attendance(models.Model):
#     employee = models.ForeignKey(Account, on_delete=models.CASCADE)
#     date = models.DateField()
#     status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])
