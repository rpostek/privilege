import fdb
from .base import DatasourceBase
from .. import models


class FirebirdDatasource(DatasourceBase):
    def __init__(self, system: models.System):
        super().__init__(system)
        self.__connection = None

    def __connect(self):
        self.__connection = fdb.connect(
            host=self.system.server_name,
            database=self.system.database,
            user=self.system.login,
            password=self.system.password,
            charset='UTF8'
        )

    def get_identifier(self):
        return "fb"

    def load_data(self):
        self.__connect()
        data = {}

        # load roles
        cur = self.__connection.cursor()
        cur.execute(self.system.sql_query_roles)
        result = cur.fetchall()
        data["roles"] = tuple(result)
        cur.close()

        # load accounts
        cur = self.__connection.cursor()
        cur.execute(self.system.sql_query_accounts)
        result = cur.fetchall()
        accounts_raw = tuple(result)
        data["accounts"] = []
        for account_raw in accounts_raw:
            if len(account_raw[3]) == 0:
                first_name, last_name = account_raw[2].split(' ', 1)[0], account_raw[2].split(' ', 1)[-1]
            else:
                first_name, last_name = account_raw[2], account_raw[3]

            data["accounts"].append((account_raw[0], account_raw[1], first_name, last_name))
        cur.close()

        # load accounts' roles
        cur = self.__connection.cursor()
        cur.execute(self.system.sql_query_accounts_roles)
        result = cur.fetchall()
        data["account-roles"] = tuple(result)
        cur.close()

        # load into models
        models.Role.objects.filter(system=self.system).delete()
        for role_raw in data["roles"]:
            role = models.Role(system=self.system, internal_id=role_raw[0], name=role_raw[1], description=role_raw[2])
            role.save()

        models.Account.objects.filter(system=self.system).delete()
        for account_raw in data["accounts"]:
            account = models.Account(system=self.system, internal_id=account_raw[0], login=account_raw[1], first_name=account_raw[2],
                                  last_name=account_raw[3])
            account.save()

        for account_role_raw in data["account-roles"]:
            try:
                account = models.Account.objects.get(system=self.system, internal_id=account_role_raw[0])
                account.roles.add(models.Role.objects.get(system=self.system, internal_id=account_role_raw[1]))
                account.save()
            except models.Account.DoesNotExist :
                pass
            except models.Role.DoesNotExist :
                print('brak roli', account_role_raw[1])

        self.__connection.close()
