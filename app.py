from flask import Flask, render_template, request, jsonify
from controllers.nmap import NmapController
from dataStorage import DataStorage
from sections import Sections
from controllers.scan import ScanController

app = Flask(__name__, static_url_path='/static')
nmap_controller = NmapController()
data_storage = DataStorage('test.json')
sections_provider = Sections()
sections = sections_provider.sections
scan_controller = ScanController()

@app.route('/')
def index():
    scan_list = scan_controller.fetch_saved_scans()
    
    return render_template('index.html', scan_list=scan_list)

@app.route(sections_provider.LINK_NMAP_INTERFACE, methods=['GET', 'POST'])
def nmap_interface():
    if request.method == 'POST':
        target = request.form.get('target')
        option = request.form.get('options')
      
        return render_template('nmap_results.html', target=target, options=option, sections=sections)
    
    return render_template('nmap_interface.html', sections=sections, options_list=nmap_controller.options)

@app.route(sections_provider.LINK_NMAP_RESULTS, methods=['POST'])
def nmap_results():
    target = request.form.get('target')
    options = request.form.get('options')

    html_scan_result = nmap_controller.scan(target, options)
    return jsonify(html_scan_result)

@app.route(sections_provider.LINK_NMAP_SAVE_RESULTS, methods=['POST'])
def nmap_save_results():
    data_storage.save_key_value('nmap', nmap_controller.scan_result)
    return "<p>Results successfully saved.</p>"
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
