from flask import Flask, request, jsonify
from flask_cors import CORS
import pyrebase
from pymongo import MongoClient

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
solicitud=db["solicitud"]


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
    

    


if __name__ == '__main__':
    app.run()