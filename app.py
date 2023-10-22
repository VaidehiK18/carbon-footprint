from flask import Flask, render_template, request, json, jsonify, make_response
import subprocess
import os
import pandas as pd
from flask_cors import CORS
import ast


app = Flask(__name__,static_url_path='/static')
CORS(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/execute_script', methods=['POST'])
def execute_script():
    # Fetch the Python script content from the frontend
    uploaded_file = request.files['file']
    print(uploaded_file)
    uploaded_file.save(f'{os.getcwd()}/scripts/{uploaded_file.filename}')
    

    # Add headers
    header = "from codecarbon import track_emissions"
    decorator = "@track_emissions()"
    function_start = "def track():"
    function_call = "track()"
        
    with open('scripts/uploaded_script.py', 'w') as script_file:
        script_file.write(uploaded_file.read())    

    # Check if the requirements file already exists, and if so, delete it
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        os.remove(requirements_file)

    # Generate the requirements.txt file
    generate_requirements_file(f'{os.getcwd()}/scripts/uploaded_script.py', requirements_file)

    # Save the script content to a temporary file
    with open('scripts/uploaded_script.py', 'r') as script_file:
        var = ast.parse(script_file.read())
    modified_content = f"{header}\n{decorator}\n{function_start}\n\t{var}\n{function_call}"
    print(modified_content)
    # Execute the script
    try:
        create_environment()
        subprocess.check_output(['python', 'scripts/uploaded_script.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    
    # The script generates a CSV file 'emissions.csv', read and render specific columns
    csv_column = read_csv_column('emissions.csv', column_name=['emissions','emissions_rate','cpu_power','gpu_power','ram_power','cpu_energy','gpu_energy','ram_energy','energy_consumed'])
    # print(f"csv_column = {csv_column}")
    # Remove the temporary script file
    os.remove('scripts/uploaded_script.py')
    delete_environment()
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

def create_environment():
    directory_path = os.getcwd()
    subprocess.run([f'{directory_path}/create_env.sh', directory_path])

def delete_environment():
    directory_path = os.getcwd()
    subprocess.run(f'{directory_path}/delete_env.sh')

# Define a function to extract import statements from a Python script
def extract_imports(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            for n in node.names:
                imports.append(f"{node.module}.{n.name}")
    return imports

# Define a function to generate a requirements.txt file
def generate_requirements_file(file_path, output_file):
    imports = extract_imports(file_path)
    
    # Create or append to the requirements.txt file
    with open(output_file, 'a') as req_file:
        for package in imports:
            req_file.write(f"{package}\n")


def read_csv_column(file_path, column_name):
    import csv
    with open(file_path, 'r') as csv_file:
        df = pd.read_csv(csv_file)
        # Get the latest record, i.e the last one from emissions.csv
        data = df.tail(1)[column_name]
        print(data)
    return data


if __name__ == '__main__':
    app.run(debug=True)