from flask import Flask, request, jsonify
import requests
import json
from gevent.pywsgi import WSGIServer
import os

app = Flask(__name__)

DESTINO_URL = str(os.environ.get('DESTINO_URL'))
#Para testes

DESTINO_URL_LIST_LEAD_ID = DESTINO_URL + "crm.lead.list.json?order[id]=desc&select[0]=id"   
ID_LAST_LEAD_REQUEST = requests.post(DESTINO_URL_LIST_LEAD_ID).json()['result'][0]['ID']
ID_NEXT_LEAD = int(ID_LAST_LEAD_REQUEST) + 1


@app.route('/convertendoParaContatosIluminacao', methods=['POST'])
def convert_and_forwardIlu():
    global ID_NEXT_LEAD

    tituloDoLead = "Lead - RD Station - nº " + str(ID_NEXT_LEAD)
    try:
        # Obtendo o JSON enviado pelo primeiro sistema
        json_data = request.get_json()
     
        if not json_data:
            return jsonify({"erro": "Nenhum JSON recebido"}), 400
        
        #Campos = ['NAME','HAS_EMAIL','EMAIL','ADDRESS_PROVINCE','PHONE','COMMENTS','UTM_SOURCE','UTM_MEDIUM','UTM_CAMPAIGN']
        Values = []
        # Garante que há um dicionário para evitar KeyError
        lead = json_data.get('leads', [{}])[0]  

        Values.append(lead.get('name', ''))

        # E-mail: adiciona 'Y' se existir e 'N' caso contrário
        email = lead.get('email', '')
        Values.append('Y' if email else 'N')
        Values.append(email)

        Values.append(lead.get('state', ''))

        # Telefone: prioriza 'personal_phone', senão 'mobile_phone', senão vazio
        Values.append(lead.get('personal_phone') or lead.get('mobile_phone', ''))

        # Comentários: adicionar 'company'
        Values.append(lead.get('company', ''))

        # Última conversão
        conversion = lead.get('last_conversion', {}).get('conversion_origin', {})
        Values.append(conversion.get('source', ''))
        Values.append(conversion.get('medium', ''))
        Values.append(conversion.get('campaign', ''))


        #CNPJ via CNPJ Já 

        body = {
				"fields":
				{ 
                    "TITLE": f"{tituloDoLead}",
					"NAME": f"{Values[0]}",
					"ASSIGNED_BY_ID": 91,
                    "HAS_EMAIL": f"{Values[1]}",
                    "EMAIL": [ { "VALUE": f"{Values[2]}", "VALUE_TYPE": "OTHER" } ],
                    "ADDRESS_PROVINCE": f"{Values[3]}",
                    "PHONE": [ { "VALUE": f"55 {Values[4]}", "VALUE_TYPE": "OTHER" } ],
                    "COMMENTS": f"{Values[5]}",
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{Values[6]}",
                    "UTM_MEDIUM": f"{Values[7]}",
                    "UTM_CAMPAIGN": f"{Values[8]}",
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
            if response.status_code == 200:
                DESTINO_DEAL_UPDATE = DESTINO_URL + "crm.deal.update.json"
                body = {
                    "id": f"{ID_DEAL}",
                    "fields": {
                        "UF_CRM_1734459916238": 45
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