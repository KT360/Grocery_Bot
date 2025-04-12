from flask import Flask, request, jsonify
import json
import os
import psycopg2
from psycopg2 import pool

app = Flask(__name__)

user = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
hostname = os.environ.get('HOST_NAME')


global db_pool

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=user,
    password=password,
    host=hostname,
    database='deals_uh8h_y8cg',
    port=5432
)
print("✅ Connection pool initialized")


@app.route("/")
def hello():
    return "Hello World!"

#Executes the search query on the database returns json with 'items' property/array containing all records
@app.route("/search", methods=['POST'])
def getItems():
    #For now working on the assumption that the query is a select/union query
    #TODO: Find a way to sanitize and confirm query is a selection
    try:

        #get query from headers
        data = request.get_json()
        sql_query = data.get('query')

        if not sql_query:
            return "No SQL query provided", 400

        #Establish connection to database
        cnx = db_pool.getconn()
        cursor = cnx.cursor()

        cursor.execute(sql_query)
        list = cursor.fetchall()

        formatted_list = []
        for row in list:
            formatted_list.append({
                'name':row[0],
                'price':row[1],
                'product_id':row[2],
                'price_before':row[3],
                'product_link':row[4],
                'product_image':row[5],
                'type':row[6]
            })

        cnx.commit()

        response = {"items":formatted_list}

        return json.dumps(response), 200

    except Exception as e:
        if cnx:
            cnx.rollback()
        return str(e), 500
    
    finally:
        if cursor:
            cursor.close()
        if cnx:
            db_pool.putconn(cnx) #Return connection to pool

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)