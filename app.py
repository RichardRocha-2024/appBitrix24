from flask import Flask, request, jsonify
import requests
import json
from gevent.pywsgi import WSGIServer
import os
import datetime

class empresa:
    def __init__(self, cnpj = None, razaoSocial = None,
                 ie = None, nomeFantasia = None, capitalSocial = None , endereco = None,
                numero = None, complemento = None, bairro = None, cep = None,
                cidade = None, estado = None, ibge =None, telefone = [], email = [],
                responsavel = None, cargo = None, matriz = False,
                cnae = [], situacaoData = None, dataAbertura = None, situacao = None,
                 ):
        self.cnpj = cnpj
        self.razaoSocial = razaoSocial
        self.ie = ie
        self.capitalSocial = capitalSocial
        self.nomeFantasia = nomeFantasia
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cep = cep
        self.cidade = cidade
        self.estado = estado
        self.ibge = ibge
        self.telefone = telefone
        self.email = email
        self.responsavel = responsavel
        self.cargo = cargo
        self.cnae = cnae
        self.situacaoData = situacaoData
        self.dataAbertura = dataAbertura
        self.situacao = situacao
        self.matriz = matriz



class Lead:
    def __init__(self, nome = None, cnpj = None, email = None, telefone = None, estado = None,
                 comentarios = None, utm_source = None, utm_medium = None, utm_campaign = None,
                 company = None, segmento = None):
        self.nome = nome
        self.cnpj = cnpj
        self.company = company
        self.email = email
        self.hasEmail = email
        self.telefone = telefone
        self.estado = estado
        self.comentarios = comentarios
        self.utm_source = utm_source
        self.utm_medium = utm_medium
        self.utm_campaign = utm_campaign
        self.segmento = segmento

    def buscarCNPJJa(self):
        AUTH_CNPJJA = str(os.environ.get('AUTH_CNPJJA'))
        
        response = requests.get('https://api.cnpja.com/office/' + self.cnpj + '?registrations=BR', 
                    headers={"Authorization": AUTH_CNPJJA})
        cnpjJson = response.json()

        #print("CNPJJA: " + str(cnpjJson))
        #print(cnpjJson)
        dadosCNPJ = empresa()
        
        #Dados da Empresa
        dadosCNPJ.cnpj = self.cnpj
        dadosCNPJ.razaoSocial = cnpjJson.get("company", {}).get("name", "")
        dadosCNPJ.nomeFantasia = cnpjJson.get("alias", "")
        dadosCNPJ.matriz = cnpjJson.get("head", False)
        dadosCNPJ.capitalSocial = cnpjJson.get("company", {}).get("equity", "")
        dadosCNPJ.dataAbertura = cnpjJson.get("founded", "")
        dadosCNPJ.situacao = cnpjJson.get("status", {}).get("text", "")
        dadosCNPJ.situacaoData = cnpjJson.get("statusDate", "")
        dadosCNPJ.porte = cnpjJson.get("company", {}).get("size", {}).get("text", "")
        
        #Address
        dadosCNPJ.endereco = cnpjJson.get("address", {}).get("street", "")
        dadosCNPJ.numero = cnpjJson.get("address", {}).get("number", "")
        dadosCNPJ.complemento = cnpjJson.get("address", {}).get("details", "")
        dadosCNPJ.bairro = cnpjJson.get("address", {}).get("district", "")
        dadosCNPJ.cep = cnpjJson.get("address", {}).get("zip", "")
        dadosCNPJ.estado = cnpjJson.get("address", {}).get("state", "")
        dadosCNPJ.ibge = cnpjJson.get("address", {}).get("municipality", "")

        #CNAE
        dadosCNPJ.cnae = []
        main = cnpjJson.get("mainActivity",{})
        side = cnpjJson.get("sideActivities",[])
        dadosCNPJ.cnae.append(main)
        for cnaeAc in side:
            dadosCNPJ.cnae.append(cnaeAc)

        #Contatos
        listaDeEmails = []
        listaDeEmails = cnpjJson.get("emails",[])
        for emailsJSON in listaDeEmails:
            dadosCNPJ.email.append(emailsJSON)
        
        listaDeEmails = []
        listaDeTelefones = cnpjJson.get("phones",[])
        for telefoneJSON in listaDeTelefones:
            dadosCNPJ.telefone.append('55'+str(telefoneJSON).replace("-",""))

        #Registros
        registros = cnpjJson.get("registrations",[])
        for registro in registros:
            if registro.get("type", "") == "IE":
                dadosCNPJ.ie = registro.get("number", "")

        return dadosCNPJ



app = Flask(__name__)
DESTINO_URL = str(os.environ.get('DESTINO_URL'))
#Para testes

DESTINO_URL_LIST_LEAD_ID = DESTINO_URL + "crm.lead.list.json?order[id]=desc&select[0]=id"   
ID_LAST_LEAD_REQUEST = requests.post(DESTINO_URL_LIST_LEAD_ID).json()['result'][0]['ID']
ID_NEXT_LEAD = int(ID_LAST_LEAD_REQUEST) + 1

print("ID_NEXT_LEAD: " + str(ID_NEXT_LEAD))

@app.route('/convertendoParaContatos', methods=['POST'])
def convert_and_forwardIlu():
    global ID_NEXT_LEAD
    tituloDoLead = "Lead - RD Station - nº " + str(ID_NEXT_LEAD)
    ASSIMGNED_BY_ID = 431

    try:
        # Obtendo o JSON enviado pelo primeiro sistema
        json_data = request.get_json()
        bu = request.args.get('bu','')

        if bu == 'iluminacao':
            dep = 45
        elif bu == 'solar':
            dep = 47
        else:
            #Cai padrão para iluminação
            dep = 45
     
        if not json_data:
            return jsonify({"erro": "Nenhum JSON recebido"}), 400
        
        #Campos = ['NAME','HAS_EMAIL','EMAIL','ADDRESS_PROVINCE','PHONE','COMMENTS','UTM_SOURCE','UTM_MEDIUM','UTM_CAMPAIGN']
        LeadRDStaion = Lead()
        
        
        # Garante que há um dicionário para evitar KeyError
        lead = json_data.get('leads', [{}])[0]  

        LeadRDStaion.nome = (lead.get('name', 'Desconhecido'))
        
        # E-mail: Adiciona 'Y' se existir e 'N' caso contrário
        email = lead.get('email', '')
        LeadRDStaion.hasEmail = ('Y' if email else 'N')
        LeadRDStaion.email = email

        LeadRDStaion.estado = (lead.get('state', ''))

        # Telefone: Prioriza 'personal_phone', senão 'mobile_phone', senão vazio
        phone = lead.get('personal_phone') or lead.get('mobile_phone', '')
        if phone != '' and phone != None:
            phone = "55" + str(phone).replace("-","")
        LeadRDStaion.telefone = str(phone).replace("-","")

        # Comentários: Adicionar 'company'
        LeadRDStaion.company = (lead.get('company', ''))

        # Última conversão
        conversion = lead.get('last_conversion', {}).get('conversion_origin', {})
        LeadRDStaion.utm_source = (conversion.get('source', ''))
        LeadRDStaion.utm_medium = (conversion.get('medium', ''))
        LeadRDStaion.utm_campaign = (conversion.get('campaign', ''))
        
        #ID do CNPJ 
        LeadRDStaion.cnpj = lead.get('custom_fields', {}).get('CNPJ:', '').replace('.','').replace('/','').replace('-','').replace(' ','')
        CNPJ_SEARCH = requests.get(DESTINO_URL + 'crm.company.list.json?filter[UF_CRM_1737047624]=' + f'{LeadRDStaion.cnpj}').json()        
        print(LeadRDStaion.cnpj)


        ASSIMGNED_BY_ID = 91

        # Trabalhando CNPJ Localizado
        if LeadRDStaion.cnpj == "":
            # Se não encontrar CNPJ, busca na API CNPJ JA
            print('Sem CNPJ')
            #ID do Contato
            ID_CONTATO = ""
            ID_CNPJ = ""
            
        elif CNPJ_SEARCH['result'] != []:
            print("CNPJ localizado")
            print(CNPJ_SEARCH['result'])
            #Pegar Data de Atualização do CNPJ
            CNPJ_SEARCH_DATA_UPDATE = str(CNPJ_SEARCH['result'][0]['DATE_MODIFY'])[0:10]
            hoje = datetime.datetime.now()
            hoje = str(hoje)[0:10]

            #ID do CNPJ
            ID_CNPJ = CNPJ_SEARCH['result'][0]['ID']

            #ID responsável
            try:
                ASSIMGNED_BY_ID = int(CNPJ_SEARCH['result'][0]['ASSIGNED_BY_ID'])
            except:
                ASSIMGNED_BY_ID = 91

            #Se a data de atualização for 6 meses a menos que hoje, atualiza
            diferencaDeDatas = datetime.datetime.strptime(hoje, "%Y-%m-%d") - datetime.datetime.strptime(CNPJ_SEARCH_DATA_UPDATE, "%Y-%m-%d")
            
            if diferencaDeDatas.days > 180:
                print("Atualizar CNPJ")
            
            #Criar o contato
            bodyContato = {
                "fields":
                {                     
                    "SECOND_NAME": f"{LeadRDStaion.nome}",
                    "NAME": f"{LeadRDStaion.nome}",
                    "ASSIGNED_BY_ID": ASSIMGNED_BY_ID,
                    "EMAIL": [ { "VALUE": f"{LeadRDStaion.email}", "VALUE_TYPE": "WORK" } ],
                    "ADDRESS_PROVINCE": f"{LeadRDStaion.estado}",
                    "PHONE": [ { "VALUE": f"{LeadRDStaion.telefone}", "VALUE_TYPE": "OTHER" } ],
                    "COMPANY_ID": f"{ID_CNPJ}",
                    "COMMENTS": f"{LeadRDStaion.company}",
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{LeadRDStaion.utm_source}",
                    "UTM_MEDIUM": f"{LeadRDStaion.utm_medium}",
                    "UTM_CAMPAIGN": f"{LeadRDStaion.utm_campaign}",
                    
                }
            }

            print(bodyContato)
            print("\n")

            DESTINO_URL_ADD_CONTACT = DESTINO_URL + "crm.contact.add.json"
            response = requests.post(DESTINO_URL_ADD_CONTACT, json=bodyContato)

            #ID do Contato
            ID_CONTATO = response.json()['result']

        elif LeadRDStaion.cnpj != "" and CNPJ_SEARCH['total'] !=1:
            print("CNPJ não localizado na base Bitrix")
            
            #Criar Empresa
            EmpresaRegistroNacional = LeadRDStaion.buscarCNPJJa()
            listaDeCnaes = [itemCNAE['id'] for itemCNAE in EmpresaRegistroNacional.cnae]

            bodyEmpresa = {
                "fields":
                {                     
                    "TITLE": f"{EmpresaRegistroNacional.razaoSocial}",
                    "COMPANY_TYPE" : "CUSTOMERS",
                    "ASSIGNED_BY_ID": ASSIMGNED_BY_ID,
                    "EMAIL": [ { "VALUE": f"{EmpresaRegistroNacional.email[0]['address']}", "VALUE_TYPE": "WORK" } ],
                    "ADDRESS_PROVINCE": f"{EmpresaRegistroNacional.estado}",
                    "PHONE": [ { "VALUE": f"{EmpresaRegistroNacional.telefone[0]}", "VALUE_TYPE": "OTHER" } ],
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{LeadRDStaion.utm_source}",
                    "UTM_MEDIUM": f"{LeadRDStaion.utm_medium}",
                    "UTM_CAMPAIGN": f"{LeadRDStaion.utm_campaign}",
                    "REVENUE": f"{EmpresaRegistroNacional.capitalSocial}",
                    "CURRENCY_ID": "BRL",
                    "UF_CRM_1737047541": f"{EmpresaRegistroNacional.endereco}, {EmpresaRegistroNacional.numero}",
                    "UF_CRM_1737047653": f"{listaDeCnaes}",
                    "UF_CRM_1737047624": f"{LeadRDStaion.cnpj}",              
                }
            }

            DESTINO_URL_ADD_COMPANY = DESTINO_URL + "crm.company.add.json"
            response = requests.post(DESTINO_URL_ADD_COMPANY, json = bodyEmpresa)


            print(response.json()['result'])
            ID_CNPJ = response.json()['result']
            print(ID_CNPJ)
            
            #Criar o contato
            bodyContato = {
                "fields":
                {                     
                    "SECOND_NAME": f"{LeadRDStaion.nome}",
                    "NAME": f"{LeadRDStaion.nome}",
                    "ASSIGNED_BY_ID": ASSIMGNED_BY_ID,
                    "COMPANY_ID": f"{ID_CNPJ}",
                    "EMAIL": [ { "VALUE": f"{LeadRDStaion.email}", "VALUE_TYPE": "WORK" } ],
                    "ADDRESS_PROVINCE": f"{LeadRDStaion.estado}",
                    "PHONE": [ { "VALUE": f"{LeadRDStaion.telefone}", "VALUE_TYPE": "OTHER" } ],
                    "COMMENTS": f"{LeadRDStaion.company}",
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{LeadRDStaion.utm_source}",
                    "UTM_MEDIUM": f"{LeadRDStaion.utm_medium}",
                    "UTM_CAMPAIGN": f"{LeadRDStaion.utm_campaign}",
                    
                }
            }

            DESTINO_URL_ADD_CONTACT = DESTINO_URL + "crm.contact.add.json"
            response = requests.post(DESTINO_URL_ADD_CONTACT, json=bodyContato)

            #ID do Contato
            ID_CONTATO = response.json()['result']


            

            
        else:
            ID_CNPJ = ''
            ID_CONTATO = ''


        # Criar o Lead
        listaDeCnaes = [itemCNAE['id'] for itemCNAE in EmpresaRegistroNacional.cnae]
        LeadRDStaion.segmento = 273

        print(4744099 in listaDeCnaes)

        if   4744099 in listaDeCnaes or 4744005 in listaDeCnaes:
            LeadRDStaion.segmento = 49
        elif 4742300 in listaDeCnaes or 4754703 in listaDeCnaes:
            LeadRDStaion.segmento = 53
        elif 4729699 in listaDeCnaes or 4712100 in listaDeCnaes:
            LeadRDStaion.segmento = 51

        body = {
                "fields":
                { 
                    "TITLE": f"{tituloDoLead}",
                    "NAME": f"{LeadRDStaion.nome}",
                    "ASSIGNED_BY_ID": ASSIMGNED_BY_ID,
                    "COMPANY_ID": f"{ID_CNPJ}",
                    "CONTACT_ID": f"{ID_CONTATO}",
                    "EMAIL": [ { "VALUE": f"{LeadRDStaion.email}", "VALUE_TYPE": "WORK" } ],
                    "ADDRESS_PROVINCE": f"{LeadRDStaion.estado}",
                    "PHONE": [ { "VALUE": f"{LeadRDStaion.telefone}", "VALUE_TYPE": "OTHER" } ],
                    "COMMENTS": f"{LeadRDStaion.company}",
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{LeadRDStaion.utm_source}",
                    "UTM_MEDIUM": f"{LeadRDStaion.utm_medium}",
                    "UTM_CAMPAIGN": f"{LeadRDStaion.utm_campaign}",
            }
        }
        
        # Requisição para adicionar ao Bitrix24
        DESTINO_URL_ADD_LEAD = DESTINO_URL + "crm.lead.add.json"
        response = requests.post(DESTINO_URL_ADD_LEAD, json=body)
        
        # Retornando a resposta do segundo sistema
        if response.status_code == 200:
            ID_NEXT_LEAD += 1
            DESTINO_DEAL_ID = DESTINO_URL + "crm.deal.list.json?select[0]=id&filter[TITLE]=" + tituloDoLead 
            response = requests.get(DESTINO_DEAL_ID)
            ID_DEAL = str(response.json()['result'][0]['ID'])
            if response.status_code == 200 and dep != '':
                DESTINO_DEAL_UPDATE = DESTINO_URL + "crm.deal.update.json"
                body = {
                    "id": f"{ID_DEAL}",
                    "fields": {
                        "UF_CRM_1734459916238": dep,
                        "UF_CRM_1734459945563": f"{LeadRDStaion.segmento}",
                    }
                }
                response = requests.post(DESTINO_DEAL_UPDATE, json=body)
                print("DEAL" + str(response.json()))
        

        print("NEXT: " + str(ID_NEXT_LEAD))
        return jsonify({
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
        })
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()