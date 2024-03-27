from .base import DatasourceBase
from ..models import Role, Account
import csv

class CsvDatasource(DatasourceBase):
    def get_identifier(self):
        return "CS"

    def load_data(self):
        Role.objects.filter(system=self.system).delete()
        Account.objects.filter(system=self.system).delete()
        filename = self.system.sql_query_accounts_roles
        with open(filename, fieldnames=['first_name', 'last_name', 'role', 'description'], newline='', encoding='utf-8') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            for row in datareader:
                first_name = row['first_name']
                last_name = row['last_name']
                role = row['role']
                description = row['description']
                if not Role.objects.filter(internal_id=role).exists():
                    r = Role(system=self.system, internal_id=role, description=description)
                    r.save()
                if not Account.objects.filter(internal_id=first_name + last_name).exists():
                    u = Account(system=self.system, internal_id=first_name + last_name, login=first_name + last_name, first_name=first_name, last_name=last_name)
                    u.save()
                u.roles.add(r)
