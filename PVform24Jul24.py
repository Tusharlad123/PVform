import pandas as pd
from flask import Flask, request, jsonify, render_template_string
import numpy as np
# Assuming you have a BigQuery client and query already set up
from google.cloud import bigquery

project_id = 'agel-svc-winddata-dmz-prod'
client = bigquery.Client(credentials= credentials,project=project_id)
Tablename = "Static_plants"
 
df = client.query(selectQuery).to_dataframe() 
plants = df.Plantname.unique()

def listToString(s):
     # initialize an empty string
     str1 = ""
     # return string
     return (str1.join(s))

def remove(string):
    return string.replace(" ", "")
 

#plant = np.array(["Pvform1", "Pvform2","Pvform3","Pvform4"])

print('4')
#blk = sorted(blk , key = lambda x: int (x.split('-')[1]))
app = Flask(__name__)
@app.route('/load_data')

def load_data():    
    plant = request.args.get('plant') 
    filter_plant = df[df['Plantname'] == plant]  
    mytable = filter_plant.Tablename.unique()
    mytable = list(mytable)    
    mytable = listToString(mytable)
    mytable = remove(mytable)       

    selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + mytable    
    df1 = client.query(selectQuery).to_dataframe()      
    df2 = df1[df1['Plant'] == plant]        
    blk1 = df2.Block.unique()    
    block = request.args.get('block')     
    print(plant)
    print(blk1)
    block_data = df2[df2['Block'] == block]   
    print(block_data)
    #blk = np.array(["Block-1", "Block-11","Block-22", "Block-33","Block-99","Block-3"])
    return jsonify(block_data.to_dict(orient='records'))


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
            background-color: #ffffff;
            margin: 0;
            padding: 20px;
        }

        h1 {
            font-size: 5rem;
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

        .logo {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 150px; /* Adjust size as needed */
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

        .dropdown {
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
    </style>
</head>
<body>
    <img src="https://logowik.com/content/uploads/images/adani-renewables-green-energy1681.logowik.com.webp" alt="Company Logo" class="logo">
    <h1>PV Form</h1>

    <select class="dropdown" id="plantDropdown" onchange="selectPlant()">
        {% for plant in plants %}
        <option value="{{ plant }}">{{ plant }}</option>
        {% endfor %}
    </select>
    

    <div id="tabs"></div>
    <input type="text" placeholder="Search.." class="search-bar">
    <div id="data"></div>
    <button onclick="saveData()">Save Data</button>

    <script>
   let currentBlock = '';
   let currentPlant = 'plant';

    function createTabs(blocks) {
        const tabsContainer = document.getElementById('tabs');
        tabsContainer.innerHTML = '';
        blocks.forEach(block => {
            const button = document.createElement('button');
            button.className = 'tab';
            button.innerText = block;
            button.onclick = () => loadData(block);
            tabsContainer.appendChild(button);
        });
    }

    function selectPlant() {
        const dropdown = document.getElementById('plantDropdown');
        currentPlant = dropdown.value;
        load_Data();       
        }

    function loadData(block = currentBlock,plant = currentPlant) {
        currentBlock = block;
        currentPlant = plant;
        fetch(`/load_data?block=${block}&plant=${currentPlant}`)
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

    // Initial setup to create tabs
    const uniqueBlocks = {{ unique_blocks | safe }};
    createTabs(uniqueBlocks);
    </script>
</body>
</html>
    """, plants=plants)

@app.route('/get_blocks')

#def get_blocks():
 #   plant = request.args.get('plant', 'Jhansi')
 #   plant_data = df[df['Plant'] == plant]
 #   unique_blocks = plant_data['Block'].unique().tolist()
 #   return jsonify(unique_blocks)

@app.route('/save_data', methods=['POST'])
def save_data():
    block = request.args.get('block')
    plant = request.args.get('plant')
    data = request.json
    print(data)     
    block_df = pd.DataFrame(data)      
    df = client.query(selectQuery).to_dataframe() 
    
    df = df[df['Block'] != block].append(block_df, ignore_index=True)
    
    csv_file_path = "D:\\OneDrive - Adani\\Documents\\" + plant + ".csv"    
    df.to_csv(csv_file_path, index=False)    
    
    table = bigquery.Table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = "WRITE_TRUNCATE"  # Overwrite table truncate
    df = df.astype(str)
    job = client.load_table_from_dataframe(df, table, job_config=job_config)       
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