from flask import Flask, render_template, request, jsonify
import subprocess
import os
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/execute_script', methods=['POST'])
def execute_script():
    # Fetch the Python script content from the frontend
    filename = request.form['filename']
    print(filename)

    # Save the script content to a temporary file
    with open('scripts/uploaded_script.py', 'w') as script_file:
        script_file.write(filename)
        print(script_file)

    # Execute the script
    try:
        subprocess.check_output(['python', 'scripts/uploaded_script.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output

    # The script generates a CSV file 'emissions.csv', read and render specific columns
    csv_column = pd.read_csv('emissions.csv')
    column_name=['emissions','emissions_rate','cpu_energy','gpu_energy','ram_energy','energy_consumed']
    csv_column = csv_column.tail(1)[column_name]
    print(f"csv_column = {csv_column}")
    # Remove the temporary script file
    os.remove('scripts/uploaded_script.py')  
    csv_column = csv_column.to_json(orient='records')    
    print(f"json_csv_column = {csv_column}")
    return render_template("emissions.html", csv_column=csv_column)

def read_csv_column(file_path, column_name):
    import csv
    with open(file_path, 'r') as csv_file:
        df = pd.read_csv(csv_file)
        # Get the latest record, i.e the last one from emissions.csv
        data = df.tail(1)[column_name]
    return data

if __name__ == '__main__':
    app.run(debug=True)