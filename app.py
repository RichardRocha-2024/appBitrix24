from flask import Flask, request, jsonify
import requests
import json
from gevent.pywsgi import WSGIServer
import os

app = Flask(__name__)

DESTINO_URL_ADD_CONTATOS = str(os.environ.get('DESTINO_URL_ADD_CONTATOS'))

@app.route('/convertendoParaConcatosIluminacao', methods=['POST'])
def convert_and_forward():
    
    try:
        # Obtendo o JSON enviado pelo primeiro sistema
        json_data = request.get_json()
     
        if not json_data:
            return jsonify({"erro": "Nenhum JSON recebido"}), 400
        
        with open("MicroServicos/exemploRDNEW.json", "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        Campos = ['NAME','HAS_EMAIL','EMAIL][0][VALUE','ADDRESS_PROVINCE','PHONE][0][VALUE']
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