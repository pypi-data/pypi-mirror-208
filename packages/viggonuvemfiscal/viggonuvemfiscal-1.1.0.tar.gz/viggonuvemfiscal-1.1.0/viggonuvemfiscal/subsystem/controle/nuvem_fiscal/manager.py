import json
import requests
from viggocore.common.subsystem import operation, manager
from viggocore.common import exception, utils


# classes das chamadas a api da Nuvem Fiscal envolvendo empresa
class CadastrarEmpresa(operation.Create):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/empresas')
        return self.manager.executar_requisicao('POST', url, json=kwargs)


class ListarEmpresas(operation.List):

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/empresas')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class BuscarEmpresa(operation.List):

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class AlterarEmpresa(operation.Update):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}')
        return self.manager.executar_requisicao('PUT', url, json=kwargs)


class ConsultarCerticado(operation.List):

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/certificado')
        return self.manager.executar_requisicao('GET', url)


class CadastrarCertificado(operation.Update):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/certificado')
        kwargs.pop('cpf_cnpj')
        return self.manager.executar_requisicao('PUT', url, json=kwargs)


class DeletarCertificado(operation.Delete):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/certificado')
        return self.manager.executar_requisicao('DELETE', url)


class ConsultarConfiguracaoNfe(operation.List):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/nfe')
        return self.manager.executar_requisicao('GET', url)


class AlterarConfiguracaoNfe(operation.Update):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/nfe')
        kwargs.pop('cpf_cnpj')
        return self.manager.executar_requisicao('PUT', url, json=kwargs)


class ConsultarConfiguracaoNfce(operation.List):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/nfce')
        return self.manager.executar_requisicao('GET', url)


class AlterarConfiguracaoNfce(operation.Update):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        cpf_cnpj = self.manager.get_cpf_cnpj(**kwargs)
        url = self.manager.get_endpoint(f'/empresas/{cpf_cnpj}/nfce')
        kwargs.pop('cpf_cnpj')
        self.json = utils.to_json(kwargs)
        self.json = json.loads(self.json)
        return self.manager.executar_requisicao('PUT', url, json=self.json)


# classes das chamadas a api da Nuvem Fiscal envolvendo nfe
class EmitirNfe(operation.Create):

    def pre(self, session, **kwargs):
        nfe_dict = kwargs.pop('nfe_dict', None)
        self.json = utils.to_json(nfe_dict)
        self.json = json.loads(self.json)
        return True

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfe')
        return self.manager.executar_requisicao('POST', url, json=self.json)


class ListarNfe(operation.List):
    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfe')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class ConsultaStatusDoServicoNaSefazAutorizadoraNfe(operation.List):

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfe/sefaz/status')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class ConsultarNfe(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}')
        return self.manager.executar_requisicao('GET', url)


class BaixarXmlNfe(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/xml/nota')
        return self.manager.executar_requisicao('GET', url)


class BaixarPdfDanfeNfe(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/pdf')
        return self.manager.executar_requisicao('GET', url)


class ConsultarCancelamentoNfe(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/cancelamento')
        return self.manager.executar_requisicao('GET', url)


class BaixarXmlCancelamentoNfe(operation.List):
    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/cancelamento/xml')
        return self.manager.executar_requisicao('GET', url)


class CancelarNfeAutorizada(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/cancelamento')
        kwargs.pop('nfe_id')
        return self.manager.executar_requisicao('POST', url, json=kwargs)


class InutilizarSeqNumNfe(operation.List):

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfe/inutilizacoes')
        return self.manager.executar_requisicao('POST', url, json=kwargs)


# classes das chamadas a api da Nuvem Fiscal envolvendo nfce
class EmitirNfce(operation.Create):

    def pre(self, session, **kwargs):
        nfce_dict = kwargs.pop('nfce_dict', None)
        self.json = utils.to_json(nfce_dict)
        self.json = json.loads(self.json)
        return True

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfce')
        return self.manager.executar_requisicao('POST', url, json=self.json)


class ListarNfce(operation.List):
    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfce')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class ConsultaStatusDoServicoNaSefazAutorizadoraNfce(operation.List):

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfce/sefaz/status')
        return self.manager.executar_requisicao('GET', url, params=kwargs)


class ConsultarNfce(operation.List):

    def do(self, session, **kwargs):
        nfce_id = self.manager.get_nfce_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfce/{nfce_id}')
        return self.manager.executar_requisicao('GET', url)


class BaixarXmlNfce(operation.List):

    def do(self, session, **kwargs):
        nfe_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfe/{nfe_id}/xml/nota')
        return self.manager.executar_requisicao('GET', url)


class BaixarPdfDanfeNfce(operation.List):

    def do(self, session, **kwargs):
        nfce_id = self.manager.get_nfce_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfce/{nfce_id}/pdf')
        return self.manager.executar_requisicao('GET', url)


class ConsultarCancelamentoNfce(operation.List):

    def do(self, session, **kwargs):
        nfce_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfce/{nfce_id}/cancelamento')
        return self.manager.executar_requisicao('GET', url)


class BaixarXmlCancelamentoNfce(operation.List):
    def do(self, session, **kwargs):
        nfce_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfce/{nfce_id}/cancelamento/xml')
        return self.manager.executar_requisicao('GET', url)


class CancelarNfceAutorizada(operation.List):

    def do(self, session, **kwargs):
        nfce_id = self.manager.get_nfe_id(**kwargs)
        url = self.manager.get_endpoint(f'/nfce/{nfce_id}/cancelamento')
        kwargs.pop('nfce_id')
        return self.manager.executar_requisicao('POST', url, json=kwargs)


class InutilizarSeqNumNfce(operation.List):

    def do(self, session, **kwargs):
        url = self.manager.get_endpoint('/nfce/inutilizacoes')
        return self.manager.executar_requisicao('POST', url, json=kwargs)


class Manager(manager.Manager):
    # BASE_URL_PROD = 'https://api.nuvemfiscal.com.br'
    BASE_URL_HOMO = 'https://api.sandbox.nuvemfiscal.com.br'

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        # rotas de empresa
        self.cadastrar_empresa = CadastrarEmpresa(self)
        self.listar_empresas = ListarEmpresas(self)
        self.buscar_empresa = BuscarEmpresa(self)
        self.alterar_empresa = AlterarEmpresa(self)
        self.consultar_certicado = ConsultarCerticado(self)
        self.cadastrar_certificado = CadastrarCertificado(self)
        self.deletar_certificado = DeletarCertificado(self)
        self.consultar_configuracao_nfe = ConsultarConfiguracaoNfe(self)
        self.alterar_configuracao_nfe = AlterarConfiguracaoNfe(self)
        self.consultar_configuracao_nfce = ConsultarConfiguracaoNfce(self)
        self.alterar_configuracao_nfce = AlterarConfiguracaoNfce(self)
        # rotas de nfe
        self.emitir_nfe = EmitirNfe(self)
        self.listar_nfe = ListarNfe(self)
        self.consulta_status_do_servico_na_sefaz_autorizadora_nfe = \
            ConsultaStatusDoServicoNaSefazAutorizadoraNfe(self)
        self.consultar_nfe = ConsultarNfe(self)
        self.baixar_xml_nfe = BaixarXmlNfe(self)
        self.baixar_pdf_danfe_nfe = BaixarPdfDanfeNfe(self)
        self.consultar_cancelamento_nfe = ConsultarCancelamentoNfe(self)
        self.baixar_xml_cancelamento_nfe = BaixarXmlCancelamentoNfe(self)
        self.cancelar_nfe_autorizada = CancelarNfeAutorizada(self)
        self.inutilizar_seq_num_nfe = InutilizarSeqNumNfe(self)
        # rotas de nfce
        self.emitir_nfce = EmitirNfce(self)
        self.listar_nfce = ListarNfce(self)
        self.consulta_status_do_servico_na_sefaz_autorizadora_nfce = \
            ConsultaStatusDoServicoNaSefazAutorizadoraNfce(self)
        self.consultar_nfce = ConsultarNfce(self)
        self.baixar_xml_nfce = BaixarXmlNfce(self)
        self.baixar_pdf_danfe_nfce = BaixarPdfDanfeNfce(self)
        self.consultar_cancelamento_nfce = ConsultarCancelamentoNfce(self)
        self.baixar_xml_cancelamento_nfce = BaixarXmlCancelamentoNfce(self)
        self.cancelar_nfce_autorizada = CancelarNfceAutorizada(self)
        self.inutilizar_seq_num_nfce = InutilizarSeqNumNfce(self)

    def get_authorization(self):
        config = self.api.configuracao_nuvem_fiscals().\
            get_configuracao_nuvem_fiscal()
        data = {'Authorization': config.authorization}

        endpoint = self.get_endpoint('/empresas')
        response = requests.get(endpoint, params=data)

        if response.status_code == 401:
            url = 'https://auth.nuvemfiscal.com.br/oauth/token'
            body = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'grant_type': config.grant_type,
                'scope': config.scope
            }

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            response = requests.post(url, data=body, headers=headers)

            if response.status_code == 200:
                response = self.montar_response_dict(response)
                data['Authorization'] = 'Bearer ' + response.get(
                    'access_token', '')
                self.api.configuracao_nuvem_fiscals().update(
                    id=config.id, **{'authorization': data['Authorization']})
            else:
                raise exception.BadRequest(
                    'Não foi possível gerar a autorização.')
        return data

    def get_cpf_cnpj(self, **kwargs):
        cpf_cnpj = kwargs.get('cpf_cnpj', None)
        if cpf_cnpj is None:
            raise exception.BadRequest('O campo cpf_cnpj é obrigatório.')
        return cpf_cnpj

    def get_nfe_id(self, **kwargs):
        nfe_id = kwargs.get('nfe_id', None)
        if nfe_id is None:
            raise exception.BadRequest('O campo nfe_id é obrigatório.')
        return nfe_id

    def get_nfce_id(self, **kwargs):
        nfce_id = kwargs.get('nfce_id', None)
        if nfce_id is None:
            raise exception.BadRequest('O campo nfce_id é obrigatório.')
        return nfce_id

    def get_endpoint(self, resource):
        return self.BASE_URL_HOMO + resource

    def executar_requisicao(self, method, endpoint, params={}, json={},
                            headers={'Content-Type': 'application/json'},
                            data={}, sem_authorization=True):

        if sem_authorization is True:
            headers.update(self.get_authorization())

        if method == 'GET':
            return requests.get(
                endpoint, params=params, json=json, headers=headers, data=data)
        elif method == 'POST':
            return requests.post(
                endpoint, params=params, json=json, headers=headers, data=data)
        elif method == 'PUT':
            return requests.put(
                endpoint, params=params, json=json, headers=headers, data=data)
        elif method == 'DELETE':
            return requests.delete(endpoint)
        else:
            raise exception.OperationBadRequest(
                'Método de requisição não permitido.')

    def montar_response_dict(self, response):
        try:
            response_dict = json.loads(response.text)
        except Exception:
            response_dict = {'error': response.text}
        return response_dict
