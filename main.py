from flask import Flask, request, jsonify
from flask_cors import CORS
import pyrebase
from pymongo import MongoClient
from flask_cors import CORS
# Configuración de Firebase
firebase_config = {
  "apiKey": "AIzaSyBCTlDmnpFhoCGmU54auEcrkQ9IubGuZa0",
  "authDomain": "integrador-595c6.firebaseapp.com",
  "databaseURL": "integrador-595c6.firebaseio.com",
  "projectId": "integrador-595c6",
  "storageBucket": "integrador-595c6.appspot.com",
  "messagingSenderId": "976274846541",
  "appId": "1:976274846541:web:393aa19aa650e5b6713d04",
  "measurementId": "G-GG24SK52DN"   
}

# Configuración de MongoDB
mongo_uri = "mongodb+srv://ricardo:admin123@clusterinteligentes.5onsapb.mongodb.net/"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["integrador"]
collection = db["documentos"]
saldosCollection = db["saldos"]
reservasCollection = db["reservas"]
cuentasPresupuesto = db["cuentasPresupuesto"]
solicitud=db["solicitud"]
solicitudR=db["solicitudR"]


app = Flask(__name__)
CORS(app)
firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()
auth = firebase.auth()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    ruta= request.form['ruta']
    filename = ruta + file.filename
    # Cargar archivo a Firebase Storage
    storage.child(filename).put(file)
    # Obtener la URL del archivo en Firebase
    url = storage.child(filename).get_url(None)
    # Crear un registro en MongoDB con la URL del archivo
    doc = {"url": url,
            "nombre_archivo": filename
           }
    collection.insert_one(doc)
    return "Archivo cargado exitosamente."

@app.route('/delete', methods=['POST'])
def eliminar_archivo():
    request_data = request.get_json()
    ruta= request_data['ruta']
    nombre_archivo = request_data['nombre_archivo']
    nombre_archivo = ruta + nombre_archivo
    # Eliminar archivo de Firebase Storage
    storage.delete(nombre_archivo,token=None)
    # Eliminar registro en MongoDB
    collection.delete_one({"nombre_archivo": nombre_archivo})
    return jsonify({"message": f"Archivo {nombre_archivo} eliminado exitosamente."})

def convertir_a_cadena(documento):
    documento['_id'] = str(documento['_id'])
    return documento

@app.route('/listarSaldos', methods=['GET'])
def listar_saldos():
    # Obtener todos los registros de MongoDB
    saldos = saldosCollection.find()
    # Crear una lista con los registros
    lista_saldos = []
    for saldo in saldos:
        saldo = convertir_a_cadena(saldo)
        lista_saldos.append(saldo)
    return jsonify(lista_saldos)

@app.route('/listarReservas', methods=['GET'])
def listar_reservas():
    # Obtener todos los registros de MongoDB
    reservas = reservasCollection.find()
    # Crear una lista con los registros
    lista_reservas = []
    for reserva in reservas:
        reserva = convertir_a_cadena(reserva)
        lista_reservas.append(reserva)
    return jsonify(lista_reservas)

@app.route('/listarCuentasPresupuesto', methods=['GET'])
def listar_cuentas_presupuesto():
    # Obtener todos los registros de MongoDB
    cuentas = cuentasPresupuesto.find()
    # Crear una lista con los registros
    lista_cuentas = []
    for cuenta in cuentas:
        cuenta = convertir_a_cadena(cuenta)
        lista_cuentas.append(cuenta)
    return jsonify(lista_cuentas)
@app.route('/list', methods=['GET'])
def listar_archivos():
    # Obtener todos los registros de MongoDB
    docs = collection.find({})
    # Crear lista de archivos
    archivos = []
    for doc in docs:
        # Convertir el ObjectId a cadena
        doc['_id'] = str(doc['_id'])
        archivos.append(doc)
    return jsonify(archivos)
@app.route('/addsoli', methods=['POST'])
def addsoli():
    body = request.get_json()
    fecha= body['fecha']
    dependencias=body['dependencia']
    gastos= body['gastos']
    consecutivo = body['consecutivo']
    doc = {"fecha": fecha,
            "dependencia": dependencias,
            "gastos": gastos,
            "consecutivo": consecutivo
           }
    solicitud.insert_one(doc)
    return "Solicitud enviada exitosamente."

@app.route('/addsoliR', methods=['POST'])
def addsoliR():
    body = request.get_json()
    fecha= body['fecha']
    reintegros = body['reintegros']   
    consecutivo = body['consecutivo']
    doc = {"fecha": fecha,
            "reintegros": reintegros,
            "consecutivo": consecutivo
           }
    solicitudR.insert_one(doc)
    return "Solicitud enviada exitosamente."
    

    


if __name__ == '__main__':
    app.run()