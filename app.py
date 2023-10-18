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
    script_content = request.form['script_content']

    # Save the script content to a temporary file
    with open('scripts/uploaded_script.py', 'w') as script_file:
        script_file.write(script_content)

    # Execute the script
    try:
        subprocess.check_output(['python', 'scripts/uploaded_script.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output

    # The script generates a CSV file 'emissions.csv', read and render a specific column
    csv_column = read_csv_column('emissions.csv', column_name=['emissions','emissions_rate','cpu_power','gpu_power','ram_power','cpu_energy','gpu_energy','ram_energy','energy_consumed'])
    print(f"csv_column = {csv_column}")
    # Remove the temporary script file
    os.remove('scripts/uploaded_script.py')

    return render_template('home.html', csv_column=csv_column)

def read_csv_column(file_path, column_name):
    import csv
    with open(file_path, 'r') as csv_file:
        df = pd.read_csv(csv_file)
        print(df)
        data = df.tail(1)[column_name]
    return data


if __name__ == '__main__':
    app.run(debug=True)