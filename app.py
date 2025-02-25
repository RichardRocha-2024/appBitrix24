from flask import Flask, request, jsonify
import requests
import json
from gevent.pywsgi import WSGIServer
import os

app = Flask(__name__)

DESTINO_URL_ADD_CONTATOS = str(os.environ.get('DESTINO_URL_ADD_CONTATOS'))

@app.route('/convertendoParaContatosIluminacao', methods=['POST'])
def convert_and_forwardIlu():
    
    try:
        # Obtendo o JSON enviado pelo primeiro sistema
        json_data = request.get_json()
     
        if not json_data:
            return jsonify({"erro": "Nenhum JSON recebido"}), 400
        
        Campos = ['NAME','HAS_EMAIL','EMAIL][0][VALUE','ADDRESS_PROVINCE','PHONE']
        Values = []

        if json_data['leads'][0]['name'] != None:
            Values.append(json_data['leads'][0]['name'])
        else:
            Values.append('')
        
        if json_data['leads'][0]['email'] != None:
            Values.append('Y')
            Values.append(json_data['leads'][0]['email'])
        else:
            Values.append('N')
            Values.append('')

        if json_data['leads'][0]['state'] != None:
            Values.append(json_data['leads'][0]['state'])
        else:
            Values.append('')

        if json_data['leads'][0]['personal_phone'] != None:
            Values.append(json_data['leads'][0]['personal_phone'])
        elif json_data['leads'][0]['mobile_phone'] != None:
            Values.append(json_data['leads'][0]['mobile_phone'])
        else:
            Values.append('')

        if json_data['leads'][0]['company'] != None:
            Values.append(json_data['leads'][0]['company'])
        else:
            Values.append('')

        if json_data['leads'][0]['last_conversion']['conversion_origin']['source'] != None:
            Values.append(json_data['leads'][0]['last_conversion']['conversion_origin']['source'])
        else:
            Values.append('')

        print('Capturou os dados de source')

        body = {
				"fields":
				{ 
                    "TITLE": "Lead - RD Station",
					"NAME": f"{Values[0]}",
					"ASSIGNED_BY_ID": 91,
                    "HAS_EMAIL": f"{Values[1]}",
                    "EMAIL": [ { "VALUE": f"{Values[2]}", "VALUE_TYPE": "OTHER" } ],
                    "ADDRESS_PROVINCE": f"{Values[3]}",
                    "PHONE": [ { "VALUE": f"{Values[4]}", "VALUE_TYPE": "OTHER" } ],
                    "COMMENTS": f"{Values[5]}",
                    "SOURCE_ID": "WEB", 
                    "SOURCE_DESCRIPTION": "Site RD Station",
                    "UTM_SOURCE": f"{Values[6]}",


		    }
        }        
        print(body)

        # Requisição
        response = requests.post(DESTINO_URL_ADD_CONTATOS, json=body)
        
        # Retornando a resposta do segundo sistema
        return jsonify({
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
        })

    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/convertendoParaContatosSolar', methods=['POST'])
def convert_and_forwardSol():
    try:
        # Obtendo o JSON enviado pelo primeiro sistema
        json_data = request.get_json()
     
        if not json_data:
            return jsonify({"erro": "Nenhum JSON recebido"}), 400
        


        Campos = ['NAME','HAS_EMAIL','EMAIL][0][VALUE','ADDRESS_PROVINCE','PHONE']
        Values = []

        if json_data['leads'][0]['name'] != None:
            Values.append(json_data['leads'][0]['name'])
        else:
            Values.append('')
        
        if json_data['leads'][0]['email'] != None:
            Values.append('Y')
            Values.append(json_data['leads'][0]['email'])
        else:
            Values.append('N')
            Values.append('')

        if json_data['leads'][0]['state'] != None:
            Values.append(json_data['leads'][0]['state'])
        else:
            Values.append('')

        if json_data['leads'][0]['personal_phone'] != None:
            Values.append(json_data['leads'][0]['personal_phone'])
        elif json_data['leads'][0]['mobile_phone'] != None:
            Values.append(json_data['leads'][0]['mobile_phone'])
        else:
            Values.append('')

        if json_data['leads'][0]['company'] != None:
            Values.append(json_data['leads'][0]['company'])
        else:
            Values.append('')

        body = {
				"fields":
				{ 
                    "TITLE": "Lead - RD Station",
					"NAME": f"{Values[0]}",
					"ASSIGNED_BY_ID": 91,
                    "HAS_EMAIL": f"{Values[1]}",
                    "EMAIL": [ { "VALUE": f"{Values[2]}", "VALUE_TYPE": "OTHER" } ],
                    "ADDRESS_PROVINCE": f"{Values[3]}",
                    "PHONE": [ { "VALUE": f"{Values[4]}", "VALUE_TYPE": "OTHER" } ],
                    "COMMENTS": f"{Values[5]}"

		    }
        }        

        print(Values)

        # Requisição
        response = requests.post(DESTINO_URL_ADD_CONTATOS, json=body)
        
        # Retornando a resposta do segundo sistema
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