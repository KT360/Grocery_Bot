import 'package:english_words/english_words.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:provider/provider.dart';

import 'package:postgres/postgres.dart';
import 'package:http/http.dart' as http;

import 'package:fluttertoast/fluttertoast.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:loading_animation_widget/loading_animation_widget.dart';

import 'dart:convert';
import 'package:flutter/services.dart';


void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => MyAppState(),
      child: MaterialApp(
        title: 'Tracker App',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 164, 217, 238)),
        ),
        home: MyHomePage(),
      
      ),
      
    );
  }
}
//NOTE: Would be good to create a single json file with all store data such as table, formatted name, text color, background color, Icon
class MyAppState extends ChangeNotifier {
  //Products
  List<Map<dynamic,dynamic>> products = [];
  //Create connection as late, will given a value in main page init
  late Connection sqlConn;

  String lastSearch = "";

  bool showLoading = false;

  List<Map<String,dynamic>> allStores = [];

  MyAppState(){
    readJson();
  }

  void setShowLoading(value){
    showLoading = value;
    notifyListeners();
  }




  //get info on available stores, add selected property
  Future<void> readJson() async {
    final String response = await rootBundle.loadString('assets/stores.json');
    final data = await json.decode(response);

    //Add selected prperty
    for(var store in data['stores']){
      store['selected'] = false;
      allStores.add(store);
    }

    print("JSON successful");
    print("SIZE ${allStores.length}");
    notifyListeners();
  }

  void setSelected(index, isSelected){
    allStores[index]['selected'] = isSelected;
    notifyListeners();
  }


  //Takes in a table name an returns the appropriate store name
  String getFormattedStoreName(tableName){
    for(var value in allStores){
      if(value['table'] == tableName){
        return value['formatted'];
      }
    }

    return "No Name";
  }





  Future<void> makeSearchRequest(String query, String prodname) async {
    final url = Uri.parse("https://grocery-api-spje.onrender.com/search");

    try{

      final response = await http.post(
        url,
        headers:{'Content-Type':'application/json'},
        body: jsonEncode({'query':query})
      );

      if(response.statusCode == 200){

        final jsonData = jsonDecode(response.body);

        var itemList = jsonData['items'];

        var newList = itemList.map((item){
          //Add the formatted store name
          item['store'] = getFormattedStoreName(item['type']);

          return item;
        });

        for(var element in newList){
          products.add(element);
        }

      showLoading = false;
      lastSearch = prodname;
      //Notify
      notifyListeners();

      }else{
        print('Error: ${response.statusCode} = ${response.body}');
        Fluttertoast.showToast(msg: 'Connection Error: ${response.statusCode} = ${response.body}');
        showLoading = false;
        notifyListeners();
      }
    }catch(e){
      print('Exception: $e');
      Fluttertoast.showToast(msg: 'Connection Error: $e');
      showLoading = false;
      notifyListeners();
    }
  }






  //Filter tables according to the last product searched
  //All store tables should have the same columns and data types
  Future<void> filteredSearch(String prodname, List<String>tables, double priceFilter) async {

    //Clear products
    products.clear();

    var fullQuery = "";
    List<String> queries = [];
    var trimmed = prodname.trim();

    //for each table given in the array, compose query where we select the rows where the product name is present and the price is either null or lower than specified
    for(var store in tables){
      var query = "SELECT $store.*, '$store' AS type FROM $store WHERE POSITION(LOWER('$trimmed') IN LOWER($store.name))>0 AND ($store.price < $priceFilter OR $store.price IS NULL)";
      queries.add(query);
    }

    //Combine all the queries together, adding a 'UNION ALL' except at the end
    for(var i=0; i<queries.length; i++){

      if(i < queries.length - 1){
        fullQuery = fullQuery + queries[i] + " UNION ALL ";
      }else
      {
        fullQuery = fullQuery + queries[i];
      }

    }
    makeSearchRequest(fullQuery, prodname);
  }






  //Search product in all tables, no price
  //IMPORTANT table must have the same col names, types but also SAME COLUMN ORDER!
  Future<void> searchProduct(String prodname, List<String> allTables) async {

    //Clear products
    products.clear();

    var fullQuery = "";
    List<String> queries = [];
    var trimmed = prodname.trim();

    //for each table given in the array, compose query where we select the rows where the product name is present and the price is either null or lower than specified
    for(var store in allTables){
      var query = "SELECT $store.*, '$store' AS type FROM $store WHERE POSITION(LOWER('$trimmed') IN LOWER($store.name))>0";
      queries.add(query);
    }

    //Combine all the queries together, adding a 'UNION ALL' except at the end
    for(var i=0; i<queries.length; i++){

      if(i < queries.length - 1){
        fullQuery = fullQuery + queries[i] + " UNION ALL ";
      }else
      {
        fullQuery = fullQuery + queries[i];
      }

    }

    makeSearchRequest(fullQuery, prodname);
    /*
    try{

      //Execute the query
      var result = await sqlConn.execute(fullQuery);
      //Populate products with the appropriate store names depending on type column (column #7)
      var formattedMap = result.map((row){
        return {
          'name':row[0],
          'price':row[1],
          'price_before':row[2],
          'product_link':row[3],
          'product_image':row[4],
          'product_id':row[5],
          'store': getFormattedStoreName(row[6])
        };
      });

      //append all to products
      for(var element in formattedMap){
        products.add(element);
      }
      showLoading = false;

      lastSearch = prodname;

      //Notify
      notifyListeners();

    }catch(e){

      print(e);
      Fluttertoast.showToast(msg: 'Connection Error: $e');
      showLoading = false;
      notifyListeners();
      
    }*/
  }


}

// ...

class MyHomePage extends StatefulWidget {
  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {

  var selectedIndex = 0;

  @override
  Widget build(BuildContext context) {

    Widget page;
    switch(selectedIndex){
      case 0:
        page = GeneratorPage();
      default:
        throw UnimplementedError('no widget for $selectedIndex');
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        return Scaffold(
          appBar: AppBar(
            title: Text('Grocery Tracker'),
          ),
          body: Row(
            children: [
              SafeArea(
                child: NavigationRail(
                  extended: constraints.maxWidth >= 600,
                  destinations: [
                    NavigationRailDestination(
                      icon: Icon(Icons.home),
                      label: Text('Home'),
                    ),
                    
                    NavigationRailDestination(
                      icon: Icon(Icons.menu),
                      label: Text('Favorites'),
                    ),
                  ],
                  selectedIndex: selectedIndex,
                  onDestinationSelected: (value) {
                    /*setState((){
                      selectedIndex = value;
                    });*/ 
                  },
                ),
              ),
              Expanded(
                child: Container(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  child: page,
                ),
              ),
            ],
          ),
        );
      }
    );
  }
}



class GeneratorPage extends StatefulWidget {
  @override
  State<GeneratorPage> createState() => _GeneratorPageState();
}

class _GeneratorPageState extends State<GeneratorPage> {

  //bool fbSelected = true;
  //bool nfSelected = false;

  Color light = Colors.lightBlue;

  String? _priceFilter = r"Under 5$";

  final myController = TextEditingController();

  @override
  void dispose(){
    myController.dispose();
    super.dispose();
  }

  List<String> getAllTables(stateStores){
    List<String> tableList = [];
    for (var store in stateStores){
      tableList.add(store['table'] as String);
    }
    return tableList;
  }
  

  //Dialog box
  Future<void>_dialogBuilder(BuildContext context){
    return showDialog<void>(
      context: context,
      builder: (BuildContext context){
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setState){

            //Get whole state object
            var appState = Provider.of<MyAppState>(context);

            return AlertDialog(
              title: const Text('Product Filter'),
              content:SizedBox(
                height: 500,
                width: 300,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    
                    SizedBox(
                      width: 300,
                      height: 210,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          Expanded(
                            child: ListView.builder(
                              itemCount: appState.allStores.length,
                              itemBuilder: (BuildContext context, int index){
                                return CheckboxListTile(
                                  value: appState.allStores[index]['selected'] as bool, 
                                  onChanged: (bool? value){
                                    appState.setSelected(index,value);
                                  },
                                  title: Text(appState.allStores[index]['formatted'] as String),
                                );
                              },
                            ) 
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: 30,),
                    SizedBox(
                      height: 260,
                      width: 300,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          ListTile(
                              title: const Text(r'Under 5$'),
                              leading: Radio<String>(
                                value: r"Under 5$",
                                groupValue: _priceFilter,
                                onChanged: (String? value){
                                  setState(() {
                                    _priceFilter = value;
                                  });
                                },
                              )
                            ),
                          ListTile(
                              title: const Text(r'Under 10$'),
                              leading: Radio<String>(
                                value: r"Under 10$",
                                groupValue: _priceFilter,
                                onChanged: (String? value){
                                  setState(() {
                                    _priceFilter = value;
                                  });
                                },
                              )
                            ),
                          ListTile(
                              title: const Text(r'Under 15$'),
                              leading: Radio<String>(
                                value: r"Under 15$",
                                groupValue: _priceFilter,
                                onChanged: (String? value){
                                  setState(() {
                                    _priceFilter = value;
                                  });
                                },
                              )
                            ),
                        ],
                      ),
                    )
                  ],
                ),
              ),
              actions: <Widget>[
                TextButton(
                  style: TextButton.styleFrom(
                    textStyle: Theme.of(context).textTheme.labelLarge
                  ),
                  child: const Text('Cancel'),
                  onPressed: (){
                    Navigator.of(context).pop();
                  },
                ),
                TextButton(
                  style: TextButton.styleFrom(
                    textStyle: Theme.of(context).textTheme.labelLarge
                  ),
                  child: const Text('Apply'),
                  //Collect all selected table names, then pass it to search function as well as last search product
                  onPressed: (){
                    List<String> tableList = [];
                    var price = 0.00;
                    var count = 0;

                    for (var store in appState.allStores){
                      if(store['selected'] as bool == true){
                        tableList.add(store['table'] as String);
                        count++;
                      }
                    }
                    //Set the price limit depending on what was selected in the radio
                    switch(_priceFilter){
                      case r"Under 5$":
                        price = 5.00;
                      case r"Under 10$":
                        price = 10.00;
                      case r"Under 15$":
                        price = 15.00;
                      default:
                        price = 15.00;
                    }
                    if(count > 0){
                      appState.setShowLoading(true);
                      appState.filteredSearch(appState.lastSearch, tableList,price);
                      Navigator.of(context).pop();
                    }else{
                      Fluttertoast.showToast(msg: 'Please select atleast one store');
                    }
                  },
                )
              ],
            );
        });

      }
    );
  }

  @override
  Widget build(BuildContext context) {

    //Get whole state object
    var appState = Provider.of<MyAppState>(context);
    //Get updated instance of product list
    final productList = appState.products;

    
    
    return Stack(
      children: [
        Positioned.fill(
          child: ListView.builder(
            itemCount: productList.length+1, //Increment count of items since we are adding sizebox first
            //separatorBuilder: (BuildContext context, int index) => const Divider(),
            itemBuilder: (BuildContext context, int index){
              if(index == 0){
                //Return empy sizbox for margin from top
                return SizedBox(height:80);
              }
              return buildCard(productList[index - 1], appState.allStores); //Adjust index
            },
          )
        ),
        Positioned(
          top:15,
          left:20,
          right:20,
          child: SizedBox(
                child: TextField(
                  controller: myController,
                  obscureText: false,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Search Product',
                    fillColor: Colors.white,
                    filled: true
                  ),
                  //Perform three function, first collect all known tables, the set loading, then search product in tables
                  onSubmitted: (value) => {
                    appState.setShowLoading(true),
                    appState.searchProduct(value,getAllTables(appState.allStores))
                  },
                ),
              ),
        ),
        Positioned(
          right: 25,
          top: 625, //Dynamic positioning
          child: ElevatedButton(
              onPressed: appState.lastSearch == "" ? null : (){
                _dialogBuilder(context);
              },
              child: const Text('Filter')
            ),
        ),
        if(appState.showLoading)//Show loading animation
          Center(
            child:LoadingAnimationWidget.staggeredDotsWave(
              color: Color.fromARGB(255, 255, 255, 255),
              size: 50
            ), 
          )
          
      ]
    );
  }
}


Card buildCard(Map<dynamic, dynamic>  product, List<Map<String,dynamic>> allStores) {

  var storeList = allStores;

  var heading = r"$" + (product['price']?.toString() ?? 'Not Found');
  var subheading = r'was $'+ (product['price_before']?.toString() ?? 'Not Found');

  var cardImage = NetworkImage(
      product['product_image']);
  var supportingText =
      product['name'];
  var store = product['store']; //is the formatted version of the store name
  var productLink = product['product_link'];

  Color getARGB(numArray){
    return Color.fromARGB(numArray[0], numArray[1], numArray[2], numArray[3]);
  }

  Map<String,dynamic>? getStoreByName(storeName){
    for(var value in storeList){
      if(value['formatted'] == storeName)
      {
        return value;
      }
    }

    return null;
  }

  return Card(
    elevation: 4.0,
    child: Column(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: SizedBox(
                height: 75,
                child: ListTile(
                title: Text(heading, style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red),),
                subtitle: Text(subheading),
                ),
              ),
            ),
            Container(
              padding: EdgeInsets.all(10),
              color: getARGB(getStoreByName(store)?['background']),
              width: 100,
              child: Text(store, style: TextStyle(color: getARGB(getStoreByName(store)?['textColor']), fontWeight: FontWeight.bold),),
            )
          ],
        ),
        SizedBox(
          height: 200.0,
          child: Ink.image(
            image: cardImage,
            fit: BoxFit.cover,
          ),
        ),
        Container(
          padding: EdgeInsets.all(16.0),
          alignment: Alignment.centerLeft,
          child: Text(supportingText),
        ),
        ButtonBar(
          children: [
            TextButton(
              child: const Text('LEARN MORE'),
              onPressed: () async {
                final Uri url = Uri.parse(productLink);
                try{
                  var result = await launchUrl(url);
                  if(result){
                    Fluttertoast.showToast(msg: 'Connection Successful');
                  }
                }catch(e){
                  Fluttertoast.showToast(msg: e.toString());
                }
              },
            )
          ],
        )
      ],
    ));
}

//Card Widget
