import pandas as pd
from flask import Flask, request, jsonify, render_template_string
import socket
from google.cloud import bigquery
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file('D:/OneDrive - Adani/Rcode_Adani_Auto/Mypy/agel-svc-winddata-dmz-prod-fdac36bf5880.json')
project_id = 'agel-svc-winddata-dmz-prod'
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
    totalblocks = len(rt.Block.unique())
    rt['DCCapacityKWp'] = pd.to_numeric(rt['DCCapacityKWp'], errors='coerce')
    rt1 = rt[rt.DCCapacityKWp.notnull()]
    totaldcMWp = round(sum(rt1['DCCapacityKWp'])/1000, 2)
    
    summary = {
        'total_blocks': totalblocks,
        'total_dc_mwp': totaldcMWp
    }
    
    return jsonify({
        'blocks': blocks.tolist(),
        'summary': summary
    })

#@app.route('/summary')
#def summary():
#    #summary

 
    

@app.route('/')
def home():
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
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
            background-color: #fff;
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
        }

        .main-content {
            padding: 20px;
        }

        h1 {
            font-size: 5rem;
            text-align: center;
            margin-top: -2rem;
            margin-bottom: 0;
            position: relative;
            animation: changeColor infinite 3s;
            right: 35rem;
        }

        @keyframes changeColor {
            0% { color: #0a7caa; background-position: 0% 0%; }
            25% { color: #5b58a5; background-position: 25% 0%; }
            50% { color: #0056b3; background-position: 50% 0%; }
            75% { color: #8f298f; background-position: 75% 0%; }
            100% { color: #0a7caa; background-position: 100% 0%; }
        }

        .dropdown-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-top: 10px;
            position: relative;
            right: 40rem;
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

        .summary-container {
            margin-top: 20px;
            position: relative;
            right: 35rem;
        }

        .summary-container h3 {
            margin: 0;
        }

        .summary-container p {
            margin: 5px 0;
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
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
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
    </style>
</head>
<body>
    <div class="header">
        <img src="https://logowik.com/content/uploads/images/adani-renewables-green-energy1681.logowik.com.webp" alt="Company Logo" class="logo">
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
        <p id="totalBlocks"></p>
        <p id="totalDcMWp"></p>
    </div>
    <div class="main-content">
        <input type="text" placeholder="Search.." class="search-bar" oninput="searchTable()">
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
        
        totalBlocks.textContent = `Total Blocks: ${summary.total_blocks}`;
        totalDcMWp.textContent = `Total DC MWp: ${summary.total_dc_mwp}`;
        
        summaryContainer.style.display = 'block';
    }

    function selectPlant() {
        const dropdown = document.getElementById('plantDropdown');
        currentPlant = dropdown.value;
        fetch(`/load_data?plant=${currentPlant}`)
            .then(response => response.json())
            .then(data => createBlockDropdown(data.blocks, data.summary));
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
                const tableElement = document.querySelector('table');
                if (tableElement) {
                    tableElement.style.opacity = 1;
                    tableElement.style.transform = 'translateY(0)';
                }
            });
    }

    function searchTable() {
        const input = document.querySelector('.search-bar');
        const filter = input.value.toLowerCase();
        const table = document.querySelector('table');
        const tr = table.getElementsByTagName('tr');

        for (let i = 1; i < tr.length; i++) {
            let display = false;
            const td = tr[i].getElementsByTagName('td');
            for (let j = 0; j < td.length; j++) {
                if (td[j]) {
                    if (td[j].innerText.toLowerCase().indexOf(filter) > -1) {
                        display = true;
                    }
                }
            }
            tr[i].style.display = display ? '' : 'none';
        }
    }

    function addRow() {
        const table = document.querySelector('table');
        const newRow = table.insertRow();
        const cells = table.rows[0].cells.length;
        for (let i = 0; i < cells - 1; i++) {
            const newCell = newRow.insertCell(i);
            newCell.contentEditable = 'true';
            newCell.textContent = '';
        }
        const actionCell = newRow.insertCell(cells - 1);
        actionCell.innerHTML = '<button class="delete-button" onclick="deleteRow(this)">Delete</button>';
    }

    function deleteRow(button) {
        const row = button.closest('tr');
        row.parentNode.removeChild(row);
    }

    function saveData() {
        const table = document.querySelector('table');
        const rows = Array.from(table.rows).slice(1);
        const data = rows.map(row => {
            const cells = row.cells;
            const rowData = {};
            for (let i = 0; i < cells.length - 1; i++) {
                rowData[table.rows[0].cells[i].innerText] = cells[i].innerText;
            }
            return rowData;
        });
        fetch(`/save_data?plant=${currentPlant}&block=${currentBlock}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
          .then(result => alert('Data saved successfully!'))
          .catch(error => alert('Error saving data!'));
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

    df22 = df11[df11['Block'] != block].concat(block_df, ignore_index=True)
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

# Function to create a public URL
def create_public_url():
    return ("""
        (async () => {
            const url = await google.colab.kernel.proxyPort(5000);
            return url;
        })()
    """)

# Run the Flask app
if __name__ == '__main__':
    public_url = create_public_url()
    print(f"Public URL: {public_url}")
    app.run(port=5000)