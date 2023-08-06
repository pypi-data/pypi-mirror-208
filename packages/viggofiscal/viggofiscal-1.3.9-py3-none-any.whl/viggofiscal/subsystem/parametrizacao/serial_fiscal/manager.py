from viggocore.common import exception
from viggocore.common.subsystem import operation, manager


class Update(operation.Update):

    def do(self, session, **kwargs):
        kwargs.pop('ambiente', None)
        kwargs.pop('serie', None)
        kwargs.pop('modelo', None)
        return super().do(session=session, **kwargs)


class GetNextUltimoDoc(operation.Operation):
    def pre(self, session, id, **kwargs):
        serie_fiscal = self.manager.get(id=id)
        if not serie_fiscal:
            raise exception.NotFound('ERROR! serie_fiscal not found')
        self.serie_fiscal_id = serie_fiscal.id

        return True

    def do(self, session, **kwargs):
        next_ultimo_doc = self.driver.get_next_ultimo_doc(
            session, self.serie_fiscal_id)

        if next_ultimo_doc is None:
            raise exception.ViggoCoreException(
                'Não foi possível retornar o próximo ultimo_doc da serie_fiscal'
            )

        return next_ultimo_doc


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.update = Update(self)
        self.get_next_ultimo_doc = GetNextUltimoDoc(self)
