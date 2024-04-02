from flask import *
from controllers.nmap import NmapController
from dataStorage import DataStorage
from sections import Sections
from models.scan import Scan
from util import *
import os

app = Flask(__name__, static_url_path='/static')
nmap_controller = NmapController()
sections_provider = Sections()
sections = sections_provider.sections

current_scan = None

ROOT_FOLDER = "scans"
SCANS_PATH = os.path.abspath(ROOT_FOLDER)
if not os.path.exists(SCANS_PATH):
    os.makedirs(ROOT_FOLDER)
    os.path.abspath(SCANS_PATH)

@app.context_processor
def utility_processor():
    return dict(render_dictionary=render_dictionary)

@app.route('/')
def index():
    global current_scan
    if current_scan is not None:
        scan = current_scan.data_storage.__data__ 
        return render_template('index_scan.html',sections= sections, scan= scan)

    # List all saved scans
    scan_list = {}

    for scan_name in os.listdir(SCANS_PATH):
        scan = Scan(file_source= SCANS_PATH + "/" + scan_name)
        scan_list[scan_name] = scan.name

    
    return render_template('index.html', sections=sections, scan_list=scan_list)

@app.route('/new_scan', methods=['POST'])
def new_scan():
    scan_name = request.form.get('scan_name')
    scan_host = request.form.get('scan_host')
    global current_scan
    current_scan = Scan(scan_name, scan_host, SCANS_PATH)

    return redirect(url_for("index"))

@app.route('/scan_detail', methods=['GET'])
def scan_detail():
    global current_scan
    scan_file_name = request.args.get('scan_file_name')
    current_scan = Scan(file_source= SCANS_PATH + "/" + scan_file_name)
    return redirect(url_for('index'))

@app.route(sections_provider.LINK_NMAP_INTERFACE, methods=['GET', 'POST'])
def nmap_interface():
    if request.method == 'POST':
        target = request.form.get('target')
        option = request.form.get('options')
      
        return render_template('nmap_results.html', target=target, options=option, sections=sections)
    
    global current_scan
    if(current_scan is not None):
        return render_template('nmap_interface.html', sections=sections, options_list=nmap_controller.options, target= current_scan.host)
    return render_template('nmap_interface.html', sections=sections, options_list=nmap_controller.options)

@app.route(sections_provider.LINK_NMAP_RESULTS, methods=['POST'])
def nmap_results():
    target = request.form.get('target')
    options = request.form.get('options')

    html_scan_result = nmap_controller.scan(target, options)
    return jsonify(html_scan_result)

@app.route(sections_provider.LINK_NMAP_SAVE_RESULTS, methods=['POST'])
def nmap_save_results():
    global current_scan
    print(current_scan)
    if current_scan is not None:
        current_scan.save_scan('nmap', nmap_controller.scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
