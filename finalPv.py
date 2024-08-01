import pandas as pd
from flask import Flask, request, jsonify, render_template, render_template_string,session,redirect,url_for
import socket
import webbrowser
from threading import Timer

from google.cloud import bigquery
from google.oauth2 import service_account

client = bigquery.Client(credentials=credentials, project=project_id)
Tablename = "Static_plants"
selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + Tablename

df = client.query(selectQuery).to_dataframe()
plants = df.Plantname.unique()

def listToString(s):
    return "".join(s)

def remove(string):
    return string.replace(" ", "")

app = Flask(__name__)
app.secret_key = 'your_secret_key'      # Change this to a random secret key for session management


USERNAME = 'admin'
PASSWORD = 'password123'


@app.route('/load_data')
def load_data():
    plant = request.args.get('plant')
    block = request.args.get('block')
    filter_plant = df[df['Plantname'] == plant]
    mytable = filter_plant.Tablename.unique()
    mytable = listToString(mytable)
    mytable = remove(mytable)
    selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + mytable + " WHERE Plant = '" + plant + "'"
    df1 = client.query(selectQuery).to_dataframe()
    df2 = df1[df1['Plant'] == plant]
    host = socket.gethostname()
    if block:
        block_data = df2[df2['Block'] == block]
        return jsonify(block_data.to_dict(orient='records'))
    blocks = df2.Block.unique()    
    # Calculate summary statistics
    rt = df2.astype(str)
    rt['DCCapacityKWp'] = pd.to_numeric(rt['DCCapacityKWp'], errors='coerce')
    totalblocks = len(rt.Block.unique())
    rt1 = rt[rt.DCCapacityKWp.notnull()]
    totaldcMWp = round(sum(rt1['DCCapacityKWp'])/1000, 2)
    invMake = rt.INVMake.unique()
    invMake = str(invMake)
    invModel = str(rt.INVERTERModel.unique())
    modMake = str(rt.Modulemake.unique())
    ModModel = str(rt.ModuleModel.unique())
    #Invertercount = 
    stringcounts =len(rt.STRINGS.notnull())
    #totalyconnector =
    
    summary = {
        'total_blocks': totalblocks,
        'total_dc_mwp': totaldcMWp,
        'strCount':stringcounts,
        'invMake': invMake,
        'total_invModel': invModel,
        'total_modMake': modMake,
        'total_ModModel': ModModel  
    }
    
    return jsonify({
        'blocks': blocks.tolist(),
        'summary': summary
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return jsonify({'success':False,'messege':'Invalid credentials'})
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f9f9f9;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        .login-container h2 {
            margin-bottom: 20px;
        }
        .login-container input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .login-container button {
            width: 100%;
            padding: 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .login-container button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
    """)
    

@app.route('/')
def home():
    if not session.get('logged_in'):
      return redirect(url_for('login'))
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PV Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
            background-image: url("https://github.com/Tusharlad123/PVform/blob/main/solar-881.gif?raw=true");
            background-repeat: no-repeat;
            background-size: cover;

        }
        .summary-container {
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
        }
        .summary-item {
            width: 45%;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-color: #fff;
            position: relative;
        }
        .underline {
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #0a7caa, #5b58a5, #0056b3, #8f298f, #0a7caa);
            background-size: 500% 100%;
            animation: colorChange 3s infinite;
        }
        @keyframes colorChange {
            0% { background-position: 0% 0%; }
            25% { background-position: 25% 0%; }
            50% { background-position: 50% 0%; }
            75% { background-position: 75% 0%; }
            100% { background-position: 100% 0%; }
        }
        .logo {
            width: 150px;
            position: absolute;
            left: 20px;
        }
        .main-content {
            padding: 20px;
        }
        h1 {
            font-size: 5rem;
            text-align: center;
            margin-top: -1rem;
            margin-bottom: 0;
            animation: changeColor infinite 3s;
        }
        @keyframes changeColor {
            0% { color: #0a7caa; }
            25% { color: #5b58a5; }
            50% { color: #0056b3; }
            75% { color: #8f298f; }
            100% { color: #0a7caa; }
        }
        .dropdown-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
            gap: 20px;
        }
        .dropdown {
            width: 200px;
            padding: 10px;
            background-color: #fff;
            border: 2px solid #007BFF;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .dropdown:focus {
            border-color: #005bb3;
            box-shadow: 0 0 8px rgba(0, 91, 187, 0.5);
            outline: none;
        }
        .search-bar {
            display: block;
            width: 300px;
            padding: 10px;
            margin: 20px auto;
            background-color: #fff;
            border: 2px solid #007BFF;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .search-bar:focus {
            border-color: #005bb3;
            box-shadow: 0 0 8px rgba(0, 91, 187, 0.5);
            outline: none;
        }
        button {
            display: block;
            width: 150px;
            padding: 10px;
            margin: 20px auto;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #0056b3;
        }
        #tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            margin: 5px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .tab:hover {
            background-color: #0056b3;
        }
        #data {
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
            overflow: hidden;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #007BFF;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        td[contenteditable="true"] {
            background-color: #fffdd0;
            cursor: pointer;
        }
        td[contenteditable="true"]:hover {
            background-color: #fffacd;
        }

        @media (max-width: 1024px) {
            .header, .main-content, .dropdown-container {
                padding: 10px;
                flex-direction: column;
            }
            h1 {
                font-size: 3rem;
            }
            .dropdown-container {
                flex-direction: column;
            }
            .dropdown {
                width: 100%;
                margin-bottom: 10px;
            }
            .summary-container {
                flex-direction: column;
            }
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }
            .logo {
                width: 100px;
            }
            .summary-item {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://github.com/Tusharlad123/PVform/blob/main/agel.png?raw=true" alt="Company Logo" class="logo">
        <h1>PV Form</h1>
    </div>
    <div class="underline"></div>
    <div class="dropdown-container">
        <select class="dropdown" id="plantDropdown" onchange="selectPlant()">
            {% for plant in plants %}
            <option value="{{ plant }}">{{ plant }}</option>
            {% endfor %}
        </select>
        <select class="dropdown" id="blockDropdown" onchange="selectBlock()" style="display:none;">
            <!-- Options will be dynamically added here -->
        </select>
    </div>
    
    <div class="summary-container" id="summaryContainer" style="display: none;">
        <h3>Summary</h3>
        <div class="summary-row">
            <div class="summary-item" id="totalBlocks"></div>
            <div class="summary-item" id="totalString"></div>
        </div>
        <div class="summary-row">
            <div class="summary-item" id="totalDcMWp"></div>
            <div class="summary-item" id="InverterMake"></div>
        </div>
        <div class="summary-row">
            <div class="summary-item" id="totalInverters"></div>
            <div class="summary-item" id="invertersModels"></div>
        </div>
        <div class="summary-row">
            <div class="summary-item" id="ModuleMake"></div>
            <div class="summary-item" id="ModuleModels"></div>
        </div>
    </div>
    <div class="main-content">
        <div id="data"></div>
        <button onclick="addRow()">Add Row</button>
        <button onclick="saveData()">Save Data</button>
    </div>

    <script>
    let currentBlock = '';
    let currentPlant = '';

    
    function createBlockDropdown(blocks, summary) {
        const blockDropdown = document.getElementById('blockDropdown');
        blockDropdown.innerHTML = '';
        blocks.forEach(block => {
            const option = document.createElement('option');
            option.value = block;
            option.text = block;
            blockDropdown.appendChild(option);
        });
        blockDropdown.style.display = 'block';
    
        // Display summary
        const summaryContainer = document.getElementById('summaryContainer');
        const totalBlocks = document.getElementById('totalBlocks');
        const totalDcMWp = document.getElementById('totalDcMWp');
        const totalinv = document.getElementById('totalInverters');
        const invMake = document.getElementById('InverterMake');
        const invModel = document.getElementById('invertersModels');
        const modMake = document.getElementById('ModuleMake');
        const modModel = document.getElementById('ModuleModels');
        const totalStr = document.getElementById('totalString');
    
        totalBlocks.textContent = `Total Blocks: ${summary.total_blocks}`;
        totalDcMWp.textContent = `Total DC MWp: ${summary.total_dc_mwp}`;
        totalStr.textContent = `Total String: ${summary.strCount}`;
        invMake.textContent = `Inverter Make: ${summary.invMake}`;
        totalinv.textContent = `Total Inverters: ${summary.total_invMake}`;
        invModel.textContent = `Inverter Models: ${summary.total_invModel}`;
        modMake.textContent = `Module Make: ${summary.total_modMake}`;
        modModel.textContent = `Module Model: ${summary.total_ModModel}`;
    
        summaryContainer.style.display = 'block';
    }

   function selectPlant() {
    const dropdown = document.getElementById('plantDropdown');
    currentPlant = dropdown.value;
    fetch(`/load_data?plant=${currentPlant}`)
        .then(response => response.json())
        .then(data => {
            // Sort blocks alphabetically
            data.blocks.sort((a, b) => a.localeCompare(b));
            createBlockDropdown(data.blocks, data.summary);
        });
}

    function selectBlock() {
        const dropdown = document.getElementById('blockDropdown');
        currentBlock = dropdown.value;
        loadData(currentBlock);
    }

    function loadData(block) {
        fetch(`/load_data?plant=${currentPlant}&block=${block}`)
            .then(response => response.json())
            .then(data => {
                let table = '<table><tr>';
                for (let key in data[0]) {
                    table += `<th>${key}</th>`;
                }
                table += `<th>Actions</th></tr>`;
                data.forEach(row => {
                    table += '<tr>';
                    for (let key in row) {
                        table += `<td contenteditable="true">${row[key]}</td>`;
                    }
                    table += '<td><button class="delete-button" onclick="deleteRow(this)">Delete</button></td></tr>';
                });
                table += '</table>';
                document.getElementById('data').innerHTML = table;
            });
    }

    function addRow() {
        const table = document.querySelector('table');
        if (!table) return;

        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
        let newRow = '<tr>';
        headers.forEach(header => {
            if (header !== 'Actions') {
                newRow += `<td contenteditable="true"></td>`;
            }
        });
        newRow += '<td><button class="delete-button" onclick="deleteRow(this)">Delete</button></td></tr>';
        table.innerHTML += newRow;
    }

    function deleteRow(button) {
        const row = button.parentElement.parentElement;
        row.remove();
    }

   

        function saveData() {
            let data = [];
    
            let table = document.querySelector('table');
            let headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
            let rows = table.querySelectorAll('tr');
            for (let i = 1; i < rows.length; i++) {
                let row = {};
                let cells = rows[i].querySelectorAll('td');
                headers.forEach((header, index) => {
                    if (header !== 'Actions') {
                        row[header] = cells[index].textContent;
                    }
                });
                data.push(row);
            }
            fetch(`/save_data?block=${currentBlock}&plant=${currentPlant}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(result => alert(result.message));
        }
    </script>
</body>
</html>
    """, plants=plants)

@app.route('/save_data', methods=['POST'])
def save_data():
    block = request.args.get('block')
    plant = request.args.get('plant')
    data = request.json
    print(data)
    block_df = pd.DataFrame(data)

    filter_plant = df[df['Plantname'] == plant]
    mytable = filter_plant.Tablename.unique()
    mytable = listToString(mytable)
    mytable = remove(mytable)

    selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + mytable
    df11 = client.query(selectQuery).to_dataframe()

    df22 = df11[df11['Block'] != block].append(block_df, ignore_index=True)
    df33 = df22[df22['Plant'] == plant]

    print(df22)

    csv_file_path = "D:\\OneDrive - Adani\\Documents\\" + plant + ".csv"
    df33.to_csv(csv_file_path, index=False)

    table_id = "agel-svc-winddata-dmz-prod.winddata." + mytable
    table = bigquery.Table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = "WRITE_TRUNCATE"  # Overwrite table truncate
    df22 = df22.astype(str)
    job = client.load_table_from_dataframe(df22, table, job_config=job_config)
    return jsonify({"message": "Data saved successfully"})

def open_browser():
    webbrowser.open_new("http://localhost:5000/")
# Run the Flask app
if __name__ == '__main__':
    Timer(1, open_browser()).start
    app.run(debug=False)
