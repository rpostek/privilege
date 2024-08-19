from .. import models
import subprocess
import json
import re
from .. import views
from .. import models

class AdDatasource():
    @classmethod
    def get_ad_persons(request):
        try:
            '''ad_containers = ["OU=Users,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl",
                             "OU=Wesola_BAiSO,OU=Delegatury,OU=Users,OU=Biuro Administracji i Spraw Obywatelskich,OU=Biura,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl",
                             "OU=Wesola_CB,OU=Delegatury,OU=Users,OU=Stoleczne Centrum Bezpieczenstwa,OU=Biura,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl",
                             "OU=Users,OU=Centrum Obslugi Podatnika,OU=Biura,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl",
                             ]
            '''
            ad_containers = models.AdContainer.objects.all()
            models.AdPerson.objects.all().delete()
            for ad_container in ad_containers:
                ps_script = 'Get-ADUser -Filter * -SearchBase "' + ad_container.string + '" -Properties SamAccountName,Name,GivenName,Surname,Title,Department,Office,Manager,emailaddress,OfficePhone,MobilePhone,POBox \
                            | Select-Object -Property SamAccountName,Name,GivenName,Surname,Title,Department,Office,Manager,emailaddress,OfficePhone,MobilePhone,POBox \
                            | convertto-json'
                ps = subprocess.Popen(["powershell", "-Command", ps_script],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                data, errs = ps.communicate(timeout=120)
                data_str = data.decode(encoding='cp852')
                data = json.loads(data_str)
                for row in data:
                    try:
                        _manager = re.search('^CN=([^,]*)', row['Manager']).group(0)
                        _manager = _manager[3:]
                    except:
                        _manager = 'b.d.'
                    if not models.AdPerson.objects.filter(first_name=row['GivenName'], last_name=row['Surname']).exists():
                        if row['GivenName'] and row['Surname']:  # na wypadek specjalnych userów (konsultacje.wesola)
                            person = models.AdPerson(login=row['SamAccountName'],
                                                     full_name=row['Name'],
                                                     first_name=row['GivenName'],
                                                     last_name=row['Surname'],
                                                     title=row['Title'] if row['Title'] else 'b.d.',
                                                     department=row['Department'] if row['Department'] else 'b.d.',
                                                     office=row['Office'] if row['Office'] else 'b.d.',
                                                     manager=_manager,
                                                     emailaddress=row['emailaddress'],
                                                     office_phone=row['OfficePhone'] if row['OfficePhone'] else None,
                                                     mobile_phone=row['MobilePhone'] if row['MobilePhone'] else None,
                                                     room_number=str(row['POBox']) if row['POBox'] else None)
                            person.save()
            views.update_ad_person()
            alerts=[{'type':'primary', 'text':'lista pracowników pomyślnie pobrana z AD'}]
            return alerts
        except Exception as e:
            print(e)
            alerts = [{'type':'danger', 'text':'błąd pobrania z AD listy pracowników'}]
        return alerts
