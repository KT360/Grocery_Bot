import 'package:english_words/english_words.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:mysql_client/mysql_client.dart';
import 'package:http/http.dart' as http;

import 'package:fluttertoast/fluttertoast.dart';
import 'package:url_launcher/url_launcher.dart';


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
          colorScheme: ColorScheme.fromSeed(seedColor: const Color.fromARGB(255, 34, 255, 152)),
        ),
        home: MyHomePage(),
      ),
    );
  }
}

class MyAppState extends ChangeNotifier {
  //Products
  List<Map<dynamic,dynamic>> products = [];
  //Create connection as late, will given a value in main page init
  late MySQLConnection sqlConn;

  //Get all products
  Future<void> getAllProducts() async {
    products.clear();
    try{
      var result = await sqlConn.execute('SELECT * FROM foodbasics');
      for(var element in result.rows){
      Map data = element.assoc();
      products.add(data);
      }
      notifyListeners();
    }catch(e){
      print(e);
    }
  }

  Future<void> searchProduct(String prodname) async {
    products.clear();
    try{
      var result = await sqlConn.execute("SELECT * FROM foodbasics WHERE LOCATE('$prodname', name)>0");
      for(var element in result.rows){
        Map data = element.assoc();
        data['store'] = 'FoodBasics';
        products.add(data);
      }
      notifyListeners();
    }catch(e){
      print(e);
    }
  }

}

// ...

class MyHomePage extends StatefulWidget {
  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {

  var selectedIndex = 0;

  //NOTE: Emulator Android uses 10.0.2.2 as reference to current device
  //Connect to mysql
  Future<void> connectToSQL() async {

    //Get current instance of state
    final appState = Provider.of<MyAppState>(context, listen: false);

    try{

      final conn = await MySQLConnection.createConnection(
      host: '10.0.2.2', 
      port: 3306, 
      userName: 'android', 
      password: 'Iamdroid123',
      databaseName: 'Deals'
      );

      await conn.connect();

      //Set connection
      appState.sqlConn = conn;

      Fluttertoast.showToast(msg: 'Connection Successful');

    }catch(e){

      Fluttertoast.showToast(msg: 'Connection Error: $e');
      print(e);
    }

  }


  //Connect when main page is initialized
  @override
  void initState(){
    super.initState();
    connectToSQL();
  }

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
                      icon: Icon(Icons.favorite),
                      label: Text('Favorites'),
                    ),
                  ],
                  selectedIndex: selectedIndex,
                  onDestinationSelected: (value) {
                    setState((){
                      selectedIndex = value;
                    });
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

  final myController = TextEditingController();

  @override
  void dispose(){
    myController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {

    //Get whole state object
    var appState = Provider.of<MyAppState>(context);
    //Get updated instance of product list
    final productList = appState.products;

    
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 250,
            child: TextField(
              controller: myController,
              obscureText: false,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Search Product',
              )
            ),
          ),
          SizedBox(height: 10),
          Expanded(
          child: ListView.separated(
            itemCount: productList.length,
            separatorBuilder: (BuildContext context, int index) => const Divider(),
            itemBuilder: (BuildContext context, int index){
              return buildCard(productList[index]);
              },
            ),
          ),
          ElevatedButton(
            onPressed: () {
              appState.searchProduct(myController.text);
            },
            child: Text('Search'),
          ),
        ],
      ),
    );
  }
}

//Card Widget
Card buildCard(Map<dynamic, dynamic>  product) {
   var heading = product['price'];
   var subheading = 'was ${product['price_before']}';
   var cardImage = NetworkImage(
       product['product_image']);
   var supportingText =
       product['name'];
    var store = product['store'];
    var productLink = product['product_link'];
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
              color: Colors.lightGreen,
              width: 100,
              child: Text(store, style: TextStyle(color: Colors.yellow, fontWeight: FontWeight.bold),),
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