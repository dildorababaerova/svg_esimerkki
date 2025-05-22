# PYSIDE6-SOVELLUS POSTGRESQL-NÄKYMIEN TIETOJEN TALLENTAMISEEN
# CSV- JA TSV-TIEDOSTOIHIN
# ============================================================


# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ----------------------------------
# import os # Polkumääritykset
import os
import csv
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


        # Oletusasetukset

        self.defaultFolder = f'{os.path.expanduser("~")}/Documents/'





        # OHJELMOIDUT SIGNAALIT
        # ---------------------

       # Kun painetaan Testaa-painiketta, näytetään tilarivillä tulos ja
        # päivtetään objektityypin valinnat. Jos virhe, näyteään msgbox
        # Painike asettaa tietokantaparametrit ja yhteysmerkkijonon

        self.ui.testConnectionPushButton.clicked.connect(self.connectDb)
        
        # TODO: Kun poistutaan objektityypin valinnasta, haetaan tyypin objketilista
        # ja päivitetään objektin nimi -valinnat ISSUE 13
        self.ui.objectTypeComboBox.currentIndexChanged.connect(self.getObjectNames)


        # TODO: Kun poistutaan / valinta on muuttunut objektilistasta 
        # näyteään päivitetään esikatselu ja näytetään Tallenna-painike
        self.ui.getDataPushButton.clicked.connect(self.updatePreview)

        # TODO: Tallennuspainikkeen painaminen käynnistää tallennusdialogin ISSUE 9

         # TODO: Tallennuspainikkeen painaminen käynnistää tallennusdialogin ISSUE 9
        self.ui.exportPushButton.clicked.connect(self.saveToCSVFile)



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
            # self.ui.objectTypeComboBox.currentTextChanged.connect(
            #     lambda: self.updateObjectNames(self.dbConnection))
            
            
            
            self.ui.statusbar.showMessage('Connection successful')
        
        except Exception as e:
            print('Connection failed')
            print(e)
            self.ui.statusbar.showMessage('Connection failed: ' + str(e))

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

            objectNames = dbConnection.filterDistinctColumnsFromTable(table,columns,filterText)
            self.ui.statusbar.showMessage('Haettiin tietokantaobjektien nimet')
            
            print(objectNames)

            # Tehdään monikkolistasta merkkijonolista
            self.ui.objectNameComboBox.clear() # Tyhjentää vanhat vaihtoehdot


            cleanedObjectNameList = ['Valitse']
            
            # Optimal versio!
            # cleanedObjectTypes = [obj[0] for obj in objectTypes]
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
            print('Virhe objektin nimien haussa')
            print(e)

    def updatePreview(self):

        # Muodostetaan asetussanakirja
        settingsDictionary = {'server': self.serverName,
                      'port': self.portNumber,
                      'database': self.databaseName,
                      'userName': self.userName,
                      'password': self.password}
        
        # Luetaan valitun tietokantaobjektin skeema ja nimi
        currentObjectSelection = self.ui.objectNameComboBox.currentText()
        print('Valittu tietokantaobjekti:', currentObjectSelection)
        # Luodaan tietokantayhteysolio

        if currentObjectSelection == 'Valitse' or currentObjectSelection == '':
            self.ui.statusbar.showMessage('Valitse ensin tietokantaobjekti')
            self.ui.previewTableWidget.clear()
            self.ui.previewTableWidget.setRowCount(0)
            self.ui.previewTableWidget.setColumnCount(0)
            self.ui.previewTableWidget.setHorizontalHeaderLabels([])
            self.ui.statusbar.showMessage('Tietoa puuttuu tietokantaobjektissa')
            return
        try:
            dbConnection2 = dbOperations.DbConnection(settingsDictionary)
            self.resultSet = dbConnection2.readAllColumnsFromTable(currentObjectSelection)
            self.ui.statusbar.showMessage('Haettiin tietokantaobjektin ' + currentObjectSelection + ' tiedot')
            print('TULOSJOUKKO', self.resultSet)
    
        except:
            pass
        

        # Tyhjennetään vanhat tiedot käyttöliittymästä ennen uusien lukemista tietokannasta
        self.ui.previewTableWidget.clear()

        # Määritellään taulukkoelementin otsikot
        try:
            # Tulosjoukon rivimäärä
            numberOfRows = len(self.resultSet)
            self.ui.previewTableWidget.setRowCount(numberOfRows)

            # Tulosjoukon sarakemäärä
            columnCount = len(self.resultSet[0])
            self.ui.previewTableWidget.setColumnCount(columnCount)
            dbConnection = dbOperations.DbConnection(settingsDictionary)
            self.headerRow = dbConnection.getColumnNames(currentObjectSelection)
            self.ui.previewTableWidget.setHorizontalHeaderLabels(self.headerRow)

            # Asetetaan taulukon solujen arvot
            for row in range(numberOfRows): # Luetaan listaa riveittäin
                for column in range(len(self.resultSet[row])): # Luetaan monikkoa sarakkeittain
                    
                    # Muutetaan merkkijonoksi ja QTableWidgetItem-olioksi
                    data = QtWidgets.QTableWidgetItem(str(self.resultSet[row][column])) 
                    self.ui.previewTableWidget.setItem(row, column, data)
                    self.ui.previewTableWidget.setHorizontalHeaderLabels(self.headerRow)
        
        except Exception as e:
            pass   

        
            
    def createCSVFile(self, separator=',', textDelimiter= "'"):
        # Luodaan tiedosto ja kirjoitetaan siihen CSV-muotoista dataa
        # csvFileName = 'test.csv'
        print(f"CREATECSV {self.headerRow} + {separator} + {textDelimiter}")
        
        
        
    
    def saveToCSVFile(self):
        # Luodaan tiedosto ja kirjoitetaan siihen CSV-muotoista dataa
        # csvFileName = 'test.csv'

        

        defaultFileName = f"{self.defaultFolder}{self.ui.objectNameComboBox.currentText()}"
        csvFileNameAndType = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                        defaultFileName,
                        ("CSV files (*.csv);;TSV files (*.tsv);;Text files (*.txt)"),
                        # ("Erotellut tiedostot (*.csv *.tsv *.txt)")
                         )
        print(csvFileNameAndType)



        csvFileName = csvFileNameAndType[0]

        selected_filter = csvFileNameAndType[1]

        print('Selected filter:', selected_filter)
        if not csvFileName:
            self.ui.statusbar.showMessage('Tallennus peruutettu')
            return
        
        # data = f"'Erkki','Kalle','Matti'"

        # with open(csvFileName, 'wt', ) as fileToWrite:
        #     fileToWrite = csv.writer(data)
        #     fileToWrite.writerow(data)
        #     print('Tiedosto kirjoitettu onnistuneesti')



        with open(csvFileName, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            
            # Kirjoitetaan otsikkorivi (header)
            if hasattr(self, 'headerRow'):
                writer.writerow(self.headerRow)
            
            # Kirjoitetaan data
            if hasattr(self, 'resultSet') and self.resultSet:
                for row in self.resultSet:
                    writer.writerow(row)
                
                self.ui.statusbar.showMessage(f'Tiedosto tallennettu: {csvFileName}')
                self.defaultFolder = os.path.dirname(csvFileName)






        # if csvFileName[0] != '':
        #     # Tiedoston tallennus onnistui
        #     self.ui.statusbar.showMessage('Tallennus onnistui')
        #     print('Tallennus onnistui')
        # else:
        #     # Tiedoston tallennus epäonnistui
        #     self.ui.statusbar.showMessage('Tallennus epäonnistui')
        #     print('Tallennus epäonnistui')

        #     file_path = csvFileName[0]
        #     selected_filter = csvFileName[1]
        #     print('Selected filter:', selected_filter)
            
        #     if not file_path:
        #         self.ui.statusbar.showMessage('Tallennus peruutettu')
        #         return

        #     try:
        #         # Määritellään erotin tiedostotyypin mukaan
        #         if 'CSV' in selected_filter:
        #             delimiter = ','
        #             file_extension = '.csv'
        #         elif 'TSV' in selected_filter:
        #             delimiter = '\t'
        #             file_extension = '.tsv'
        #         else:
        #             delimiter = ','
        #             file_extension = '.txt'

        #         # Varmistetaan tiedostopääte
        #         if not file_path(file_extension):
        #             file_path += file_extension

        #         # Kirjoitetaan data tiedostoon
        #         with open(file_path, 'w', newline='', encoding='utf-8') as file:
        #             writer = csv.writer(file, delimiter=delimiter)
                    
        #             # Kirjoitetaan otsikkorivi (header)
        #             if hasattr(self, 'header_row'):
        #                 writer.writerow(self.header_row)
                    
        #             # Kirjoitetaan data
        #             if hasattr(self, 'resultSet') and self.resultSet:
        #                 for row in self.resultSet:
        #                     writer.writerow(row)
                        
        #                 self.ui.statusbar.showMessage(f'Tiedosto tallennettu: {file_path}')
        #                 self.defaultFolder = os.path.dirname(file_path)  # Päivitetään oletuskansio
        #             else:
        #                 self.ui.statusbar.showMessage('Ei tallennettavaa dataa')

        #     except Exception as e:
        #         self.ui.statusbar.showMessage(f'Tallennus epäonnistui: {str(e)}')
        #         print(f'Virhe tallennuksessa: {e}')

            
            
           
            

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