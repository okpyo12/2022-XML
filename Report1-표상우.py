import sys, pymysql, json, csv
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class DB_Utils:
    conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')

    def queryExecutor(self, sql, params):
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                tuples = cursor.fetchall()
                return tuples
        except Exception as e:
            print(e)
            print(type(e))

#########################################

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dbManager = DB_Utils()
        self.setupUI()
        self.search_click()

    def setupUI(self):
        self.setWindowTitle("XML_Report-20181704-표상우")
        self.setGeometry(0, 0, 1100, 600)
        self.inputBox1 = {
            'customerName': {
                'label': QLabel('고객 : '),
                'inputType': QComboBox(),
            },
            'country': {
                'label':  QLabel('국가 : '),
                'inputType': QComboBox(),
            },
            'city': {
                'label':  QLabel('도시 : '),
                'inputType': QComboBox(),
            }
        }

        menu_name = QHBoxLayout()
        menu_name.addWidget(QLabel("주문 검색"))
        menu_name.setContentsMargins(15, 0, 0, 0)

        search_filter = QHBoxLayout()
        for name, data in self.inputBox1.items():
            label = data['label']
            label.setAlignment(Qt.AlignCenter)
            inputBox = data['inputType']
            inputBox.setMaximumWidth(150)
            search_filter.addWidget(label)
            search_filter.addWidget(inputBox)
            self.inputBox1[name]['inputType'].addItem("ALL")

            if name == 'customerName':
                sql = 'SELECT distinct name from customers ORDER BY name asc'
                params = ()
                tuples = self.dbManager.queryExecutor(sql, params)
                for i in tuples:
                    if i['name']:
                        self.inputBox1['customerName']['inputType'].addItem(i['name'])

            elif name == 'country':
                sql = 'SELECT distinct country from customers ORDER BY country asc'
                params = ()
                tuples = self.dbManager.queryExecutor(sql, params)
                for i in tuples:
                    if i['country']:
                        self.inputBox1['country']['inputType'].addItem(i['country'])
                
            elif name == 'city':
                sql = 'SELECT distinct city from customers ORDER BY city asc'
                params = ()
                tuples = self.dbManager.queryExecutor(sql, params)
                for i in tuples:
                    if i['city']:
                        self.inputBox1['city']['inputType'].addItem(i['city'])

        self.inputBox1['customerName']['inputType'].activated.connect(self.name_click)
        self.inputBox1['country']['inputType'].activated.connect(self.country_click)
        self.inputBox1['city']['inputType'].activated.connect(self.city_click)

        search_btn = QPushButton('검색')
        search_btn.setMaximumWidth(100)
        search_btn.setMinimumWidth(100)
        search_btn.clicked.connect(self.search_click)
        search_filter.addWidget(search_btn)
        search_filter.setContentsMargins(30, 0, 0, 0)

        menu_info = QHBoxLayout()
        self.menu_cnt = QLabel("검색된 주문의 개수 : ")
        menu_info.addWidget(self.menu_cnt)
        menu_info.setContentsMargins(30, 0, 0, 0)

        reset_btn = QPushButton('초기화')
        reset_btn.setMaximumWidth(100)
        reset_btn.clicked.connect(self.reset_click)
        menu_info.addWidget(reset_btn)

        self.Data_table = QTableWidget()
        self.Data_table.activated.connect(self.data_click)
        self.Data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menu_name)
        mainLayout.addLayout(search_filter)
        mainLayout.addLayout(menu_info)
        mainLayout.addWidget(self.Data_table)

        self.setLayout(mainLayout)

    def reset_click(self):
        for e, data in self.inputBox1.items():
            data['inputType'].setCurrentText("ALL")
        sql = "SELECT distinct city from customers order by city asc"
        params = ()
        cities = self.dbManager.queryExecutor(sql, params)
        self.inputBox1['city']['inputType'].clear()
        self.inputBox1['city']['inputType'].addItem("ALL")
        for city in cities:
            for columnName in city:
                self.inputBox1['city']['inputType'].addItem(city[columnName])
        self.search_click()

    def search_click(self):
        sql = "SELECT distinct orders.orderNo, orders.orderDate, orders.requiredDate, orders.shippedDate, orders.status, customers.name as customer, orders.comments from orders inner join customers on customers.customerId = orders.customerId "
        TorF = False
        for name, data in self.inputBox1.items():
            option = data['inputType'].currentText()
            if name == 'customerName':
                if option != 'ALL':
                    sql += f'where customers.name like "{option}" '
                    TorF = True
            if name == 'country':
                if option != 'ALL':
                    if TorF:
                        sql += f'and customers.country like "{option}" '
                        TorF = True
                    else:
                        sql += f'where customers.country like "{option}" '
                        TorF = True
            if name == 'city':
                if option != 'ALL':
                    if TorF:
                        sql += f'and customers.city like "{option}" '
                    else:
                        sql += f'where customers.city like "{option}" '

        sql += 'order by orders.orderNo asc'
        params = ()
        tuples = self.dbManager.queryExecutor(sql, params)

        if len(tuples) == 0:
            self.Data_table.setColumnCount(1)
            self.Data_table.setRowCount(1)
            self.Data_table.clear()
            self.menu_cnt.setText("검색된 주문의 개수 : " + str(0))
            return

        self.Data_table.setColumnCount(len(tuples[0]))
        self.Data_table.setRowCount(len(tuples))
        self.Data_table.setHorizontalHeaderLabels(list(tuples[0].keys()))

        for rowIDX, val in enumerate(tuples):
            for columnIDX, columnVal in enumerate(val.items()):
                if columnVal[1] == None:
                    continue
                self.Data_table.setItem(rowIDX, columnIDX, QTableWidgetItem(str(columnVal[1])))

        self.Data_table.resizeColumnsToContents()

        self.menu_cnt.setText("검색된 주문의 개수 : " + str(len(tuples)))

    def data_click(self, item):
        if self.Data_table.item(item.row(), 0) != None:
            self.order_data = Order_Detail(self.Data_table.item(item.row(), 0).data(0))
            self.order_data.show()

    def name_click(self):
        if self.inputBox1['city']['inputType'].currentText() != "ALL":
            sql = "SELECT distinct city from customers order by city asc"
            params = ()
            cities = self.dbManager.queryExecutor(sql, params)
            self.inputBox1['city']['inputType'].clear()
            self.inputBox1['city']['inputType'].addItem("ALL")
            for city in cities:
                for columnName in city:
                    self.inputBox1['city']['inputType'].addItem(city[columnName])
        
        if self.inputBox1['country']['inputType'].currentText() != "ALL":
            sql = "SELECT distinct country from customers order by country asc"
            params = ()
            countries = self.dbManager.queryExecutor(sql, params)
            self.inputBox1['country']['inputType'].clear()
            self.inputBox1['country']['inputType'].addItem("ALL")
            for country in countries:
                for columnName in country:
                    self.inputBox1['country']['inputType'].addItem(country[columnName])

    def country_click(self):
        if self.inputBox1['country']['inputType'].currentText() == "ALL":
            sql = "SELECT distinct city from customers order by city asc"
        else:
            sql = "SELECT distinct city from customers where country like '" + self.inputBox1['country']['inputType'].currentText() + "' order by city asc"
        params = ()
        cities = self.dbManager.queryExecutor(sql, params)
        self.inputBox1['city']['inputType'].clear()
        self.inputBox1['city']['inputType'].addItem("ALL")
        for city in cities:
            for columnName in city:
                self.inputBox1['city']['inputType'].addItem(city[columnName])

        if self.inputBox1['customerName']['inputType'].currentText() != "ALL":
            sql = "SELECT distinct name from customers order by name asc"
            params = ()
            names = self.dbManager.queryExecutor(sql, params)
            self.inputBox1['customerName']['inputType'].clear()
            self.inputBox1['customerName']['inputType'].addItem("ALL")
            for name in names:
                for columnName in name:
                    self.inputBox1['customerName']['inputType'].addItem(name[columnName])

    def city_click(self):
        if self.inputBox1['customerName']['inputType'].currentText() != "ALL":
            sql = "SELECT distinct name from customers order by name asc"
            params = ()
            names = self.dbManager.queryExecutor(sql, params)
            self.inputBox1['customerName']['inputType'].clear()
            self.inputBox1['customerName']['inputType'].addItem("ALL")
            for name in names:
                for columnName in name:
                    self.inputBox1['customerName']['inputType'].addItem(name[columnName])

class Order_Detail(QWidget):
    def __init__(self, orderNo):
        super().__init__()
        self.orderNo = orderNo
        self.dbManager = DB_Utils()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("XML_Report-20181704-표상우")
        self.setGeometry(200, 100, 700, 500)
        
        self.downloadType = {
            'CSV': QRadioButton('CSV'),
            'JSON': QRadioButton('JSON'),
            'XML': QRadioButton('XML'),
        }
        self.downloadType['CSV'].setChecked(True)

        detail_menu_name = QHBoxLayout()
        detail_menu_name.addWidget(QLabel("주문 상세 내역"))
        detail_menu_name.setContentsMargins(15, 0, 0, 0)

        order_detail_info = QHBoxLayout()
        order_detail_info.addWidget(QLabel("주문번호 : " + str(self.orderNo)))
        order_detail_info.addWidget(QLabel("상품개수 : "))
        order_detail_info.addWidget(QLabel("주문액 : "))
        order_detail_info.setContentsMargins(30, 0, 0, 0)

        detail_table = QHBoxLayout()
        self.detail_data_table = QTableWidget()
        self.detail_data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        detail_table.addWidget(self.detail_data_table)

        sql = f'SELECT distinct orderDetails.orderLineNo, orderDetails.productCode, products.name as productName, orderDetails.quantity, orderDetails.priceEach, (orderDetails.quantity * orderDetails.priceEach) as 상품주문액 from orders inner join orderDetails on orders.orderNo = orderDetails.orderNo inner join products on orderDetails.productCode = products.productCode where orders.orderNo like "{self.orderNo}" order by orderDetails.orderLineNo asc'
        params = ()
        self.tuples = self.dbManager.queryExecutor(sql, params)

        if len(self.tuples) == 0:
            return

        self.detail_data_table.setColumnCount(len(self.tuples[0]))
        self.detail_data_table.setRowCount(len(self.tuples))
        self.detail_data_table.setHorizontalHeaderLabels(list(self.tuples[0].keys()))

        price = 0
        for rowIDX, val in enumerate(self.tuples):
            for columnIDX, columnVal in enumerate(val.items()):
                if columnVal[1] == None:
                    continue
                self.detail_data_table.setItem(rowIDX, columnIDX, QTableWidgetItem(str(columnVal[1])))
                if columnIDX == 5:
                    price += float(columnVal[1])

        self.detail_data_table.resizeColumnsToContents()

        order_detail_info = QHBoxLayout()
        order_detail_info.addWidget(QLabel("주문번호 : " + str(self.orderNo)))
        order_detail_info.addWidget(QLabel("상품개수 : " + str(len(self.tuples))))
        order_detail_info.addWidget(QLabel("주문액 : " + str(price)))
        order_detail_info.setContentsMargins(30, 0, 0, 0)
        
        downloadLabel = QHBoxLayout()
        downloadLabel.addWidget(QLabel("파일 출력"))
        downloadLabel.setContentsMargins(15, 10, 10, 10)

        downloadLayout = QHBoxLayout()
        downloadLayout.addWidget(self.downloadType['CSV'])
        downloadLayout.addWidget(self.downloadType['JSON'])
        downloadLayout.addWidget(self.downloadType['XML'])
        downloadLayout.setContentsMargins(50, 10, 0, 10)

        downloadbtnLayout = QHBoxLayout()
        downloadbtn = QPushButton('저장')
        downloadbtn.clicked.connect(self.download_click)
        downloadbtn.setMaximumWidth(100)
        downloadbtn.setMinimumWidth(100)
        downloadbtnLayout.addWidget(downloadbtn, alignment=Qt.AlignRight)

        detailmainLayout = QVBoxLayout()
        detailmainLayout.addLayout(detail_menu_name)
        detailmainLayout.addLayout(order_detail_info)
        detailmainLayout.addLayout(detail_table)
        detailmainLayout.addLayout(downloadLabel)
        detailmainLayout.addLayout(downloadLayout)
        detailmainLayout.addLayout(downloadbtnLayout)

        self.setLayout(detailmainLayout)
    
    def download_click(self):
        if self.downloadType['CSV'].isChecked():
            with open(self.orderNo + ".csv", 'w') as f:
                w = csv.writer(f)
                w.writerow(self.tuples[0].keys())
                for item in self.tuples:
                    w.writerow(item.values())
            QMessageBox.about(self, "Ok", "저장되었습니다.")

        if self.downloadType['JSON'].isChecked():
            for i in self.tuples:
                i['priceEach'] = str(i['priceEach'])
                i['상품주문액'] = str(i['상품주문액'])
            with open(self.orderNo + ".json", 'w') as f:
                json.dump(self.tuples, f, indent=4, ensure_ascii=False)
            QMessageBox.about(self, "Ok", "저장되었습니다.")

        if self.downloadType['XML'].isChecked():
            root = ET.Element('TABLE')
            for i in self.tuples:
                row = ET.Element('ROW')
                root.append(row)
                for j in list(i.keys()):
                    if(i[j] == None):
                        row.attrib[j] = ''
                    else:
                        row.attrib[j] = str(i[j])
            ET.ElementTree(root).write(self.orderNo + ".xml", encoding='utf-8', xml_declaration=True)
            QMessageBox.about(self, "Ok", "저장되었습니다.")

#########################################

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
main()