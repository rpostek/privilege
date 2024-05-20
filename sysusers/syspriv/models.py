import logging
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template


class System(models.Model):
    db_type_choices = [
        ('fb', 'Firebird'),
        ('MS', 'MS SQL Server'),
        ('PS', "Powershell"),
        ('CS', 'CSV file'),
        ('YA', 'yaml file'),
    ]
    display_name = models.CharField(max_length=60)
    server_name = models.CharField(max_length=60, null=True)
    database = models.CharField(max_length=60, null=True)
    login = models.CharField(max_length=30, null=True)
    password = models.CharField(max_length=30)
    port = models.CharField(max_length=6, null=True)
    db_type = models.CharField(choices=db_type_choices, null=False, max_length=8)
    sql_query_roles = models.TextField()
    sql_query_accounts = models.TextField()
    sql_query_accounts_roles = models.TextField()
    update_time = models.DateTimeField(null=True)
    description = models.TextField(max_length=500, blank=True, default='')

    class Meta:
        ordering = ["display_name",]

    def __str__(self):
        return self.display_name

    def query_system(self):
        from .datasources.base import get_datasource

        ds = get_datasource(self)
        try:
            ds.load_data()
            self.update_time = timezone.now()
            self.save()
            return True
        except Exception as e:
            logging.error(e)
            return False


class Role(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    internal_id = models.CharField(max_length=40)
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=500)
    def __str__(self):
        return self.system.display_name + ': ' + self.name

    class Meta:
        ordering = ["system", "name"]


class AdPerson(models.Model):
    login = models.CharField(max_length=30, default='b.d.') #SamAccountName
    full_name = models.CharField(max_length=40) #Name
    first_name = models.CharField(max_length=30) #GivenName
    last_name = models.CharField(max_length=40) #Surname
    title = models.CharField(max_length=60, null=False, default='b.d.') #Title
    department = models.CharField(max_length=80, default='b.d.') #Department (wydział)
    office = models.CharField(max_length=80, null=False, default='b.d.') #Office (biuro/dzielnica)
    manager = models.CharField(max_length=100, default='b.d.') #Manager
    emailaddress = models.CharField(max_length=50, default='b.d.') #emailaddress

    def __str__(self):
        return self.full_name

    @classmethod
    def logged_aduser(cls, user):
        try:
            return AdPerson.objects.get(login__iexact=user.username)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def people_from_department(cls, user):
        try:
            user_ad = cls.logged_aduser(user)
            return cls.objects.filter(department=user_ad.department, office=user_ad.office)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def people_allowed_for_user(cls, user):
        if user.groups.filter(name='master').exists():
            return cls.objects.all()
        else:
            return cls.people_from_department(user)


    class Meta:
        ordering = ["last_name", "first_name"]

class Account(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    internal_id = models.CharField(max_length=40)
    login = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    roles = models.ManyToManyField(Role, related_name='accounts')
    adperson = models.ForeignKey(AdPerson, null=True, on_delete=models.SET_NULL)
    @property
    def full_name(self):
        return self.last_name + ' ' + self.first_name

    def __str__(self):
        return self.system.display_name + ': ' + self.login

    class Meta:
        ordering = ["last_name", "first_name"]

class Department(models.Model):
    name = models.CharField(max_length=80, default='b.d.')
    office = models.CharField(max_length=80, null=False, default='b.d.')
    systems = models.ManyToManyField(System)

    class Meta:
        ordering = ["office", "name",]

    def __str__(self):
        return self.office + ': ' + self.name


class Commission(models.Model):
    display_id = models.IntegerField(default = 10000)
    manager_first_name = models.CharField(max_length=30)
    manager_last_name = models.CharField(max_length=40)
    person_first_name = models.CharField(max_length=30)
    person_last_name = models.CharField(max_length=40, verbose_name='nazwisko użytkownika')
    request_time = models.DateTimeField(null=False)
    accept_time = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["display_id",]

    def commision_html(self):
        t = Template('''
    <html>
      <head></head>
      <body>
      Proszę o akceptację wniosku numer {{ object.display_id|stringformat:"05d" }} o zmianę uprawnień dla <b>{{ object.person_first_name}} {{ object.person_last_name}}</b>.<br>
    Wnioskujący: {{object.manager_first_name}} {{object.manager_last_name}}<br> 
    Data utworzenia wniosku: {{object.request_time|date:"Y-m-d H:i"}}<br>
<table style="border: 1px solid black;">
<tr style="text-align:center;"><th>system</th><th>uprawnienie</th><th>status</th></tr>
    {% for d in object.commission_role_set.all %}
    {% cycle '100%' '95%' as brightness silent %}
    <tr style="border: 1px solid black; background-color: white; filter: brightness({{ brightness }});">
    {% if d.status == "-" %}
        <td style="text-decoration: line-through; padding-right: 5px; padding-left: 5px;">{{ d.system_name }}</td>
        <td style="text-decoration: line-through; padding-right: 5px; padding-left: 5px;">{{ d.role_name }}</td>
        <td style="background-color: #FFF0F0; padding-right: 5px; padding-left: 5px;">zabrane</td>
     {% elif d.status == "+" %}
        <td style="font-weight: bold; padding-right: 5px; padding-left: 5px;">{{ d.system_name }}</td>
        <td style="font-weight: bold; padding-right: 5px; padding-left: 5px;">{{ d.role_name }}</td>
        <td style="background-color: #F0FFF0; padding-right: 5px; padding-left: 5px;">dodane</td>
    {% else %}
        <td style="padding-right: 5px; padding-left: 5px;">{{ d.system_name }}</td>
        <td style="padding-right: 5px; padding-left: 5px;">{{ d.role_name }}</td>
        <td style="padding-right: 5px; padding-left: 5px;">b.z.</td>
    {% endif %}
    </tr>
    {% endfor %}
</table>
</body>
</html>
''')
        c = Context({"object": self})
        return t.render(c)

class Commission_role(models.Model):
    ROLE_STATUS = [
        ('+', 'dodane'),
        ('-', 'usunięte'),
        ('=', 'bez zmian')
    ]
    system_name = models.CharField(max_length=60)
    role_name = models.CharField(max_length=60)
    role_internal_id = models.CharField(max_length=40)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    status = models.CharField(default='=', choices=ROLE_STATUS, max_length=2)

    class Meta:
        ordering = ["system_name","role_name"]


class AdContainer(models.Model):
    # tabela przechowująca stringi z OU do zapytań w AD o użytkowników z wybranych wydziałów
    name = models.CharField(max_length=100)
    string = models.TextField(max_length=500)

class AdUser(models.Model):
    ROLE = [
        ('M', 'master'),
        ('S', 'standard'),
    ]
    login = models.CharField(max_length=30) #SamAccountName
    first_name = models.CharField(max_length=30) #GivenName
    last_name = models.CharField(max_length=40) #Surname
    status = models.CharField(default='S', choices=ROLE, max_length=2)

class Config(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.key + ': ' + self.value
