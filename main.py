from flask import Flask, send_from_directory, redirect, url_for, make_response, request, jsonify
from pathlib import Path
from multiprocessing import Value
from flask_cors import CORS
import requests
import shutil

SZAMLAZZ_URL = "https://www.szamlazz.hu/szamla/"


def cleanup():
    """
    Remove saved files from previous run.
    """
    if Path("./xmls").exists():
        shutil.rmtree("./xmls")

    if Path("./pdfs").exists():
        shutil.rmtree("./pdfs")

    Path("./xmls").mkdir()
    Path("./pdfs").mkdir()


class MyFlaskApp(Flask):
  def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
    if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
      with self.app_context():
        cleanup()
    super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

create_counter = Value('i', 0)
get_counter = Value('i', 0)

app = MyFlaskApp(__name__)
app.config['CREATE_FOLDER'] = Path(app.root_path) / 'xmls'
app.config['GET_FOLDER'] = Path(app.root_path) / 'pdfs'
CORS(app)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/create/', methods=['GET', 'POST'])
def create(): 

    payload = request.data
    data = {"action-szamla_agent_nyugta_create": payload}
    res = requests.post(SZAMLAZZ_URL, 
                        data=data)
    return jsonify({'data': res.text})

@app.route('/get/', methods=['GET', 'POST'])
def get():
    payload = request.data

    data = {"action-szamla_agent_nyugta_get": payload}
    res = requests.post(SZAMLAZZ_URL, 
                        data=data)

    with get_counter.get_lock():
        get_counter.value += 1
    
    target = app.config['GET_FOLDER'] / "{}.pdf".format(get_counter.value)

    with open(str(target), "w") as f:
        f.write(res.text)
        f.close()

    return redirect(url_for('get_file',
                            filename=target.name))

@app.route('/get/<filename>')
def get_file(filename):
    return send_from_directory(app.config['GET_FOLDER'],
                               filename)

@app.route('/storno/', methods=['GET', 'POST'])
def storno(): 

    payload = request.data
    data = {"action-szamla_agent_nyugta_storno": payload}
    res = requests.post(SZAMLAZZ_URL, 
                        data=data)
    return jsonify({'data': res.text})

@app.route('/email/', methods=['GET', 'POST'])
def email(): 

    payload = request.data
    data = {"action-szamla_agent_nyugta_send": payload}
    res = requests.post(SZAMLAZZ_URL, 
                        data=data)
    return jsonify({'data': res.text})