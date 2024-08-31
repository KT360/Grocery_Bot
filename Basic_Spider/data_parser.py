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
    #Add data
    data = []

    #Get FOODBASICS Data
    with open('foodbasics_deals.jsonl') as data_file:
        #convert each line to json object
        for line in data_file:
            data.append(json.loads(line))
        #create insert statement
        add_product = ("INSERT INTO foodbasics "
                        "(name, price, product_id, price_before, product_link, product_image) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        #Clear table
        clear_table = ("TRUNCATE TABLE foodbasics;")
        cursor.execute(clear_table)

        #for each product, create a tuple and add data using insert statement
        for product  in data:

            product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
            cursor.execute(add_product, product_data)
            #commit data
            cnx.commit()


    data.clear()
    #Get NOFRILLS Data
    with open('nofrills_deals.jsonl') as data_file:
        #convert each line to json object
        for line in data_file:
            data.append(json.loads(line))
        #create insert statement
        add_product = ("INSERT INTO nofrills "
                        "(name, price, product_id, price_before, product_link, product_image) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        #Clear table
        clear_table = ("TRUNCATE TABLE nofrills;")
        cursor.execute(clear_table)

        #for each product, create a tuple and add data using insert statement
        for product  in data:

            product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
            cursor.execute(add_product, product_data)
            #commit data
            cnx.commit()


    data.clear()
    #Get SUPERSTORE Data
    with open('superstore_deals.jsonl') as data_file:
        #convert each line to json object
        for line in data_file:
            data.append(json.loads(line))
        #create insert statement
        add_product = ("INSERT INTO superstore "
                        "(name, price, product_id, price_before, product_link, product_image) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        #Clear table
        clear_table = ("TRUNCATE TABLE superstore;")
        cursor.execute(clear_table)

        #for each product, create a tuple and add data using insert statement
        for product  in data:

            product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
            cursor.execute(add_product, product_data)
            #commit data
            cnx.commit()

    #end session
    cursor.close()
    cnx.close()
