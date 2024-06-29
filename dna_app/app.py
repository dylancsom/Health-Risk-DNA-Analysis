from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from flask import jsonify
import re
import sqlite3
import threading
import tempfile


from werkzeug import utils
app = Flask(__name__, template_folder = '/Users/dylansomra/Desktop/dna_app/templates')

class App:
    def __init__(self):
        self.processing_status = "not started"
        self.lock = threading.Lock()
        


app.lock = threading.Lock()
        

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/css/dnamystyle.css')
def send_css():
    return send_from_directory('/Users/dylansomra/Desktop/dna_app/ApppyCss/',
                               'dnamystyle.css')

@app.route("/loading", methods=["GET", "POST"])
def loading():
    if app.processing_status == "finished":
        return redirect("/results")
    else:
        return render_template("loading.html")

@app.route("/check_processing_status", methods=["GET"])
def check_processing_status():
    
    return jsonify({"status": app.processing_status})
    
lock = threading.Lock()
matches = []
    
def process_file(file):
    
    app.lock.acquire()
    try:
        conn = sqlite3.connect('/Users/dylansomra/Desktop/dna_app/data/SNPTable.db')
        cursor = conn.cursor()
    

        snps = []


        with open(file.filename, "r") as file:
                for line in file:
                    match = re.search(r'rs\w+', line)
                    if match:
                        rsid = match.group()
                        alleles = line.split()
                        alleles = [x for x in alleles if x != rsid]
                        alleles = [x for x in alleles if not x.isdigit()]
                        allele_str = ' '.join(alleles)
                        snps.append((rsid, allele_str))
                
        
        for item in snps:
                rsid = item[0]
                alleles = item[1]
                cursor.execute("SELECT * FROM 'RSID_INFO' WHERE rsid=? AND alleles=?", (rsid, alleles))
                result = cursor.fetchone()
                if result:
                    matches.append((rsid, alleles, result[3], result[4]))
                    print("ID:", result[0])
                    print("rsid:", result[1])
                    print("alleles:", result[2])
                    print("cancer:", result[3])
                    print("risk association:", result[4])
    
        conn.close()
    
    finally:
        app.processing_status = "finished"
        redirect('/results')
        app.lock.release()
        

@app.route("/run_dna_read", methods=["POST"])
def run_dna_read():
    app.processing_status = "processing"
    file = request.files['file']
    
    thread = threading.Thread(target=process_file, args=(file,))
    thread.start()
        
    
    
    return redirect("/loading")
 


@app.route("/results", methods=["POST", "GET"])
def results():
    return render_template("result.html", matches=matches)


if __name__ == "__main__":
    app.run(debug=True)

