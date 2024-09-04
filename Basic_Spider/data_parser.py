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

    print("Uploading FoodBasics")
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
        print("Clearing table")
        clear_table = ("TRUNCATE TABLE foodbasics;")
        try:
            cursor.execute(clear_table)
        except:
            print("Error TRUNCATE table FOODBASICS")

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
    #Get NOFRILLS Data
    print("Uploading NoFrills")
    with open('nofrills_deals.jsonl') as data_file:
        #convert each line to json object
        for line in data_file:
            data.append(json.loads(line))
        #create insert statement
        add_product = ("INSERT INTO nofrills "
                        "(name, price, product_id, price_before, product_link, product_image) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        #Clear table
        print("Clearing table")
        clear_table = ("TRUNCATE TABLE nofrills;")
        try:
            cursor.execute(clear_table)
        except:
            print("Error TRUNCATE NOFRILLS")

        #for each product, create a tuple and add data using insert statement
        for product  in data:

            product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
            try:
                cursor.execute(add_product, product_data)
            except:
                print("Error ADD PRODUCT NOFRILLS")
            #commit data
            cnx.commit()


    data.clear()
    #Get SUPERSTORE Data
    print("Uploading Superstore")
    with open('superstore_deals.jsonl') as data_file:
        #convert each line to json object
        for line in data_file:
            data.append(json.loads(line))
        #create insert statement
        add_product = ("INSERT INTO superstore "
                        "(name, price, product_id, price_before, product_link, product_image) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        #Clear table
        print("Clearing table")
        clear_table = ("TRUNCATE TABLE superstore;")
        try:
            cursor.execute(clear_table)
        except:
            print("Error TRUNCATE TABLE SUPERSTORE")

        #for each product, create a tuple and add data using insert statement
        for product  in data:

            product_data = (product['name'], product['price'], product['product_id'], product['price_before'], product['product_link'], product['product_image'])
            try:
                cursor.execute(add_product, product_data)
            except:
                print("Error ADD PRODUCT SUPERSTORE")
            #commit data
            cnx.commit()
    print("Ending database connection")
    #end session
    cursor.close()
    cnx.close()
    print("Upload end")
