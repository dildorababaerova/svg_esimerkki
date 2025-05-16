# PYSIDE6-SOVELLUS POSTGRESQL-NÄKYMIEN TIETOJEN TALLENTAMISEEN
# CSV- JA TSV-TIEDOSTOIHIN
# ============================================================


# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ----------------------------------
import os # Polkumääritykset
import sys # Käynnistysargumentit

from PySide6 import QtWidgets # Qt-vimpaimet

# Itsetehdyt moduulit
from customModules import dbOperations

# mainWindow_ui:n tilalle käännetyn pääikkunan tiedoston nimi
# ilman .py-tiedostopäätettä
from exportTool_ui import Ui_MainWindow # Käännetyn käyttöliittymän luokka

# Määritellään luokka, joka perii QMainWindow- ja Ui_MainWindow-luokan
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """A class for creating main window for the application"""
    
    # Määritellään olionmuodostin ja kutsutaan yliluokkien muodostimia
    def __init__(self):
        super().__init__()

        # Luodaan käyttöliittymä konvertoidun tiedoston perusteella MainWindow:n ui-ominaisuudeksi. Tämä suojaa lopun MainWindow-olion ylikirjoitukselta, kun ui-tiedostoa päivitetään
        self.ui = Ui_MainWindow()

        # Kutsutaan käyttöliittymän muodostusmetodia setupUi
        self.ui.setupUi(self)



        # self.serverName = ''
        # self.databaseName = ''
        # self.userName = ''   
        # self.password = ''
        # self.portNumber = ''
        self.serverName = 'localhost'
        self.databaseName = 'autolainaus'
        self.userName = 'postgres'   
        self.password = 'Q2werty'
        self.portNumber = '5432'


        


        # OHJELMOIDUT SIGNAALIT
        # ---------------------
        
        # Kun Tulosta-painiketta on klikattu, kutsutaan updatePrintedLabel-metodia
        # self.ui.tulostaPushButton.clicked.connect(self.updatePrintedLabel)

        self.ui.testConnectionPushButton.clicked.connect(self.connectDb)

   
   
    # OHJELMOIDUT SLOTIT
    # ------------------


    def connectDb(self):
        # Haetaan syötteet käyttöliittymästä
        # self.serverName = self.ui.serverLineEdit.text()
        # self.databaseName = self.ui.databaseLineEdit.text()
        # self.userName = self.ui.userNameLineEdit.text()
        # self.password = self.ui.passwordLineEdit.text()
        # self.portNumber = self.ui.portLineEdit.text()


        settingsDictionary = {
            'server': self.serverName,
            'database': self.databaseName,
            'userName': self.userName,  
            'password': self.password,
            'port': self.portNumber
        }

        # Testataan yhteys
        try:
            dbConnection=dbOperations.DbConnection(settingsDictionary)
            print('Yhteys onnistui')
            
            table= 'information_schema.tables'
            columns = ['table_type']
            filterText = f"table_schema NOT IN ('information_schema', 'pg_catalog')"
            
            self.ui.statusbar.showMessage('Yhteys onnistui')

            objectType = dbConnection.filterDistinctColumsFromTable(table, columns, filterText)
            print('Objektit nimet:', objectType)

            cleanedObjectType = []
            for value in objectType:
               objectType = value[0]
               cleanedObjectType.append(objectType)
            print('Tyyppilista:', cleanedObjectType)
            
            self.ui.objectTypeComboBox.addItems(cleanedObjectType)


            if cleanedObjectType == 'VIEW':
                columns = ['table_name']
                filterView = f"table_schema NOT IN ('information_schema', 'pg_catalog', 'BASE TABLE')"
                filterBaseTable = f"table_schema NOT IN ('information_schema', 'pg_catalog', 'VIEW')"
                
                objectViewName=dbConnection.filterDistinctColumsFromTable(table, columns, filterView)
                print('Objektin nimi:', objectViewName)
                objectBaseTableName=dbConnection.filterDistinctColumsFromTable(table, columns, filterBaseTable)
                print('Objektin nimi:', objectBaseTableName)
                
                cleanedObjectViewName = []
                for value in objectViewName:
                    objectViewName = value[0]
                    cleanedObjectViewName.append(objectViewName)
                print('View_Name_lista:', cleanedObjectViewName)
                
                cleanedObjectBaseTableName = []
                for value in objectBaseTableName:
                    objectBaseTableName = value[0]
                    cleanedObjectBaseTableName.append(objectBaseTableName)
                print('Base_Table_lista:', cleanedObjectBaseTableName)
                self.ui.objectNameComboBox.addItems(cleanedObjectViewName)
            else:
                self.ui.objectNameComboBox.addItems(cleanedObjectBaseTableName)
            

            #self.updatePrintedLabel()
        except Exception as e:
            print('Yhteys epäonnistui')
            print(e)
            #self.openWarning()

    # Muutetaan tulostettuLabel:n sisältö: teksti ja väri
    def updatePrintedLabel(self):
        pass
        #self.ui.tulostettuLabel.setText('Tulostettu')
        # self.ui.tulostettuLabel.setStyleSheet(u"color: rgb(0, 255, 0);")

    # Avataan MessageBox
    def openWarning(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle('Hirveetä!')
        msgBox.setText('Jotain kamalaa tapahtui')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()

if __name__ == "__main__":

    # Luodaan sovellus
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Luodaan objekti pääikkunalle ja tehdään siitä näkyvä
    window = MainWindow()
    window.show()

    # Käynnistetään sovellus ja tapahtumienkäsittelijä
    app.exec()

    