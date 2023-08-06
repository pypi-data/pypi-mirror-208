from viggocore.common.subsystem import operation, manager
from viggocore.common import exception


class Create(operation.Create):

    def pre(self, session, **kwargs):
        configuracao_nuvem_fiscals = self.manager.list()
        if len(configuracao_nuvem_fiscals) > 0:
            raise exception.BadRequest(
                'Já existe uma configuração, por favor edite ela!')
        return super().pre(session, **kwargs)


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)

    def get_configuracao_nuvem_fiscal(self):
        configs = self.list()
        if len(configs) == 0:
            raise exception.NotFound(
                'Nenhuma configuração da Nuvem Fiscal cadastrada, por favor ' +
                'cadastre uma para usar a api.')
        return configs[0]
