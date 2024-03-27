from .base import DatasourceBase
from ..models import Role, Account
import yaml

class YamlDatasource(DatasourceBase):
    def get_identifier(self):
        return "YA"

    def load_data(self):
        Role.objects.filter(system=self.system).delete()
        Account.objects.filter(system=self.system).delete()
        with open(self.system.sql_query_accounts_roles, 'r', encoding='utf-8') as file:
            yml_data = yaml.safe_load(file)
            for yml_role in yml_data['roles']:
                r = Role(system=self.system, internal_id=yml_role['role'][:40], name=yml_role['role'], description=yml_role['description'])
                r.save()
                for yml_account in yml_role['users']:
                    yml_account_id = yml_account.get('login', yml_account['first_name'][:4] + yml_account['last_name'][:14])
                    if not Account.objects.filter(system=self.system, internal_id=yml_account_id).exists():
                        u = Account(system=self.system, internal_id=yml_account_id, login=yml_account_id,
                                    first_name=yml_account['first_name'], last_name=yml_account['last_name'])
                        u.save()
                    else:
                        u = Account.objects.get(system=self.system, internal_id=yml_account_id)
                    u.roles.add(r)
                    u.save()
