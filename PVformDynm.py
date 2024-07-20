import pandas as pd
from flask import Flask, request, jsonify
#from google.colab.output import eval_js
from IPython.display import display, Javascript
#import os
from google.cloud import bigquery
from google.oauth2 import service_account

df = client.query(selectQuery).to_dataframe()

blk = df.Block.unique()

# Create sample CSV files for different blocks


app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PV Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }

        h1 {
          font-size:5rem;
            color: #333;
            text-align: center;
            animation: colorChange infinite 3s;
          
        }
         @keyframes colorChange {
            0% { color: #0a7caa; }
            25% { color: #5b58a5; }
            50% { color: #0056b3; }
            75% { color: #8f298f; }
            100% { color: #0a7caa; }
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
        }

        .tab {
            padding: 10px 20px;
            margin: 0 5px;
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
    <h1>PV Form</h1>
    <div id="tabs">
        <button class="tab" onclick="loadData('block-1')">Block 1</button>
        <button class="tab" onclick="loadData('block-2')">Block 2</button>
        <button class="tab" onclick="loadData('block-3')">Block 3</button>
        <button class="tab" onclick="loadData('block-4')">Block 4</button>
    </div>
    <button onclick="loadData()">Load Data</button>
    <div id="data"></div>
    <button onclick="saveData()">Save Data</button>

    <script>
    let currentBlock = 'block-1';

    function loadData(block = currentBlock) {
        currentBlock = block;
        fetch(`/load_data?block=${block}`)
            .then(response => response.json())
            .then(data => {
                let table = '<table><tr>';
                for (let key in data[0]) {
                    table += `<th>${key}</th>`;
                }
                table += '</tr>';
                data.forEach(row => {
                    table += '<tr>';
                    for (let key in row) {
                        table += `<td contenteditable="true">${row[key]}</td>`;
                    }
                    table += '</tr>';
                });
                table += '</table>';
                document.getElementById('data').innerHTML = table;
            });
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
                row[header] = cells[index].textContent;
            });
            data.push(row);
        }
        fetch(`/save_data?block=${currentBlock}`, {
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
    """

@app.route('/load_data')

def load_data(df=df):
    #df = df
    block = request.args.get('block', 'block-2')
    df.set_index("Block", inplace = True)
    block_data = df.loc[["Block-1"]]     
    #block_data = df[df['Block'] == block] 
    print(f"loading data for {block}")
    #print(block_data.head())
    return jsonify(block_data.to_dict(orient='records'))

@app.route('/save_data', methods=['POST'])
def save_data():
    block = request.args.get('block', 'block-1')
    data = request.json
    block_df = pd.DataFrame(data)
    
    #remove the existing rows for the block and appent the new data
    global df
    df = df[df['Block']!= block].append(block_df, ignore_index= True)
    
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