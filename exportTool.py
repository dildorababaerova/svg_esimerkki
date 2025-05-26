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

        # Tietokantayhteys
        self.serverName = ''
        self.portNumber = ''
        self.databaseName = ''
        self.userName = ''
        self.password = ''

        # Tietokantaobjekti
        self.dbobjectType = ''
        self.dbObjectName = ''

        # Tietokantaobjektin sarakkeiden nimet
        self.columnNamesList = []
        self.resultSet = []

        # Virheilmoitustiedot
        self.errorWindowTitle = ""
        self.errorText = ""
        self.errorDetails = ""

        # Oletustallennushakemisto
        self.defaultFolder = f'{os.path.expanduser('~')}\\Documents\\'

        # OHJELMOIDUT SIGNAALIT
        # ---------------------

        # Kun painetaan Testaa-painiketta, näytetään tilarivillä tulos ja
        # päivtetään objektityypin valinnat. Jos virhe, näyteään msgbox
        # Painike asettaa tietokantaparametrit ja yhteysmerkkijonon

        self.ui.testConnectionPushButton.clicked.connect(self.connectDb)
        
        # Kun poistutaan objektityypin valinnasta, haetaan tyypin objketilista
        # ja päivitetään objektin nimi -valinnat 
        self.ui.objectTypeComboBox.currentIndexChanged.connect(self.getObjectNames)


        # TODO: Kun poistutaan / valinta on muuttunut objektilistasta 
        # näyteään päivitetään esikatselu ja näytetään Tallenna-painike
        self.ui.objectNameComboBox.currentIndexChanged.connect(self.updatePreview)
        # self.ui.getDataPushButton.clicked.connect(self.updatePreview)

        # TODO: Tallennuspainikkeen painaminen käynnistää tallennusdialogin ISSUE 9
        self.ui.exportPushButton.clicked.connect(self.saveToCSVFile)

        # RadionButtonit signaalit
        self.ui.commaRadioButton.clicked.connect(self.setSeparator)
        self.ui.semicolonRadioButton.clicked.connect(self.setSeparator)
        self.ui.tabRadioButton.clicked.connect(self.setSeparator)
        self.ui.otherSeparatorRadioButton.clicked.connect(self.setSeparator)
        self.ui.otherSeparatorLineEdit.textChanged.connect(self.forceOtherSeparator)

        # Tekstin tunnistimen valinnan signalit

        self.ui.doubleQuotationRadioButton.clicked.connect(self.setQualifier)
        self.ui.semiQuoteRadioButton.clicked.connect(self.setQualifier)
        self.ui.withoutRadioButton.clicked.connect(self.setQualifier)
        self.ui.otherQualiferRadioButton.clicked.connect(self.setQualifier)
        self.ui.otherQualiferLineEdit.textChanged.connect(self.forceOtherQualifier)

    def setQualifier(self):
        # Kun käyttäjä valitsee erottimen, pakotetaan
        
        if self.ui.doubleQuotationRadioButton.isChecked():
            self.textIdentifier = '"'
        elif self.ui.semiQuoteRadioButton.isChecked():
            self.textIdentifier = "'"
        elif self.ui.withoutRadioButton.isChecked():
            self.textIdentifier = ''
        elif self.ui.otherQualiferRadioButton.isChecked():
            self.textIdentifier = self.ui.otherQualiferLineEdit.text().strip()
        else:
            self.textIdentifier = '"'


        statusbarMessage = f'Tekstin tunnistin: {self.textIdentifier}'
        self.ui.statusbar.showMessage(statusbarMessage, 5000) # Näytetään viesti 5 sekuntia

    def forceOtherQualifier(self):
        # Kun käyttäjä syöttää erottimen, pakotetaan
        self.ui.otherQualiferRadioButton.setChecked(True)
        




    def forceOtherSeparator(self):
        # Kun käyttäjä syöttää erottimen, pakotetaan
        
        self.ui.otherSeparatorLineEdit.setEnabled(True)
    
    def setSeparator(self):
        # Kun käyttäjä valitsee erottimen, pakotetaan
        
        if self.ui.commaRadioButton.isChecked():
            self.separator = ','
        elif self.ui.semicolonRadioButton.isChecked():
            self.separator = ';'
        elif self.ui.tabRadioButton.isChecked():
            self.separator = '\t'
        elif self.ui.otherSeparatorRadioButton.isChecked():
            self.separator = self.ui.otherSeparatorLineEdit.text().strip()
        else:
            self.separator = ';'  

        statusbarMessage = f'Erottelija: {self.separator}'
        self.ui.statusbar.showMessage(statusbarMessage, 5000) # Näytetään viesti 5 sekuntia  
   
   
    # OHJELMOIDUT SLOTIT
    # ------------------
    def connectDb(self):

        # Päivitetään tietokantaan liittyvät ominaisuudet syötettyjen tietojen perusteella
        # self.serverName = self.ui.serverLineEdit.text()
        # self.portNumber = self.ui.portLineEdit.text()
        # self.databaseName = self.ui.databaseLineEdit.text()
        # self.userName = self.ui.userNameLineEdit.text()
        # self.password = self.ui.passwordLineEdit.text()


        self.serverName = '127.0.0.1'
        self.portNumber = 5432
        self.databaseName = 'testaus'
        self.userName = 'postgres'
        self.password = 'Q2werty'

        # Muodostetaan asetussanakirja
        settingsDictionary = {'server': self.serverName,
                      'port': self.portNumber,
                      'database': self.databaseName,
                      'userName': self.userName,
                      'password': self.password}
        
        # Luodaan tietokantayhteysolio
        try:
            dbConnection = dbOperations.DbConnection(settingsDictionary)
            table = 'information_schema.tables'
            columns = ['table_type']
            filterText = f"table_schema NOT IN ('information_schema', 'pg_catalog')"

            objectTypes = dbConnection.filterDistinctColumsFromTable(table,columns,filterText)
            self.ui.statusbar.showMessage('Yhteyden muodostus tietokantaan onnistui')
            print(objectTypes)

            # Tehdään monikkolistasta merkkijonolista
            self.ui.objectTypeComboBox.clear() # Tyhjentää vanhat vaihtoehdot
            cleanedObjectTypeList = ['Valitse']
            for value in objectTypes:
                objectType = value[0] # Ottaa monikon ensimmäisen arvon
                cleanedObjectTypeList.append(objectType)
            
            # Lisätään lista yhdistelmäruutuun
            self.ui.objectTypeComboBox.addItems(cleanedObjectTypeList)
        
        except Exception as e:
            self.errorWindowTitle = 'Yhteys tietokantaan ei onnistunut'
            self.errorText = 'Yhteyden muodostuksessa tapahtui virhe'
            self.errorDetails = str(e)
            self.openWarning()
        

    # TODO: Tee slotti, joka hakee information_schema-nimiavaruudesta listan
    # tietokantaobjekteista, jotka eivät ole information_schemassa tai pg_catalogissa
    #  a) tee  kysely ensin SQL-kielellä PGAdminissa ja kokeile
    #  b) käytä filterColumnsFromTable metodia tietojen hakemiseen ja tallenna ne
    #     pääohjelmaan muuttujaan self.tablesAndViews
    def getObjectNames(self):

        # Muodostetaan asetussanakirja
        settingsDictionary = {'server': self.serverName,
                      'port': self.portNumber,
                      'database': self.databaseName,
                      'userName': self.userName,
                      'password': self.password}
        
         # Luodaan tietokantayhteysolio
        try:
            dbConnection = dbOperations.DbConnection(settingsDictionary)
            table = 'information_schema.tables'
            columns = ['table_schema','table_name']
            tableType = self.ui.objectTypeComboBox.currentText()

            filterText  = f"table_type = '{tableType}' AND table_schema NOT IN ('information_schema', 'pg_catalog')"

            objectNames = dbConnection.filterColumsFromTable(table,columns,filterText)
            self.ui.statusbar.showMessage('Haettiin tietokantaobjektien nimet')
            
            print(objectNames)

            # Tehdään monikkolistasta merkkijonolista
            self.ui.objectNameComboBox.clear() # Tyhjentää vanhat vaihtoehdot
            cleanedObjectNameList = ['Valitse']
            for value in objectNames:
                objectSchema = value[0] # Ottaa monikon ensimmäisen arvon -> skeema
                objectName = value[1] # Ottaa monikon toisen arvon -> objektin nimi
                objectFullName = f'{objectSchema}.{objectName}' # Objektin polku: skeema.nimi
                cleanedObjectNameList.append(objectFullName)
            
            # Lisätään lista yhdistelmäruutuun
            self.ui.objectNameComboBox.addItems(cleanedObjectNameList)
        
        
        except Exception as e:
            self.errorWindowTitle = 'Yhteys tietokantaobjektien haku ei onnistunut'
            self.errorText = 'Objektien nimien haku ei onnistunut'
            self.errorDetails = str(e)
            self.openWarning()
            

    def updatePreview(self):
        settingsDictionary = {
            'server': self.serverName,
            'port': self.portNumber,
            'database': self.databaseName,
            'userName': self.userName,
            'password': self.password
        }
        
        currentObjectSelection = self.ui.objectNameComboBox.currentText()

        # Clear table if no selection
        if not currentObjectSelection or currentObjectSelection == 'Valitse':
            self.ui.previewTableWidget.clear()
            self.ui.previewTableWidget.setRowCount(0)
            self.ui.previewTableWidget.setColumnCount(0)
            return

        try:
            # Establish database connection
            dbConnection = dbOperations.DbConnection(settingsDictionary)
            
            # Get column names from database metadata
            headerRow = dbConnection.getColumnNames(currentObjectSelection)
            columnCount = len(headerRow)
            
            # Set column headers
            self.ui.previewTableWidget.setColumnCount(columnCount)
            self.ui.previewTableWidget.setHorizontalHeaderLabels(headerRow)
            
            # Fetch data rows
            self.resultSet = dbConnection.readAllColumnsFromTable(currentObjectSelection)
            numberOfRows = len(self.resultSet)
            self.ui.previewTableWidget.setRowCount(numberOfRows)

            # Populate data if available
            if numberOfRows > 0:
                for row_idx, row_data in enumerate(self.resultSet):
                    for col_idx, cell_data in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(cell_data))
                        self.ui.previewTableWidget.setItem(row_idx, col_idx, item)

        except Exception as e:
            self.ui.statusbar.showMessage(f"Error: {str(e)}")
            self.ui.previewTableWidget.clear()
            self.ui.previewTableWidget.setRowCount(0)
            self.ui.previewTableWidget.setColumnCount(0)
        

    def createCSVdata(self, separator=';', textIdentifier='"'):
        headerRow = ''
        for item in self.columnNamesList:
            headerRow = headerRow + item + separator

        # Poistetaan viimeinen erottelija
        headerRow = headerRow[:-1] # Poistetaan viimeisen sarakkeen jälkeen tuleva erotusmerkki
        # Lisätään rivinvaihto
        headerRow = headerRow + '\\n'
        print('Otsikot:', headerRow)
        # print('Data', dataRows)

        dataRows = self.resultSet
        dataRows = ''
        dataRow= ''
        for row in self.resultSet:
            print('Rivi:', row)

            for columnValue in row:
                typeOfColumn = type(str(columnValue))
                print('Tyyppi:', typeOfColumn)
                dataRow += str(columnValue) + separator
            
        # Poistetaan viimeinen erottelija
        dataRow= dataRow[:-1] # Poistetaan viimeisen sarakkeen jälkeen tuleva erotusmerkki
        # Lisätään rivinvaihto
        dataRows += dataRow + '\\n'
        print('Tiedot:', dataRows)
        


    # Tallennus CSV-tiedostoksi
    def saveToCSVFile(self):
        
        # Avataan tallennusdialogi oletuskanisona on käyttäjän tiedostot-kansio
        defaultFileName = f'{self.defaultFolder}{self.ui.objectNameComboBox.currentText()}'
        csvFileNameAndType = QtWidgets.QFileDialog.getSaveFileName(self, "Tallenna tiedosto",
                           defaultFileName,
                           ("CSV files (*.csv);;TSV files (*.tsv);;Text files (*.txt)"))
 
        # Otetaan monikosta polku ja tiedoston nimi
        csvFileName = csvFileNameAndType[0]

        data = f"'Erkki'; 'Esimerkki'; 55 \\n"

        # Avataan tiedosto kirjoittamista varten
        self.createCSVdata(';', '"')
        with open(csvFileName, 'wt') as fileToWrite:
            fileToWrite.write(data)

        # Nollataan tiedot onnistuneen tallennuksen jälkeen
        self.resultSet = []
        self.columnNamesList = []

    # Virheilmoitusdialogi
    def openWarning(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(self.errorWindowTitle)
        msgBox.setText(self.errorText)
        msgBox.setDetailedText(self.errorDetails)
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


    