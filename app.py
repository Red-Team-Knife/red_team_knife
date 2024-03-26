from flask import Flask, render_template, request, jsonify
from controllers.nmap import NmapController
from dataStorage import DataStorage
from sections import Sections

app = Flask(__name__, static_url_path='/static')
nmap_controller = NmapController()
data_storage = DataStorage('test.json')
sections_provider = Sections()
sections = sections_provider.sections

@app.route('/')
def index():
    
    return render_template('index.html', sections=sections)

@app.route(sections_provider.LINK_NMAP_INTERFACE, methods=['GET', 'POST'])
def nmap_interface():
    if request.method == 'POST':
        target = request.form.get('target')
        options = request.form.get('options')

        print(target)
        print(options)
        return render_template('nmap_results.html', target=target, options=options, sections=sections)
    
    return render_template('nmap_interface.html', sections=sections)

@app.route(sections_provider.LINK_NMAP_RESULTS, methods=['POST'])
def nmap_results():
    target = request.form.get('target')
    options = request.form.get('options')

    html_scan_result, scan_result = nmap_controller.scan(target, options)

    data_storage.save_key_value('nmap', scan_result)
    return jsonify(html_scan_result)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
