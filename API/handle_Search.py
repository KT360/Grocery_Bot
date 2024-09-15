from flask import Flask, request, jsonify
import json
import os
import psycopg2

app = Flask(__name__)

user = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
hostname = os.environ.get('HOST_NAME')

#Connect to database
cnx = psycopg2.connect(user=user, password=password, host=hostname, database='deals_uh8h', port=5432)
cursor = cnx.cursor()

@app.route("/")
def hello():
    return "Hello World!"

#Executes the search query on the database returns json with 'items' property/array containing all records
@app.route("/search", methods=['POST'])
def getItems(query):
    #For now working on the assumption that the query is a select/union query
    #TODO: Find a way to sanitize and confirm query is a selection
    try:

        #get query from headers
        data = request.get_json()
        sql_query = data.get('query')

        if not sql_query:
            return "No SQL query provided", 400

        cursor.execute(sql_query)
        list = cursor.fetchall()

        formatted_list = []
        for row in list:
            formatted_list.append({
                'name':row[0],
                'price':row[1],
                'price_before':row[2],
                'product_link':row[3],
                'product_image':row[4],
                'product_id':row[5],
                'type':row[6]
            })

        response = {"items":formatted_list}

        return json.dumps(response), 200

    except Exception as e:
        return str(e),200



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=4000)