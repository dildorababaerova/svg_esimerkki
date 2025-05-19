# PYSIDE6-SOVELLUS POSTGRESQL-NÄKYMIEN TIETOJEN TALLENTAMISEEN
# CSV- JA TSV-TIEDOSTOIHIN
# ============================================================


# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ----------------------------------
# import os # Polkumääritykset
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


        self.settingsDictionary = {
            'server': self.serverName,
            'database': self.databaseName,
            'userName': self.userName,  
            'password': self.password,
            'port': self.portNumber
        }

        # Testataan yhteys
        try:
        # Establish database connection
            self.dbConnection = dbOperations.DbConnection(self.settingsDictionary)
            
            # Get all object types (VIEW/BASE TABLE)
            table = 'information_schema.tables'
            columns = ['table_type']
            filterText = "table_schema NOT IN ('information_schema', 'pg_catalog')"
            objectTypes = self.dbConnection.filterDistinctColumnsFromTable(table, columns, filterText)
            
            # Clean object types
            cleanedObjectTypeList = ['Valitse']
            for value in objectTypes:
                objectType = value[0]
                cleanedObjectTypeList.append(objectType)
            print('Available object types:', cleanedObjectTypeList)
            
            # Optimal versio!
            # cleanedObjectTypes = [obj[0] for obj in objectTypes]
            print('Available object types:', cleanedObjectTypeList)
            
            # Populate object type combobox
            self.ui.objectTypeComboBox.clear()
            self.ui.objectTypeComboBox.addItems(cleanedObjectTypeList)
            
            # Connect object type selection change signal
            self.ui.objectTypeComboBox.currentTextChanged.connect(
                lambda: self.updateObjectNames(self.dbConnection))
            
            # Initial population of object names
            self.updateObjectNames(self.dbConnection)
            
            self.ui.statusbar.showMessage('Connection successful')
        
        except Exception as e:
            print('Connection failed')
            print(e)
            self.ui.statusbar.showMessage('Connection failed: ' + str(e))

    def updateObjectNames(self, dbConnection):
        """Updates object names combobox based on selected object type"""
        
        selected_type = self.ui.objectTypeComboBox.currentText()
        table = 'information_schema.tables'
        columns = ['table_name']
        
        try:
            if selected_type == 'VIEW':
                filterText = "table_schema NOT IN ('information_schema', 'pg_catalog') AND table_type = 'VIEW'"
            else:  # BASE TABLE
                filterText = "table_schema NOT IN ('information_schema', 'pg_catalog') AND table_type = 'BASE TABLE'"

            objectNames = self.dbConnection.filterDistinctColumnsFromTable(table, columns, filterText)
            # cleanedObjectNames = [name[0] for name in objectNames]
            cleanedObjectNameList = []
            for value in objectNames:
                objectName = value[0]
                cleanedObjectNameList.append(objectName)
            
            self.ui.objectNameComboBox.clear()
            self.ui.objectNameComboBox.addItems(cleanedObjectNameList)
            
            print(f'Objects of type {selected_type}:', cleanedObjectNameList)
            
        except Exception as e:
            print(f'Error loading {selected_type} names:', e)
            self.ui.statusbar.showMessage(f'Error loading {selected_type} names')

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