import django_filters
from django.views import View
from django.views.generic import FormView, ListView, TemplateView, DetailView
from . import models
from .forms import SystemsSelectForm, PersonSelectForm, SystemSelectForm, CommissionCreateForm1, CommissionCreateForm2, CommissionCreateForm3
from django.db.models.functions import Lower
from django.db.models import Count
from django.shortcuts import render, redirect
from .datasources.ad import AdDatasource
from formtools.wizard.views import SessionWizardView
from django.utils import timezone
from django.db.models import Max
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from .auth.auth import get_logged_ad_user, DomainBackend
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

class NotAllowed(Exception):
    pass


class HomeView(View):
    def get(self, request):
        print('home page')
        data = {}
        try:
            username = get_logged_ad_user(request)
            #ad_logged_user = models.AdPerson.objects.get(login__iexact=request.user.username)
            ad_logged_user = models.AdPerson.objects.get(login__iexact=username)
            data.update({'ad_user_raw': str(username)})
            data.update({'ad_user': ad_logged_user})
            data.update({'systems_allowed': models.Department.objects.get(name=ad_logged_user.department).systems.all()})
        except ObjectDoesNotExist:
            pass
        data.update({'groups': request.user.groups.values_list('name', flat=True)})
        return render(request, "syspriv/home.html", data)


@login_required
def get_systems(request):
    if request.user.groups.filter(name='master').exists():
        data = models.System.objects.all().order_by('display_name')
        if request.method == "POST":
            form = SystemsSelectForm(request.POST)
            if form.is_valid():
                if 'AD' in request.POST:
                    alerts = AdDatasource.get_ad_persons()
                else:
                    alerts = []
                    for s in form.cleaned_data['systems']:
                        result = s.query_system()
                        if not result:
                            alerts.append({'type': 'danger', 'text':f'aktualizacja danych z systemu <b>{s.display_name}</b> nie powiodła się'})
                        else:
                            alerts.append({'type': 'primary', 'text':f'aktualizacja danych z systemu <b>{s.display_name}</b> zakończona pomyślnie'})
                    update_ad_person()
                return render(request, "syspriv/systems_select.html", {"form": form, 'systems': data, 'alerts': alerts})
        else:
            form = SystemsSelectForm()
        return render(request, "syspriv/systems_select.html", {"form": form, 'systems': data})
    else:
        return redirect('home')
@method_decorator(login_required, name='dispatch')
class SystemListView(View):
    def get(self, request):
        return render(request, 'syspriv/system_list.html', {'systems': models.System.objects.all()})

@method_decorator(login_required, name='dispatch')
class SystemDetailView(View):
    def get(self, request, id):
        system = models.System.objects.get(id=id)
        roles = models.Role.objects.filter(system=system).prefetch_related("accounts").annotate(no_of_users=Count('accounts')).order_by(Lower('name')).all()
        roles_assigned = []  # insert tuple of role and list of users
        for role in roles:
            accounts = role.accounts.order_by('adperson__full_name').all()
            if len(accounts):
                roles_assigned.append((role, accounts))
        return render(request, template_name='syspriv/system_detail.html', context={'system': system, 'roles':roles})




@method_decorator(login_required, name='dispatch')
class SystemPeopleView(View):
    def get(self, request, id):
        system = models.System.objects.get(id=id)
        roles = models.Role.objects.filter(system=system).prefetch_related("accounts").all()
        roles_assigned = []  # insert tuple of role and list of users
        if request.user.groups.filter(name='master').exists():
            filter = {}
        else:
            try:
                ad_logged_user = models.AdPerson.objects.get(login__iexact=request.user.username)
                ad_logged_users_department = models.Department.objects.get(name=ad_logged_user.department, office=ad_logged_user.office)
                if system in ad_logged_users_department.systems.all():
                    filter = {}
                else:
                    filter = {'adperson__department': ad_logged_user.department, 'adperson__office':ad_logged_user.office}
            except ObjectDoesNotExist:
                filter = { 'adperson__department': '---!!!---'}  #użytkownika nie dao się zapować na adperson, więc niech filtr usunie wszystkie obiekty
        for role in roles:
            accounts = role.accounts.filter(**filter)
            if len(accounts):
                roles_assigned.append((role, accounts))
        return render(
            self.request,
            "syspriv/system_select_3.html",
            {
                'system': system,
                'roles': roles_assigned,
            }
        )


@method_decorator(login_required, name='dispatch')
class PersonListView(View):
    def get(self, request):
        people_who_are_users = models.Account.objects.values_list('adperson', flat=True).distinct()
        # tabela Adperson ma sporo więcej osób niż użytkownicy systemów
        people = models.AdPerson.people_allowed_for_user(request.user).filter(id__in=people_who_are_users)
        return render(request, "syspriv/people_list.html", {'people': people})

@method_decorator(login_required, name='dispatch')
class PersonDetailView(View):
    def get(self, request, id):
        try:
            adperson = models.AdPerson.objects.get(id=id)
        except ObjectDoesNotExist:
            adperson = None
        data = []
        if adperson in models.AdPerson.people_allowed_for_user(request.user):
            systems = models.System.objects.filter(role__accounts__adperson=adperson).distinct()
            logins = models.Account.objects.filter(adperson=adperson)
            for system in systems:
                roles = models.Role.objects.filter(system=system).filter(accounts__in=logins)
                data.append({'system': system, 'roles':roles})
        else:
            adperson = None
        return render(request, "syspriv/person_detail.html", {'systems': data, 'selected_user': adperson})

@method_decorator(login_required, name='dispatch')
class DeaprtmentListView(View):
    def get(self, request):
        query = []
        try:
            if request.user.groups.filter(name='master').exists():
                query = models.Department.objects.all()
            else:
                ad_logged_user = models.AdPerson.objects.get(login__iexact=request.user.username)
                query = models.Department.objects.filter(name=ad_logged_user.department, office=ad_logged_user.office)
        except ObjectDoesNotExist:
            pass
        return render(self.request, 'syspriv/department_list.html', {'departments': query})


@method_decorator(login_required, name='dispatch')
class DeaprtmentDetailView(View):
    def get(self, request, id):
        data = {}
        department = models.Department.objects.get(id=id)
        try:
            if not request.user.groups.filter(name='master').exists():
                ad_logged_user = models.AdPerson.objects.get(login__iexact=request.user.username)
                users_department = models.Department.objects.filter(name=ad_logged_user.department, office=ad_logged_user.office).first()
                if users_department != department:
                    raise(NotAllowed)
            data['department'] = department.name
            dept_users = models.Account.objects.filter(adperson__department=department.name, adperson__office=department.office)
            systems = models.System.objects.filter(account__in=dept_users).distinct()
            data['systems'] = []
            for system in systems:
                roles = []
                for role in models.Role.objects.filter(system=system, accounts__in=dept_users).distinct():
                    uu = dept_users.filter(roles=role)
                    roles.append({'role': role, 'users': uu})
                data['systems'].append({'system':system, 'roles': roles})
        except (NotAllowed, ObjectDoesNotExist):
            data = {}
        return render(self.request, 'syspriv/department_list_roles.html', data)

@method_decorator(login_required, name='dispatch')
class SummaryView(View):
    def get(self, request):
        data = {}
        try:
            if request.user.groups.filter(name='master').exists():
                data['department'] = "Wszystkie wydziały"
                systems = models.System.objects.all().distinct()
                data['systems'] = []
                for system in systems:
                    roles = []
                    for role in models.Role.objects.filter(system=system).distinct():
                        #uu = models.Account.objects.filter(roles=role)
                        uu = models.AdPerson.objects.filter(account__roles=role).exclude(login__exact='brak')
                        # zostawiam tylko użytkowników domenowych
                        if uu:
                            roles.append({'role': role, 'users': uu})
                    data['systems'].append({'system':system, 'roles': roles})
        except (NotAllowed, ObjectDoesNotExist):
            data = {}
        return render(self.request, 'syspriv/summary_list_roles.html', data)



def update_ad_person():
    # osobom z User przypisuje po imieniu i nazwisku osoby w AdPerson
    # ewentualnie dodaje nowe osoby do AdPerson (jak ich brak)
    # aktualizuje Department
    for user in models.Account.objects.all():
        if not models.AdPerson.objects.filter(first_name__iexact=user.first_name.lower(), last_name__iexact=user.last_name.lower()).exists():
            new_person = models.AdPerson(login='brak',
                                         full_name=user.full_name,
                                         first_name=user.first_name,
                                         last_name=user.last_name,
                                         title='brak',
                                         )
            new_person.save()
        user.adperson = models.AdPerson.objects.get(first_name__iexact=user.first_name.lower(), last_name__iexact=user.last_name.lower())
        user.save()
    #models.Department.objects.all().delete()
    people_who_are_users = models.Account.objects.values_list('adperson', flat=True).distinct()
    dd = models.AdPerson.objects.filter(id__in=people_who_are_users).order_by().values('office','department').distinct('office','department')
    for department_name in dd:
        if not models.Department.objects.filter(name__exact=department_name['department'], office__exact=department_name['office']).exists():
            d = models.Department(name=department_name['department'], office=department_name['office'])
            d.save()
#@method_decorator(login_required, name='dispatch')
class CommissionCreateView(SessionWizardView):
    TEMPLATES = {'0': 'syspriv/commission_create0.html', '1': 'syspriv/commission_create1.html','2': 'syspriv/commission_create2.html'}
    form_list = [CommissionCreateForm1, CommissionCreateForm2, CommissionCreateForm3]

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            if self.request.user.groups.filter(name='master').exists():
                sq = models.AdPerson.objects.all().exclude(login__exact='brak')
            else:
                try:
                    ad_logged_user = models.AdPerson.objects.get(login__iexact=self.request.user.username)
                    sq = models.AdPerson.objects.filter(department=ad_logged_user.department, office=ad_logged_user.office)
                except:
                    sq = models.AdPerson.objects.none()
            form.fields['person'].choices = ((choice.pk, choice) for choice in sq)
        return form



    def done(self, form_list, **kwargs):
        try:
            ad_logged_user = models.AdPerson.objects.get(login__iexact=self.request.user.username)
        except ObjectDoesNotExist :
            alerts = [{'type': 'danger', 'text': 'Zlecający nie jest zalogowany kontem domenowym. Wniosek nie został utworzony '}, ]
            return render(self.request, 'syspriv/home.html',
                          {'alerts': alerts})
        data = self.get_all_cleaned_data()
        commission = models.Commission()
        cm_id_next = models.Commission.objects.aggregate(Max('display_id', default = 0))
        commission.display_id = cm_id_next['display_id__max'] + 1
        commission.manager_first_name = ad_logged_user.first_name
        commission.manager_last_name = ad_logged_user.last_name
        commission.person_first_name = data['person'].first_name
        commission.person_last_name = data['person'].last_name
        commission.request_time = timezone.now()
        commission.save()
        for r in data['roles']:
            com_role = models.Commission_role()
            com_role.system_name = r.system.display_name
            com_role.role_name = r.name
            com_role.role_internal_id = r.internal_id
            com_role.status = '+' if r.id in self.storage.extra_data['roles_add'] else '='
            com_role.commission = commission
            com_role.save()
        for r_id in self.storage.extra_data['roles_remove']:
            r = models.Role.objects.get(id=r_id)
            com_role = models.Commission_role()
            com_role.system_name = r.system.display_name
            com_role.role_name = r.name
            com_role.role_internal_id = r.internal_id
            com_role.status = '-'
            com_role.commission = commission
            com_role.save()

        alerts = [{'type': 'primary', 'text': 'wniosek o zmianę uprawnień został utworzony'},]
        return render(self.request, 'syspriv/done.html', {'form_data': [form.cleaned_data for form in form_list], 'alerts': alerts})

    def get_form_initial(self, step):
        initials = self.initial_dict.get(step, {})
        if step == '0' and self.storage.current_step == '0' and '1' in self.storage.data['step_data']:
            self.storage.set_step_data('1', None)
        elif step == '1' and self.storage.current_step == '0':
            # przejście z kroku '0' do '1' nie występuje przy cofnięciu z kroku '2'
            # ew. warunek self.storage.data.step_data['1'] (nie testowane)
            a = self.get_cleaned_data_for_step('0')
            logins = models.Account.objects.filter(adperson=a['person'])
            roles = models.Role.objects.filter(accounts__in=logins)
            initials.update({'roles': roles})
        elif step == '1' and self.storage.current_step == '1' and '1' in self.storage.data['step_data']:
            try:
                roles_id = self.storage.data['step_data']['1']['1-roles']
            except (TypeError, KeyError):
                roles_id = []
            roles = models.Role.objects.filter(id__in=roles_id)
            initials.update({'roles': roles})
        return initials


    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == '2':
            new_roles_set = self.get_cleaned_data_for_step('1')['roles']
            person_selected = self.get_cleaned_data_for_step('0')['person']
            logins = models.Account.objects.filter(adperson=person_selected)
            old_roles_set = models.Role.objects.filter(accounts__in=logins)
            roles_add = [i for i in new_roles_set if i not in old_roles_set]
            roles_remove = [i for i in old_roles_set if i not in new_roles_set]
            self.storage.extra_data['roles_add'] = [x.id for x in roles_add]
            self.storage.extra_data['roles_remove'] = [x.id for x in roles_remove]
            context.update({'person': person_selected,
                            'roles_add': roles_add,
                            'roles_remove': roles_remove})
        elif self.steps.current == '1':
            context.update({'person': self.get_cleaned_data_for_step('0')['person']})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]


def test_page(request):
    return render(request, 'syspriv/test.html')


class CommissionFilter(django_filters.FilterSet):
    class Meta:
        model = models.Commission
        fields = ['person_first_name','person_last_name']

@method_decorator(login_required, name='dispatch')
class CommissionListView(ListView):
    model = models.Commission
    ordering = ['-display_id']
    paginate_by = 10
    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        if self.request.user.groups.filter(name='master').exists():  # dodane dla zwiekszenia szybkości
            return qs
        allowed_people = ({'person_first_name': p.first_name, 'person_last_name': p.last_name} for p in models.AdPerson.people_allowed_for_user(self.request.user))
        q = models.Commission.objects.none()
        for qk in allowed_people:
            q |= models.Commission.objects.filter(**qk)
        return q.order_by('-display_id')

@method_decorator(login_required, name='dispatch')
class CommissionDetailView(DetailView):
    model = models.Commission
    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        if self.request.user.groups.filter(name='master').exists(): # dodane dla zwiekszenia szybkości
            return qs
        allowed_people = ({'person_first_name': p.first_name, 'person_last_name': p.last_name} for p in models.AdPerson.people_allowed_for_user(self.request.user))
        q = models.Commission.objects.none()
        for qk in allowed_people:
            q |= models.Commission.objects.filter(**qk)
        return q.order_by('-display_id')



class MyLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'syspriv/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))

def login_redirect(request):
    username = get_logged_ad_user(request)
    if username:
        login(request, User.objects.get(username=username))
    return redirect('/syspriv/')

'''def reset(request):
    Session.objects.all().delete()
    return render(request, "syspriv/list_roles2.html", {})
'''
'''class RolesListView(View):
    def get(self, request):
        data = models.System.objects.all().prefetch_related('role_set').order_by('display_name')
        return render(request, "syspriv/list_roles2.html", {'systems': data})
'''

'''class RoleListView(View):
    def get(self, request):
        data = []
        systems = models.System.objects.all().order_by(Lower('display_name'))
        for system in systems:
            roles = models.Role.objects.filter(system=system).all()
            data.append({'system': system, 'roles':roles})
        return render(request, "syspriv/list_roles.html", {'systems': data})
'''

'''
def filter_by_person(adperson):
    users = models.User.objects.filter(adperson=adperson)  # one person can have multiple users
    d = models.User.objects.filter(adperson=adperson).values("roles__system__display_name", "roles__name",
                                                             "roles__description")
    groupped_by_system_name = {}
    for x in d:
        system_name = x['roles__system__display_name']
        if system_name not in groupped_by_system_name:
            groupped_by_system_name[system_name] = []
        groupped_by_system_name[system_name].append(x)
    data = {'systems': []}
    for system in models.System.objects.all():
        data['systems'].append(
            {'system': system,
             'user': users.filter(system=system),
             'roles': models.Role.objects.filter(system=system).filter(users__in=users)})
    data['selected_user'] = adperson
    data['form'] = PersonSelectForm()
    return data


class FilterUserView(FormView):
    form_class = PersonSelectForm
    template_name = 'syspriv/user_select.html'

    def form_valid(self, form):
        adperson = form.cleaned_data['person']
        users = models.User.objects.filter(adperson=adperson)  # one person can have multiple users
        d = models.User.objects.filter(adperson=adperson).values("roles__system__display_name", "roles__name",
                                                             "roles__description")
        groupped_by_system_name = {}
        for x in d:
            system_name = x['roles__system__display_name']
            if system_name not in groupped_by_system_name:
                groupped_by_system_name[system_name] = []
            groupped_by_system_name[system_name].append(x)
        data = {'systems': []}
        for system in models.System.objects.all():
            data['systems'].append(
                {'system': system,
                 'user': users.filter(system=system),
                 'roles': models.Role.objects.filter(system=system).filter(users__in=users)})
        data['selected_user'] = adperson
        data['form'] = PersonSelectForm()
        return render(self.request, "syspriv/user_select.html", data)

'''

'''class FilterSystemView(FormView):
    form_class = SystemSelectForm
    template_name = 'syspriv/system_select.html'

    def form_valid(self, form):
        selected_system = form.cleaned_data['system']
        system = models.System.objects.get(id=selected_system.id)
        roles = models.Role.objects.filter(system=system).prefetch_related("users").all()
        roles_assigned = []  # insert tuple of role and list of users

        for role in roles:
            users = role.users.all()
            if len(users):
                roles_assigned.append((role, users))
        return render(
            self.request,
            "syspriv/system_select_2.html",
            {
                'system': system,
                'roles': roles_assigned,
                'form': form,
            }
        )
'''
