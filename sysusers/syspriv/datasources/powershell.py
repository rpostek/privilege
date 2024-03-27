import json
import subprocess
from ..datasources.base import DatasourceBase
from ..models import Role, Account


class PowershellDatasource(DatasourceBase):
    def get_identifier(self):
        return "PS"

    def load_data(self):
        ps = subprocess.Popen(["powershell", "-Command", self.system.sql_query_roles],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        data, errs = ps.communicate(timeout=120)
        data_str = data.decode(encoding='cp852')
        data = json.loads(data_str)
        Role.objects.filter(system=self.system).delete()
        for row in data:
            role = Role(system=self.system, internal_id=row['SamAccountName'], name=row['Name'], description=row['Description'] if row['Description'] else '')
            role.save()
        # get accounts
        ps = subprocess.Popen(["powershell", "-Command", self.system.sql_query_accounts],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        data, errs = ps.communicate(timeout=120)
        data_str = data.decode(encoding='cp852')
        data = json.loads(data_str)
        Account.objects.filter(system=self.system).delete()
        for row in data:
            #first_name, last_name = row['Name'].rsplit(' ', 1)[-1], row['Name'].rsplit(' ', 1)[0]
            account = Account(system=self.system, internal_id=row['SamAccountName'],
                           login=row['SamAccountName'],
                           first_name=row['GivenName'] if row['GivenName'] else row['SamAccountName'],
                           last_name=row['Surname'] if row['Surname'] else ''
                           )
            account.save()
        #get accounts-roles
        ps = subprocess.Popen(["powershell", "-Command", self.system.sql_query_accounts_roles],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        data, errs = ps.communicate(timeout=120)
        data_str = data.decode(encoding='cp852')
        data = json.loads(data_str)
        for account in Account.objects.filter(system=self.system):
            account.roles.clear()
            account.save()
        for row in data:
            try:
                account = Account.objects.get(system=self.system, internal_id=row['User'])
                account.roles.add(Role.objects.get(system=self.system, internal_id=row['Role']))
                account.save()
            except:
                pass
