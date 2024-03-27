import pyodbc
from .base import DatasourceBase
from ..models import Role, Account


class MsSQLDatasource(DatasourceBase):
    def get_identifier(self):
        return "MS"

    def load_data(self):
        db_string = "Driver={SQL Server Native Client 11.0};" \
                    "Server=" + self.system.server_name + ',' + self.system.port +';' \
                    "Database=" + self.system.database + ';' \
                    "Uid=" + self.system.login + ';' \
                    "Pwd=" + self.system.password + ';'

        with pyodbc.connect(db_string) as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(self.system.sql_query_roles)
            data = cursor.fetchall()
            Role.objects.filter(system=self.system).delete()
            for row in data:
                role = Role(system=self.system, internal_id=row[0], name=row[1], description=row[2])
                role.save()
            # get accounts
            cursor.execute(self.system.sql_query_accounts)
            data = cursor.fetchall()
            Account.objects.filter(system=self.system).delete()
            for row in data:
                if len(row[3]) == 0:
                    first_name, last_name = row[2].split(' ', 1)[0], row[2].split(' ', 1)[-1]
                else:
                    first_name, last_name = row[2], row[3]
                account = Account(system=self.system, internal_id=row[0], login=row[1], first_name=first_name, last_name=last_name)
                account.save()
            # get users in roles
            cursor.execute(self.system.sql_query_accounts_roles)
            data = cursor.fetchall()
            for account in Account.objects.filter(system=self.system):
                account.roles.clear()
                account.save()
            for row in data:
                try:
                    account = Account.objects.get(system=self.system, internal_id=row[0])
                    account.roles.add(Role.objects.get(system=self.system, internal_id=row[1]))
                    account.save()
                except:
                    pass
