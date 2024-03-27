import abc

from .. import models


class DatasourceBase(abc.ABC):
    def __init__(self, system: models.System):
        self.system = system

    @abc.abstractmethod
    def get_identifier(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_data(self):
        raise NotImplementedError


def get_datasource(system: models.System) -> DatasourceBase:
    if system.db_type == 'fb':
        from .firebird import FirebirdDatasource
        return FirebirdDatasource(system)
    elif system.db_type == 'MS':
        from .mssql import MsSQLDatasource
        return MsSQLDatasource(system)
    elif system.db_type == 'PS':
        from .powershell import PowershellDatasource
        return PowershellDatasource(system)
    elif system.db_type == 'YA':
        from .yaml import YamlDatasource
        return YamlDatasource(system)
    elif system.db_type == 'CS':
        from .csv import CsvDatasource
        return CsvDatasource(system)

    raise Exception("Unknown datasource type: " + system.db_type)
