from flask import Flask, render_template, request, json, jsonify, make_response
import subprocess
import os
import pandas as pd
from flask_cors import CORS

app = Flask(__name__,static_url_path='/static')
CORS(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/execute_script', methods=['POST'])
def execute_script():
    # Fetch the Python script content from the frontend
    filename = request.form['filename']

    # Save the script content to a temporary file
    with open('scripts/uploaded_script.py', 'w') as script_file:
        script_file.write(filename)

    # Execute the script
    try:
        subprocess.check_output(['python', 'scripts/uploaded_script.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    
    # The script generates a CSV file 'emissions.csv', read and render specific columns
    csv_column = read_csv_column('emissions.csv', column_name=['emissions','emissions_rate','cpu_power','gpu_power','ram_power','cpu_energy','gpu_energy','ram_energy','energy_consumed'])
    # print(f"csv_column = {csv_column}")
    # Remove the temporary script file
    os.remove('scripts/uploaded_script.py')
    resp = {
    "emissions": float(csv_column['emissions'].iloc[0]),
    "emissions_rate": float(csv_column['emissions_rate'].iloc[0]),
    "cpu_power": float(csv_column["cpu_power"].iloc[0]),
    "gpu_power": float(csv_column["gpu_power"].iloc[0]),
    'ram_power': float(csv_column['ram_power'].iloc[0]),
    'cpu_energy': float(csv_column['cpu_energy'].iloc[0]),
    'gpu_energy': float(csv_column['gpu_energy'].iloc[0]),
    'ram_energy': float(csv_column['ram_energy'].iloc[0]),
    'energy_consumed': float(csv_column['energy_consumed'].iloc[0])
    }
    
    json_response = jsonify({"data":resp})
    myResponse = make_response(json_response)
    myResponse.status_code=200
    
    
    # return render_template('home.html', csv_column=csv_column)
    return myResponse



def read_csv_column(file_path, column_name):
    import csv
    with open(file_path, 'r') as csv_file:
        df = pd.read_csv(csv_file)
        # Get the latest record, i.e the last one from emissions.csv
        data = df.tail(1)[column_name]
    return data


if __name__ == '__main__':
    app.run(debug=True)