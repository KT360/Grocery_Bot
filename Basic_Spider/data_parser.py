import psycopg2
import json
import os


user = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
hostname = os.environ.get('HOST_NAME')


#For each process (instance of the function call), need to create a new psql connection
def parseScrapedData():

    #Connect to database
    cnx = psycopg2.connect(user=user, password=password, host=hostname, database='deals_uh8h', port=5432)
    cursor = cnx.cursor()

    upload_schema = {
        {"file":"foodbasics_deals.jsonl", "table":"foodbasics"},
        {"file":"nofrills_deals.jsonl", "table":"nofrills"},
        {"file":"superstore_deals.jsonl", "table":"superstore"},
        {"file":"walmart_deals.jsonl", "table":"walmart"}
    }

    for schema in upload_schema:    
        #Add data
        data = []

        print("Uploading "+schema['table'])
        #Get FOODBASICS Data
        with open(schema['file']) as data_file:
            #convert each line to json object
            for line in data_file:
                data.append(json.loads(line))
            #create insert statement
            add_product = (f"INSERT INTO {schema['table']} "
                            "(name, price, product_id, price_before, product_link, product_image) "
                            "VALUES (%s, %s, %s, %s, %s, %s)")
            #Clear table
            print("Clearing table")
            clear_table = (f"TRUNCATE TABLE {schema['table']};")
            try:
                cursor.execute(clear_table)
            except:
                print(f"Error TRUNCATE table {schema['table']}")

            #for each product, create a tuple and add data using insert statement
            for product  in data:

                product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
                try:
                    cursor.execute(add_product, product_data)
                except:
                    print("Error ADD PRODUCT FOODBASICS")
                #commit data
                cnx.commit()

        data.clear()

    print("Ending database connection")
    #end session
    cursor.close()
    cnx.close()
    print("Upload end")
