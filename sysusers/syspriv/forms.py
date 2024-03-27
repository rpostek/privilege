from django import forms
from .models import System, AdPerson, Account, Role, Department
from django.core.exceptions import ObjectDoesNotExist



class SystemsSelectForm(forms.Form):
    systems = forms.ModelMultipleChoiceField(queryset=System.objects.all().order_by('display_name'),widget=forms.CheckboxSelectMultiple, required=False)

class PersonSelectForm(forms.Form):
    people_who_are_users = Account.objects.values_list('adperson', flat=True).distinct()
    # tabela Adperson ma sporo więcej osób niż użytkownicy systemów
    person = forms.ModelChoiceField(queryset=AdPerson.objects.filter(id__in=people_who_are_users))

class SystemPasswordForm(forms.ModelForm):
    class Meta:
        model = System
        widgets = {
            'password': forms.PasswordInput(),
        }
        fields = ['display_name', 'description', 'server_name', 'database', 'login', 'password', 'port', 'db_type', 'sql_query_roles',
                  'sql_query_accounts', 'sql_query_accounts_roles', 'update_time']



class SystemSelectForm(forms.Form):
    system = forms.ModelChoiceField(queryset=System.objects.all().order_by('display_name'), required=False)


class CommissionCreateForm1(forms.Form):
    person = forms.ModelChoiceField(queryset=AdPerson.objects.all(), required=True, label_suffix=None, label='pracownik')
    auto_id = False
    #def __init__(self, *args, **kwargs):
    #    super(CommissionCreateForm1, self).__init__(*args, **kwargs)
    #    self.fields['person'].queryset = AdPerson.objects.none()


class CommissionCreateForm2(forms.Form):
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), required=False, widget=forms.CheckboxSelectMultiple(attrs={'use_fieldset': False}))
    auto_id = False

class CommissionCreateForm3(forms.Form):
    _ = forms.CharField(widget=forms.HiddenInput(), required=False)
