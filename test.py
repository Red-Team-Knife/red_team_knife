from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/nmap_interface', methods=['GET', 'POST'])
def nmap_interface():
    if request.method == 'POST':
        # Get form data
        target = request.form.get('target')
        options = request.form.get('options')

        # Execute Nmap command (You'll need to install and import the python-nmap library)
        import nmap
        nm = nmap.PortScanner()
        nm.scan(hosts=target, arguments=options)

        # Get scan results
        scan_results = nm.all_hosts(), nm.csv()

        return render_template('nmap_results.html', scan_results=scan_results)

    return render_template('nmap_interface.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
