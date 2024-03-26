from flask import Flask, render_template, request, jsonify
import threading
import time
import nmap3
from controllers.nmap import NmapController

app = Flask(__name__, static_url_path='/static')
nmap_controller = NmapController()

@app.route('/')
def index():
    sections = {
        'Section 1': ['1.1', '1.2'],
        'Section 2': ['2.1', '2.2'],
    }
    return render_template('index.html', sections=sections)

@app.route('/nmap_interface', methods=['GET', 'POST'])
def nmap_interface():
    if request.method == 'POST':
        target = request.form.get('target')
        options = request.form.get('options')

        print(target)
        print(options)
        return render_template('nmap_results.html', target=target, options=options)
    
    return render_template('nmap_interface.html', status='not scanning')

@app.route('/nmap_results', methods=['POST'])
def nmap_results():
    target = request.form.get('target')
    options = request.form.get('options')

    scan_result = nmap_controller.scan(target, options)

    return jsonify(scan_result)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
