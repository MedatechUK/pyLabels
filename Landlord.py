#region "Imports"

import sys , os, copy , uuid , json , shutil
import pickle , re
from importlib import util , resources
from io import BytesIO
from pathlib import Path

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtWidgets

from reportlab.lib.colors import *
from reportlab.graphics.shapes import Rect
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.units import mm
from reportlab.graphics import shapes
from reportlab.lib import utils
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools import ttLib

from decimal import Decimal
mm = Decimal(mm)

from MedatechUK.Landlord.label import labelDef , sType
from MedatechUK.Landlord.UI import UI , MyForm , CustomSlider , OkOnlyDialog
from MedatechUK.Landlord import Icons 

import barcode
from barcode.writer import ImageWriter
from barcode import generate
import pyqrcode

import labels

#endregion

class LandlordUI(UI):

#region Methods"

    def tickDocked(self):
        self.btnLabels.setChecked(self.dockLabels.isVisible())
        self.btnSettings.setChecked(self.dockSettings.isVisible())

    def setUI(self,enabled):
        hasfile = "l" in dir(self)
        self.slider.setEnabled(hasfile and enabled)
        for i in [i for i in self.dockWidgetContents_3.children() if type(i).__name__ in ["DragButton" , "ClickButton"] ]:
            i.setEnabled(hasfile and enabled)

        if hasfile:
            self.MainWindow.setWindowTitle("Landlord Labels - {}{}".format(self.l.file , "*" if ( self.l.hasChanges or self.labeldefs.hasChanges ) else ""))
        else:
            self.MainWindow.setWindowTitle("Landlord Labels{}".format( "*" if ( self.labeldefs.hasChanges ) else ""))

        self.dockProperties.setVisible(hasfile and enabled)
        self.dockLabels.setVisible(self.btnLabels.isChecked())
        self.dockSettings.setVisible(self.btnSettings.isChecked())

        self.btnOpen.setEnabled(True)
        self.btnNew.setEnabled(True)
        self.btnSaveas.setEnabled(hasfile and enabled)
        self.btnSave.setEnabled(enabled and ( (hasfile and self.l.hasChanges) or self.labeldefs.hasChanges ))
        self.btnPrint.setEnabled(hasfile and enabled and not (self.l.hasChanges or self.labeldefs.hasChanges))

        self.action_Open.setEnabled(self.btnOpen.isEnabled())
        self.action_New.setEnabled(self.btnNew.isEnabled())
        self.actionSave.setEnabled(self.btnSave.isEnabled())
        self.actionSaveAs.setEnabled(self.btnSaveas.isEnabled())
        self.action_Print.setEnabled(self.btnPrint.isEnabled())
        self.actionExit.setEnabled(True)

    def updateTextShape(self):
        for c in [c for c in self.l.c.contents if self.l.ShapeType(c)==sType.text]:
            s = c.__formatStr__
            for p in range(20):
                if "<P" not in s: break
                s = s.replace("<P{}>".format(str(p+1)) , self.l.template.testdata["PAR{}".format( str(p+1) )] )
            c._text = s

    def mkBarcode(self,i,max=None):
        try:
            if not os.path.exists(os.path.join(self.WorkingDir , "tmp")):
                os.makedirs(os.path.join(self.WorkingDir , "tmp"))

            s = i.__formatStr__            
            for p in range(20):
                if "<P" not in s: break
                s = s.replace("<P{}>".format( str(p+1) ) , self.l.template.testdata["PAR{}".format( str(p+1) )] )

            match i.__encoding__:
                case "QRCODE":
                    s = s.replace("<QR>", json.dumps( self.l.template.testdata["QR"] ))
                    qrcode = pyqrcode.create(s)
                    i.path = os.path.join(self.l.WorkingDir , "tmp" , "{}.png".format(i.__filename__))
                    qrcode.png(i.path , scale=8)

                case _:
                    barclass = barcode.get_barcode_class(i.__encoding__)                                           
                    bar = barclass(s, writer=ImageWriter())
                    bar.save(os.path.join(self.l.WorkingDir , "tmp" , i.__filename__))
                    i.path = os.path.join(self.l.WorkingDir , "tmp" , "{}.png".format(i.__filename__))

            img = utils.ImageReader(i.path)
            iw, ih = img.getSize()
            ar = ih / float(iw)                        
            
            if max!=None: # Resize
                i.width = float(iw/mm)
                i.height = float(ih/mm) * ar
                while i.width > max[0] or i.height > max[1]:
                    i.width = i.width - 1
                    i.height = i.width * ar
            else:
                i.height = i.width * ar

            self.statusbar.showMessage("")

        except Exception as e:
            i.path = ""
            self.statusbar.showMessage(e.args[0])

    def drawSelect(self,i=None):

        if 'selection' not in dir(self):
            # Create a Line shape (dotted line)
            self.selection = Rect(-50, -50, 0, 0, fill=True, stroke=True,)
            self.selection.strokeWidth = 2
            self.selection.strokeDashArray = [1,3]
            self.selection.strokeColor = red
            self.selection.fillColor = white
            self.selection.fillOpacity = 0
            self.selection.__name__ = "selection"

        if not self.selection in self.l.c.contents:
            self.l.c.add(self.selection)

        if i!=None:
            bounds = i.getBounds()
            self.selection.width = bounds[2]-bounds[0]
            self.selection.height = bounds[3]-bounds[1]
            self.selection.x = bounds[0]
            self.selection.y = bounds[1]

        else:
            self.selection.x = -50
            self.selection.y = -50
            self.selection.width = 0
            self.selection.height = 0

    def refreshFonts(self , add=True):
        if add:
            font, ok = QFontDialog.getFont(parent=None)
            if ok:
                for f in [f for f in Path("C://windows//fonts" ).glob('**/*') if f.is_file() and f.suffix.upper() == '.TTF']:
                    font_id = QFontDatabase.addApplicationFont(os.path.join( "C://windows//fonts" , f.name))
                    if font_id != -1:
                        if font.family() in QFontDatabase.applicationFontFamilies(font_id):
                            shutil.copy(os.path.join( "C://windows//fonts" , f.name) , os.path.join( self.WorkingDir , f.name ))
                            break

        for f in [f for f in Path(self.WorkingDir ).glob('**/*') if f.is_file() and f.suffix.upper() == '.TTF']:
            raw_name = os.path.join( self.WorkingDir , f.name)
            font = ttLib.TTFont( raw_name )
            pdfmetrics.registerFont(TTFont(font['name'].getDebugName(1), '{}'.format( raw_name )))

    def Props(self,i):
        result = []
        for p in [p for p in dir(i) if not p.startswith("_")]  :
            if getattr(i,p) !=0 and getattr(i,p)!=None :
                match type(getattr(i,p)).__name__:
                    case "method":
                        pass
                    case "str":
                        result.append((p , "'{}'".format(getattr(i,p))))
                    case _:
                        result.append((p , getattr(i,p)))

        return result
    
    def makeFile(self, fname):
        if not os.path.exists(os.path.join(Path(__file__).parent , "pyLabels")):
            os.mkdir(os.path.join(Path(__file__).parent , "pyLabels"))
        
        if not os.path.exists(os.path.join(Path(__file__).parent , "pyLabels", "tmp")):
            os.mkdir(os.path.join(Path(__file__).parent , "pyLabels" , "tmp"))

        if not os.path.exists(os.path.join(Path(__file__).parent , "pyLabels" , fname)):
            res = resources.files("MedatechUK.Landlord")
            fpath = res.joinpath("files/{}".format( fname ))
            with resources.as_file(fpath) as resfile:
                with open(os.path.join(Path(__file__).parent , "pyLabels" , fname), "w") as file:
                    file.write( resfile.read_text() )
                
#endregion

#region "Handlers"

    def connectHandlers(self, MainWindow):

        self.MainWindow = MainWindow
        self.MainWindow.close_Event.connect(lambda: self.MenuClick('closing'))
        self.MainWindow.keyPress_Event.connect(self.windowKeypress)

        self.dockLabels.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                         QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.dockSettings.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                         QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.MainWindow.tabifyDockWidget(self.dockProperties, self.dockSettings )
        self.MainWindow.tabifyDockWidget( self.dockProperties , self.dockLabels )

        # Set the custom widget as the title bar (this hides the default title bar)
        custom_widget = QWidget()
        self.btnDock.setTitleBarWidget(custom_widget)

        self.label.wheel_event.connect(self.Zoom)
        self.label.mouse_click.connect(self.mouse_click)
        self.label.mouse_Move.connect(self.mouse_Move)
        self.label.mouse_drop.connect(self.mouse_drop)
        self.label.right_click.connect(self.right_click)

        self.Progress = QProgressBar()
        self.Progress.setMaximumWidth(200)
        self.Progress.setOrientation(Qt.Orientation.Horizontal)
        self.statusbar.addPermanentWidget(self.Progress)

        self.slider = CustomSlider(Qt.Orientation.Horizontal) # Create a horizontal slider
        self.slider.keyPress_Event.connect(self.key_press)

        self.slider.setRange(50, 400) # Set the range of the slider
        self.slider.setValue(100) # Set the current value

        self.Zoom = QLabel('{} %'.format( str(self.slider.value() )))
        self.Zoom.setMinimumWidth(50)
        self.statusbar.addPermanentWidget(self.Zoom)

        # Set tick position and interval
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(100)
        self.slider.setTracking(True) # Enable tracking

        # Set single step and page step
        self.slider.setSingleStep(25)
        self.slider.setPageStep(50)
        self.slider.setMaximumWidth(200)
        self.slider.setEnabled(False)

        self.statusbar.addPermanentWidget(self.slider) # Add the slider to the status bar
        self.slider.valueChanged.connect(self.render)

        self.btnUp.clicked.connect(lambda: self.key_press(Qt.Key.Key_Up))
        self.btnDown.clicked.connect(lambda: self.key_press(Qt.Key.Key_Down))
        self.btnLeft.clicked.connect(lambda: self.key_press(Qt.Key.Key_Left))
        self.btnRight.clicked.connect(lambda: self.key_press(Qt.Key.Key_Right))
        self.btnDelete.clicked.connect(lambda: self.key_press(Qt.Key.Key_Delete))

        self.btnDeleteShape.mouse_click.connect(self.toolClick)
        self.btnCopyShape.mouse_click.connect(self.toolClick)
        self.btnUpDown.mouse_click.connect(self.toolClick)

        self.btnCopyLabel.mouse_click.connect(self.labelClick)

        self.btnNew.mouse_click.connect(self.MenuClick)
        self.btnOpen.mouse_click.connect(self.MenuClick)
        self.btnSave.mouse_click.connect(self.MenuClick)
        self.btnSaveas.mouse_click.connect(self.MenuClick)
        self.btnPrint.mouse_click.connect(self.MenuClick)

        self.menu_Tools.aboutToShow.connect(self.tickDocked)
        self.action_New.triggered.connect(lambda: self.MenuClick('btnNew'))
        self.action_Open.triggered.connect(lambda: self.MenuClick('btnOpen'))
        self.actionSave.triggered.connect(lambda: self.MenuClick('btnSave'))
        self.actionSaveAs.triggered.connect(lambda: self.MenuClick('btnSaveas'))
        self.action_Print.triggered.connect(lambda: self.MenuClick('btnPrint'))
        self.actionExit.triggered.connect(lambda: self.MenuClick('exit'))

        self.btnRefreshFont.triggered.connect(lambda: self.refreshFonts(add=True))
        self.btnSettings.triggered.connect(lambda: self.MenuClick('btnSettings'))
        self.btnLabels.triggered.connect(lambda: self.MenuClick('btnLabels'))

        self.comboBox.currentIndexChanged.connect(self.objectSelection)
        self.labelCombo.currentIndexChanged.connect(self.labelSelection)

        self.settingsWidget.WorkingDir = self.WorkingDir
    
    def MenuClick(self, action):
        """
        Handle menu click events and perform corresponding actions.

        Args:
            action (str): The action to be performed.

        Returns:
            None
        """

        def reDraw():
            self.drawSelect()
            self.drawCombo()
            self.render()
            self.objectSelection()
            self.dockProperties.raise_()

        def saveDone():
            if "l" in dir(self):
                self.l.hasChanges = False
                self.l.hasFile = True

            if self.labeldefs.hasChanges:
                # Save Spec here
                self.SaveLabelDef()

            self.setUI(True)

        def confirmSaveChanges() -> bool:
            if "l" in dir(self):
                if self.l.hasChanges:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Confirmation")
                    msg_box.setText("Save changes to {}?".format(self.l.file))
                    msg_box.setStandardButtons(
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                    match msg_box.exec():
                        case QMessageBox.StandardButton.Yes:
                            self.MenuClick("btnSave")
                            return True
                        case QMessageBox.StandardButton.Cancel:
                            return False
                        case _:
                            return True
                else:
                    return True
            else:
                if self.labeldefs.hasChanges:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Confirmation")
                    msg_box.setText("Save changes to Label Definitions?")
                    msg_box.setStandardButtons(
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                    match msg_box.exec():
                        case QMessageBox.StandardButton.Yes:
                            saveDone()
                            return True
                        case QMessageBox.StandardButton.Cancel:
                            return False
                        case _:
                            return True
                else:
                    return True

        match action:

            case "btnOpen":
                if confirmSaveChanges():
                    # Create a file dialog
                    file_dialog = QFileDialog()
                    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)  # Choose an existing file

                    # Get the selected file path
                    selected_file, _ = file_dialog.getOpenFileName(
                        None
                        , "Open Label"
                        , os.path.join(Path(__file__).parent, "pylabels")
                        , "Label Files (*.py)"
                    )

                    if os.path.basename(selected_file).lower() == "labelspec.py":
                        self.btnLabels.setChecked(True)
                        self.MenuClick("btnLabels")

                    else:
                        if os.path.exists(selected_file):
                            try:
                                self.l = labelDef(selected_file)
                                reDraw()

                            except Exception as e:
                                d = OkOnlyDialog(title="Error!",
                                                 message="{} is not a valid label file.".format(
                                                     os.path.basename(selected_file)))
                                d.exec()
                        else:
                            d = OkOnlyDialog(title="Error!",
                                message="{} does not exist.".format(os.path.basename(selected_file)))
                            d.exec()

            case "btnNew":
                if confirmSaveChanges():
                    self.l = labelDef()
                    for l in [l for l in self.lspecs if l.default]:
                        setattr(self.l.template, "specs", l)
                        break

                    reDraw()

            case "btnSave":
                if "l" in dir(self):
                    match self.l.hasFile:
                        case False:
                            self.MenuClick("btnSaveas")
                        case _:
                            self.SaveLabel(os.path.join(self.WorkingDir, self.l.file))
                            print("Save Label: {}".format(os.path.join(self.WorkingDir, self.l.file)))
                            pass

                saveDone()

            case "btnSaveas":
                file_dialog = QFileDialog()
                options = QFileDialog.options(file_dialog)
                # options |= QFileDialog.Option.DontUseNativeDialog  # Disable native dialog
                # options |= QFileDialog.Option.DontUseCustomDirectoryIcons  # Disable custom directory icons
                file_dialog.setOptions(options)
                file_name, _ = QFileDialog.getSaveFileName(
                    None,  # Parent widget (can be None)
                    "Save File",  # Dialog title
                    os.path.join(self.WorkingDir, self.l.file),  # Default directory path
                    "Python Labels (*.py)",  # Filter for file types
                    options=options
                )

                if file_name.endswith(".py"):
                    self.l.file = os.path.basename(file_name)
                    print("Save As Label: {}".format(os.path.join(self.WorkingDir, self.l.file)))
                    self.SaveLabel(os.path.join(self.WorkingDir, self.l.file))
                    saveDone()

            case "btnPrint":

                self.btnPrint.setEnabled(False)
                try:
                    sheet = labels.Sheet(self.l.template.specs, self.l.template.draw_label, self.l.template.border)
                    clean = []
                    self.Progress.setRange(0, self.l.template.specs.rows * self.l.template.specs.columns)
                    self.Progress.setValue(0)

                    for repeat in range(self.Progress.maximum()):
                        self.statusbar.repaint()
                        self.Progress.setValue(self.Progress.value() + 1)
                        self.statusbar.showMessage("Printing Label {}".format(str(self.Progress.value())))

                        t = self.l.template.testdata
                        sheet.add_label(t)
                        clean.extend(t["clean"])

                    fn = os.path.join(
                        self.WorkingDir
                        , "tmp"
                        , "preview_{}.pdf".format(self.l.file.split(".")[0])
                    )

                    self.statusbar.showMessage("Saving...")
                    sheet.save(fn)
                    for i in clean:
                        os.remove(i)

                    os.startfile(fn)

                except:
                    pass

                finally:
                    self.statusbar.showMessage("")
                    self.Progress.setValue(0)
                    self.setUI(True)

            case "btnLabels":
                self.dockLabels.setVisible(self.btnLabels.isChecked())
                self.setUI(True)
                self.dockLabels.raise_()

            case "btnSettings":
                self.dockSettings.setVisible(self.btnSettings.isChecked())
                self.setUI(True)
                self.dockSettings.raise_()

            case "exit":
                self.MenuClick("closing")
                if MainWindow.closing: exit()

            case "closing":
                MainWindow.closing = confirmSaveChanges()
                if MainWindow.closing:
                    if "l" in dir(self):
                        self.l.__exit__(None, None, None)

            case _:
                pass

    def toolClick(self, action , pos=None):
        """
        Handle the click event for different tools.

        Args:
            action (str): The action triggered by the tool button.
            pos (QPoint, optional): The position of the click event. Defaults to None.
        """
        def focusShape(Shape):
            self.drawCombo()
            self.comboBox.setCurrentIndex( self.comboBox.findText(Shape.__name__))
            self.objectSelection()

        def nameCheck(ShapeName)->str:
            ShapeName = ShapeName.rstrip()  # Remove trailing spaces
            match = re.match(r"(.*?)(\d+)$", ShapeName)
            if match:
                base_name, num = match.groups()
                _name = "{} {}".format(base_name.rstrip(), str(int(num) + 1))
            else:
                _name = "{} 1".format(ShapeName)

            while self.comboBox.findText(_name) != -1:
                match = re.match(r"(.*?)(\d+)$", _name)
                base_name, num = match.groups()
                _name = "{} {}".format(base_name.rstrip(), str(int(num) + 1))

            return _name

        self.l.hasChanges = True
        match action:
            case "btnAddTextBox":
                newShape = Label( __formatStr__="Some Value" , __name__= nameCheck("Text Box") , boxAnchor = 'nw' , angle = 0 , fontName="Helvetica", fontSize=12 )
                newShape.setOrigin(self.l.c.width * pos.x() , self.l.c.height * pos.y())
                newShape.setText(newShape.__name__)
                self.l.c.add(newShape)
                focusShape(newShape)

            case "btnAddImg":
                newShape = shapes.Image ( self.l.c.width * pos.x() , self.l.c.height * pos.y()-100, 100, 100, os.path.join( ''), __name__ = nameCheck("Image") , __filename__ = "")
                self.l.c.add(newShape)
                focusShape(newShape)

            case "btnAddQR" | "btnAddBarcode" :
                newShape = shapes.Image ( self.l.c.width * pos.x() , self.l.c.height * pos.y(), 100, 100, ''
                    , __name__ = nameCheck( "QRcode" if action=="btnAddQR" else "Barcode" )
                    , __formatStr__= "<QR>" if action=="btnAddQR" else "123123123123" 
                    , __encoding__ = "QRCODE" if action=="btnAddQR" else "EAN13"
                    , __filename__ = "{}".format(uuid.uuid4())
                )
                self.mkBarcode(newShape, (
                    self.l.c.width - (self.l.c.width * pos.x())
                    , self.l.c.height * pos.y()
                ))
                newShape.y = newShape.y - newShape.height
                self.l.c.add(newShape)
                focusShape(newShape)                

            case "btnDeleteShape":
                i = self.l.isShape(self.comboBox.currentText())
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Confirmation")
                msg_box.setText("Are you sure you want to delete shape '{}'?".format(i.__name__))
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

                match msg_box.exec():
                    case QMessageBox.StandardButton.Ok:
                        self.comboBox.setCurrentIndex( self.comboBox.currentIndex() - 1 )
                        self.l.c.contents.remove(i)
                        if self.l.ShapeType(i)==sType.barcode:
                            os.remove(i.path)

                        self.drawCombo()
                        self.objectSelection()                        

                    case _:
                        pass

            case "btnUpDown":
                # Create a context menu
                context_menu = QMenu()

                BringToFront = QAction("Bring To Front", context_menu )
                BringToFront.__name__ = "sendfront"

                MoveBack = QAction("Move Back", context_menu)
                MoveBack.__name__ = "moveback"

                MoveForward = QAction("Move Forward", context_menu)
                MoveForward.__name__ = "moveforward"

                SendToBack = QAction("Send To Back", context_menu)
                SendToBack.__name__ = "sendback"

                for i in [i for i in context_menu.children() if "__name__" in dir(i)]:
                    i.setIcon(QIcon(":/ico/{}".format(i.__name__)))

                i = self.l.isShape(self.comboBox.currentText())
                index = self.l.c.contents.index(i)
                MoveBack.setEnabled(i != self.l.c.contents[0] )
                MoveForward.setEnabled ( i != self.l.c.contents[len(self.l.c.contents)-1] )
                BringToFront.setEnabled( MoveForward.isEnabled() )
                SendToBack.setEnabled ( MoveBack.isEnabled() )

                # Display the context menu
                context_menu.addAction(BringToFront)
                context_menu.addAction(MoveForward)
                context_menu.addSeparator()
                context_menu.addAction(MoveBack)
                context_menu.addAction(SendToBack)
                result = context_menu.exec(QCursor.pos())
                if result != None:
                    match result.__name__:
                        case "sendfront":
                            self.l.c.contents.insert(len(self.l.c.contents)-1, self.l.c.contents.pop(index))
                        case "moveback":
                            self.l.c.contents.insert(index-1, self.l.c.contents.pop(index))
                        case "moveforward":
                            self.l.c.contents.insert(index+1, self.l.c.contents.pop(index))
                        case "sendback":
                            self.l.c.contents.insert(0, self.l.c.contents.pop(index))
                        case _:
                            pass
                    self.drawCombo()

            case "btnCopyShape":
                i = self.l.isShape(self.comboBox.currentText())
                byte_array = QByteArray(pickle.dumps(i))
                mimeData = QMimeData()
                mimeData.setData("application/python-pickle", byte_array)                    
                QGuiApplication.clipboard().setMimeData(mimeData)

            case "paste":
                mimeData = QGuiApplication.clipboard().mimeData()
                if mimeData.hasFormat("application/python-pickle"):
                    byte_array = mimeData.data("application/python-pickle")
                    i = pickle.loads(byte_array)
                    i.__name__ = nameCheck(i.__name__)
                    i.x = self.l.c.width * pos.x() 
                    i.y = self.l.c.height * pos.y()
                    if self.l.ShapeType(i)!=sType.text: i.y = i.y - i.height
                    if self.l.ShapeType(i)==sType.barcode: i.__filename__ = "{}".format(uuid.uuid4())
                    self.l.c.add(i)
                    # Clear the clipboard
                    QGuiApplication.clipboard().clear()                    
                    focusShape(i)

            case _:
                pass

        self.render()

#region "Mouse Handlers"

    def Zoom(self , amount):
        self.slider.setValue(self.slider.value() + amount)

    def mouse_click(self, pos):
        self.dockProperties.raise_()
        hit = []
        for i in [i for i in self.l.c.contents if self.l.ShapeType(i)!=sType.select]:
            bounds = i.getBounds()
            rx = bounds[0] / self.l.c.width
            ry = bounds[1] / self.l.c.height
            rw = (bounds[2]-bounds[0]) / self.l.c.width
            rh = (bounds[3]-bounds[1]) / self.l.c.height
            if (rx <= pos.x() <= rx + rw) and (ry <= pos.y() <= ry + rh):
                hit.append(i)
        match len(hit):
            case 0:
                self.comboBox.setCurrentIndex( self.comboBox.findText("Label"))
            case 1:
                self.comboBox.setCurrentIndex( self.comboBox.findText(hit[0].__name__))
            case _:
                pass

        self.objectSelection()

    def mouse_Move(self,pos):
        self.l.hasChanges = True
        for i in [i for i in self.l.c.contents if i.__name__== self.comboBox.currentText()]:
            i.x = self.l.c.width * ((i.x / self.l.c.width) - pos.x())
            i.y = self.l.c.height * ((i.y / self.l.c.height) - pos.y())
            self.objectSelection()
            self.render()
            break

    def mouse_drop(self, btn, pos):
        self.l.hasChanges = True
        self.toolClick(btn , pos)

    def windowKeypress(self , key):
        match "l" in dir(self) and self.dockProperties.isFloating:
            case True:
                self.key_press(key)

    def key_press(self, key):
        def keyHandled():
            self.l.hasChanges = True
            self.render()
            self.objectSelection()

        if "l" in dir(self):
            i = self.l.isShape(self.comboBox.currentText())
            if i !=None:
                match key:
                    case Qt.Key.Key_Left:
                        i.x = i.x - 1
                        keyHandled()
                    case Qt.Key.Key_Right:
                        i.x = i.x + 1
                        keyHandled()
                    case Qt.Key.Key_Up:
                        i.y = i.y + 1
                        keyHandled()
                    case Qt.Key.Key_Down:
                        i.y = i.y - 1
                        keyHandled()
                    case Qt.Key.Key_Delete:
                        self.toolClick("btnDeleteShape")
                        keyHandled()

    def right_click(self, pos):

        self.mouse_click(pos)
        context_menu = QMenu()

        copy = QAction("Copy", context_menu )
        copy.__name__ = "copy"

        paste = QAction("Paste", context_menu )
        paste.__name__ = "paste"

        BringToFront = QAction("Bring To Front", context_menu )
        BringToFront.__name__ = "sendfront"

        MoveBack = QAction("Move Back", context_menu)
        MoveBack.__name__ = "moveback"

        MoveForward = QAction("Move Forward", context_menu)
        MoveForward.__name__ = "moveforward"

        SendToBack = QAction("Send To Back", context_menu)
        SendToBack.__name__ = "sendback"

        delete = QAction("Delete", context_menu )
        delete.__name__ = "delete"

        for i in [i for i in context_menu.children() if "__name__" in dir(i)]:
            i.setIcon(QIcon(":/ico/{}".format(i.__name__)))

        mimeData = QGuiApplication.clipboard().mimeData()        
        paste.setEnabled(mimeData.hasFormat("application/python-pickle"))

        i = self.l.isShape(self.comboBox.currentText())
        if i != None:
            index = self.l.c.contents.index(i)
            MoveBack.setEnabled(i != self.l.c.contents[0] )
            MoveForward.setEnabled ( i != self.l.c.contents[len(self.l.c.contents)-1] )
            BringToFront.setEnabled( MoveForward.isEnabled() )
            SendToBack.setEnabled ( MoveBack.isEnabled() )

            # Display the context menu
            context_menu.addAction(copy)
            context_menu.addAction(paste)
            context_menu.addSeparator()
            context_menu.addAction(BringToFront)
            context_menu.addAction(MoveForward)
            context_menu.addSeparator()
            context_menu.addAction(MoveBack)
            context_menu.addAction(SendToBack)
            context_menu.addSeparator()
            context_menu.addAction(delete)
        
        else:
            if mimeData.hasFormat("application/python-pickle"):
                context_menu.addAction(paste)

        result = context_menu.exec(QCursor.pos())
        if result != None:
            match result.__name__:
                case "sendfront":
                    self.l.c.contents.insert(len(self.l.c.contents)-1, self.l.c.contents.pop(index))
                case "moveback":
                    self.l.c.contents.insert(index-1, self.l.c.contents.pop(index))
                case "moveforward":
                    self.l.c.contents.insert(index+1, self.l.c.contents.pop(index))
                case "sendback":
                    self.l.c.contents.insert(0, self.l.c.contents.pop(index))
                case "delete":
                    self.toolClick("btnDeleteShape")
                case "paste":
                    self.toolClick("paste", pos)
                case "copy":
                    self.toolClick("btnCopyShape")
                case _:
                    pass

            self.drawCombo()

#endregion

#region "Property Tool"

    def render(self):
        self.setUI(True)
        self.updateTextShape()
        self.drawSelect(self.l.isShape(self.comboBox.currentText()))

        pixmap = QPixmap()
        pixmap.loadFromData(BytesIO(self.l.render()).getvalue())

        self.label.setScaledContents(False)
        scaled = pixmap.scaledToWidth(int(self.slider.value() * (pixmap.width() / 100)), Qt.TransformationMode.SmoothTransformation)
        self.label.pixmap = scaled
        self.label.setPixmap(scaled)
        self.Zoom.setText("{} %".format( str(self.slider.value()) ))
        self.label.repaint()

    def objectSelection(self):
        i = self.l.isShape(self.comboBox.currentText())

        self.btnDeleteShape.setEnabled( i !=None )
        self.btnUpDown.setEnabled(i !=None )
        self.btnCopyShape.setEnabled(i !=None and self.l.ShapeType(i) != sType.qr )

        match i !=None :
            case True:
                match self.l.c.contents.index(i):
                    case 0:
                        self.l.c.contents.insert(0, self.l.c.contents.pop(self.l.c.contents.index(self.selection)))
                    case _:
                        self.l.c.contents.insert(self.l.c.contents.index(i)-1, self.l.c.contents.pop(self.l.c.contents.index(self.selection)))

                p = self.l.Params(i)

            case _:
                match self.comboBox.currentText():
                    case _:
                        p = self.labelParams()

        self.propertyWidget.setParameters(p,showTop=False)
        for child in p.children():
            for child in child.childs:
                child.sigValueChanged.connect(self.propertyChange)

        self.render()

    def propertyChange(self, _param, _value):
        self.l.hasChanges = True
        i = self.l.isShape(self.comboBox.currentText())
        match self.l.ShapeType(i):
            case sType.label:
                match _param.opts["name"].lower():
                    case "labelstock":
                        for l in [l for l in self.lspecs if l.name == _value]:
                            self.l.c.width = float(l.label_width*mm)
                            self.l.c.height = float(l.label_height*mm)
                            self.l.template.specs = l
                            self.objectSelection()
                            break

                    case _:
                        self.l.template.testdata [ _param.opts["name"] ] = _value
                        for c in [c for c in self.l.c.contents if "__formatStr__" in dir(c)]:
                            s = c.__formatStr__
                            for p in range(20):
                                s = s.replace("<P{}>".format(str(p+1)) , self.l.template.testdata["PAR{}".format( str(p+1) )] )

                            match self.l.ShapeType(c):
                                case sType.text:
                                    c._text = s

                                case sType.barcode:
                                    self.mkBarcode(c)

            case sType.barcode:
                match _param.opts["name"]:
                    case "Name":
                        if self.comboBox.findText(_value) < 0:
                            self.comboBox.setItemText(self.comboBox.currentIndex(), _value)
                            i.__name__ = _value
                        else:
                            d = OkOnlyDialog(title = "Warning!", message = "Shape {} already exists!".format(_value))
                            d.exec()
                            self.objectSelection()

                    case "__encoding__" | "__formatStr__":
                        if _param.opts["name"] == "__formatStr__": i.__formatStr__ = _value
                        if _param.opts["name"] == "__encoding__": i.__encoding__ = _value
                        self.mkBarcode(i)

                    case "width" | "height":
                        ar = i.height / float(i.width)
                        match _param.opts["name"]:
                            case "width":
                                i.width = _value
                                i.height = _value * ar
                            case "height":
                                i.height =  _value
                                i.width =  _value / ar
                        self.objectSelection()

                    case _:
                        setattr(i, _param.opts["name"] , _value)

            case _:
                match str(type(_value)):
                    case "<class 'PyQt6.QtGui.QColor'>":
                        red, green, blue , alpha = _value.getRgb()
                        if alpha>0:
                            setattr(i, _param.opts["name"] , Color( red,green,blue ))
                        else:
                            setattr(i, _param.opts["name"] , None ) #Color(255,255,255))
                    case _ :
                        match _param.opts["name"]:
                            case "Name":
                                if self.comboBox.findText(_value) < 0:
                                    self.comboBox.setItemText(self.comboBox.currentIndex(), _value)
                                    i.__name__ = _value
                                else:
                                    d = OkOnlyDialog(title = "Warning!", message = "Shape {} already exists!".format(_value))
                                    d.exec()
                                    self.objectSelection()

                            case "filename":
                                img = utils.ImageReader(os.path.join(self.l.WorkingDir , _value))
                                iw, ih = img.getSize()
                                i.width = float(iw/mm)
                                i.height = float(ih/mm) * ih / float(iw)
                                i.__filename__ = _value
                                i.path = os.path.join(self.l.WorkingDir , _value)
                                self.objectSelection()

                            case _:
                                setattr(i, _param.opts["name"] , _value)

        self.render()

    def drawCombo(self):
        """
        Populates a combo box with items from a list and sets the selected item based on the current text.

        Returns:
            None
        """
        sel = self.comboBox.currentText()
        if len(sel) == 0: sel = "Label"
        self.comboBox.clear()
        f = False
        self.comboBox.addItem("Label")
        for i in [i for i in self.l.contents() if self.l.ShapeType(i) != sType.select]:
            self.comboBox.addItem(i.__name__)
            if i.__name__ == sel: f = True
        if not f: sel = "Label"
        self.comboBox.setCurrentIndex(self.comboBox.findText(sel))

    def labelParams(self):
        parameters = []

        labelStock = []
        for i in self.lspecs:
            labelStock.append(i.name)
            if self.l.template.specs.name == i.name:
                sel = i

        parameters.append({'name': 'Label',
            'type': 'group',
            'children': [
                {'title': 'Path' , 'name': 'path', 'type': 'str', 'value': self.l.file , 'readonly': True},
                {'title': 'LabelStock' ,'name': 'labelstock', 'type': 'list', 'limits': labelStock , 'value': sel.name, 'siPrefix': True, 'suffix': 'mm', 'readonly': False},
                {'title': 'Width' ,'name': 'width', 'type': 'float', 'value': sel.label_width, 'siPrefix': True, 'suffix': 'mm', 'readonly': True},
                {'title': 'Height' ,'name': 'height', 'type': 'float', 'value': sel.label_height, 'siPrefix': True, 'suffix': 'mm', 'readonly': True}
            ]
        })

        parameters.append({'name': 'Test Data',
            'type': 'group',
            'children': [
                {'name': 'PAR1', 'type': 'str', 'value': (self.l.template.testdata["PAR1"]), 'readonly': False},
                {'name': 'PAR2', 'type': 'str', 'value': (self.l.template.testdata["PAR2"]) , 'readonly': False},
                {'name': 'PAR3', 'type': 'str', 'value': (self.l.template.testdata["PAR3"]) , 'readonly': False},
                {'name': 'PAR4', 'type': 'str', 'value': (self.l.template.testdata["PAR4"]) , 'readonly': False},
                {'name': 'PAR5', 'type': 'str', 'value': (self.l.template.testdata["PAR5"]) , 'readonly': False},
                {'name': 'PAR6', 'type': 'str', 'value': (self.l.template.testdata["PAR6"]) , 'readonly': False},
                {'name': 'PAR7', 'type': 'str', 'value': (self.l.template.testdata["PAR7"]) , 'readonly': False},
                {'name': 'PAR8', 'type': 'str', 'value': (self.l.template.testdata["PAR8"]) , 'readonly': False},
                {'name': 'PAR9', 'type': 'str', 'value': (self.l.template.testdata["PAR9"]) , 'readonly': False},
                {'name': 'PAR10', 'type': 'str', 'value': (self.l.template.testdata["PAR10"]) , 'readonly': False},
                {'name': 'PAR11', 'type': 'str', 'value': (self.l.template.testdata["PAR11"]) , 'readonly': False},
                {'name': 'PAR12', 'type': 'str', 'value': (self.l.template.testdata["PAR12"]) , 'readonly': False},
                {'name': 'PAR13', 'type': 'str', 'value': (self.l.template.testdata["PAR13"]) , 'readonly': False},
                {'name': 'PAR14', 'type': 'str', 'value': (self.l.template.testdata["PAR14"]) , 'readonly': False},
                {'name': 'PAR15', 'type': 'str', 'value': (self.l.template.testdata["PAR15"]) , 'readonly': False},
                {'name': 'PAR16', 'type': 'str', 'value': (self.l.template.testdata["PAR16"]) , 'readonly': False},
                {'name': 'PAR17', 'type': 'str', 'value': (self.l.template.testdata["PAR17"]) , 'readonly': False},
                {'name': 'PAR18', 'type': 'str', 'value': (self.l.template.testdata["PAR18"]) , 'readonly': False},
                {'name': 'PAR19', 'type': 'str', 'value': (self.l.template.testdata["PAR19"]) , 'readonly': False},
                {'name': 'PAR20', 'type': 'str', 'value': (self.l.template.testdata["PAR20"]) , 'readonly': False}
            ]
        })

        return Parameter.create(name='params', type='group', children=parameters)

#endregion

#region "LabelStock Tool"

    def loadLabelDef(self):
        self.WorkingDir = Path(__file__).parent
        self.WorkingDir = os.path.join(self.WorkingDir , "pyLabels")

        spec = util.spec_from_file_location("label.labeldefs", os.path.join(self.WorkingDir , '{}.py'.format( "LabelSpec" )))
        self.labeldefs = util.module_from_spec(spec)
        sys.modules["label.labeldefs"] = self.labeldefs
        spec.loader.exec_module(self.labeldefs)

        self.lspecs = []
        for lspec in [lspec for lspec in dir(self.labeldefs) if not lspec.startswith("__") and lspec.lower() != "labels"] :
            match getattr(getattr(self.labeldefs , lspec), "default"):
                case True:
                    self.lspecs.insert(0 , getattr(self.labeldefs, lspec))
                case _:
                    self.lspecs.append(getattr(self.labeldefs, lspec))

        self.labeldefs.hasChanges = False

        self.drawLabelCombo()
        self.labelSelection()

    def labelSelection(self):
        for l in [l for l in self.lspecs if l.name==self.labelCombo.currentText()]:
            p = self.labelDefParams( l )
            self.labelWidget.setParameters(p,showTop=False)
            for child in p.children():
                for child in child.childs:
                    child.sigValueChanged.connect(self.labelChange)

    def drawLabelCombo(self):
        for i in [i for i in self.lspecs]:
            if self.labelCombo.findText(i.name) == -1:
                self.labelCombo.addItem(i.name)

    def labelChange(self, _param, _value):
        match _param.opts["name"]:
            case "name":
                if self.labelCombo.findText(_value) < 0:
                    for i in [i for i in self.lspecs if i.name == self.labelCombo.currentText()]:
                        i.name = _value
                    self.labelCombo.clear()
                    self.drawLabelCombo()
                    self.labelCombo.setCurrentIndex(self.labelCombo.findText(_value))
                    self.labeldefs.hasChanges = True

                else:
                    d = OkOnlyDialog(title = "Warning!", message = "{} already exists!".format(_value))
                    d.exec()                    

            case _ :
                try:
                    for i in [i for i in self.lspecs if i.name==self.labelCombo.currentText()]:
                        setattr(i, _param.opts["name"] , _value)
                        self.statusbar.showMessage("")
                        self.labeldefs.hasChanges = True
                        break

                except Exception as e:
                    self.statusbar.showMessage(e.args[0])
                    d = OkOnlyDialog(title = "Template Error!", message = e.args[0])
                    d.exec()                    

        if self.labeldefs.hasChanges: self.setUI(True)        

    def labelClick(self , action):
        def nameCheck(ShapeName)->str:
            i = 0
            while True:
                i = i + 1
                _name = "{}{}".format(ShapeName , str(i))
                if self.labelCombo.findText(_name)==-1:
                    return _name
                
        match action:
            case "btnCopyLabel":
                for l in [ l for l in self.lspecs if l.name == self.labelCombo.currentText() ]:
                    newValue = copy.deepcopy(l)
                    newValue.name = nameCheck( "Copy of {}".format(self.labelCombo.currentText()) )
                    newValue.default = False
                    newValue.readonly = False
                    self.lspecs.append(newValue)
                    
                    self.drawLabelCombo()
                    self.labelCombo.setCurrentIndex( self.labelCombo.findText(newValue.name) )
                    self.labelSelection()
                    self.labeldefs.hasChanges = True
                    self.setUI(True)

                    break

            case _:
                pass

    def labelDefParams(self, label):
        parameters = []

        parameters.append({'name': 'General',
            'type': 'group',
            'children': [
                {'title': 'Stock Name' , 'name': 'name', 'type': 'str', 'value': label.name , 'readonly': label.readonly },
            ]
        })

        parameters.append({'name': 'Page',
            'type': 'group',
            'children': [
                {'title': 'Sheet Width' , 'name': 'sheet_width', 'type': 'int', 'value': label.sheet_width , 'siPrefix': True, 'suffix': 'mm', 'readonly': label.readonly },
                {'title': 'Sheet Height' , 'name': 'sheet_height', 'type': 'int', 'value': label.sheet_height , 'siPrefix': True, 'suffix': 'mm', 'readonly': label.readonly },
                {'title': 'Columns' , 'name': 'columns', 'type': 'int', 'value': label.columns , 'readonly': label.readonly },
                {'title': 'Rows' , 'name': 'rows', 'type': 'int', 'value': label.rows , 'readonly': label.readonly },
            ]
        })

        parameters.append({'name': 'Label',
            'type': 'group',
            'children': [
                {'title': 'Label Width' , 'name': 'label_width', 'type': 'int', 'value': label.label_width , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Label Height' , 'name': 'label_height', 'type': 'int', 'value': label.label_height , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Column Gap' , 'name': 'column_gap', 'type': 'int', 'value': label.column_gap , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Row  Gap' , 'name': 'row_gap', 'type': 'int', 'value': label.row_gap , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
            ]
        })

        parameters.append({'name': 'Margin',
            'type': 'group',
            'children': [
                {'title': 'Left Margin' , 'name': 'left_margin', 'type': 'int', 'value': label.left_margin , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Right Margin' , 'name': 'right_margin', 'type': 'int', 'value': label.right_margin , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Top Margin' , 'name': 'top_margin', 'type': 'int', 'value': label.top_margin , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
                {'title': 'Bottom Margin' , 'name': 'bottom_margin', 'type': 'int', 'value': label.bottom_margin , 'siPrefix': True, 'suffix': 'mm' , 'readonly': label.readonly },
            ]
        })

        return Parameter.create(name='params', type='group', children=parameters)

#endregion

#endregion

#region "Save"

    def SaveLabel(self, fname):
        if self.labeldefs.hasChanges:
            #Save Spec here
            self.SaveLabelDef()
            self.labeldefs.hasChanges = False
                    
        with open(fname, "w") as file:
            file.write("import sys , uuid\n")
            file.write("from reportlab.graphics import shapes\n")
            file.write("from reportlab.graphics.charts.textlabels import Label \n")
            file.write("from reportlab.lib.colors import Color\n")
            file.write("from MedatechUK.Landlord.label import mkBarcode\n")

            file.write("specs = sys.modules['label.labeldefs'].{} \n".format( self.l.template.specs.name ))
            file.write("border = False\n")
            file.write("debug = False\n\n")

            file.write("testdata = ({})\n\n".format(json.dumps(self.l.template.testdata, indent=4)))

            file.write("def draw_label(label, width, height, obj):\n\n")

            for i in self.l.c.contents:
                match self.l.ShapeType(i):
                    case sType.barcode:
                        file.write("\t{} = shapes.Image ( \n".format(i.__name__.replace(" ","_")))
                        file.write("\t\t__name__ = '{}'\n".format(i.__name__))
                        file.write("\t\t, __formatStr__ = '{}'\n".format(i.__formatStr__))
                        file.write("\t\t, __encoding__ = '{}'\n".format(i.__encoding__))
                        file.write("\t\t, __filename__ = '{}'\n".format(i.__filename__))
                        file.write("\t\t, path = ''\n")
                        for p in [p for p in self.Props(i) if p[0]!="path"]:
                            file.write("\t\t, {} = {} \n".format(p[0] , p[1]))

                        file.write("\t)\n")
                        file.write("\tlabel.add ( {} )\n\n".format(i.__name__.replace(" ","_")))

                    case sType.image:
                        file.write("\t{} = shapes.Image ( \n".format(i.__name__.replace(" ","_")))
                        file.write("\t\t__name__ = '{}'\n".format(i.__name__))
                        file.write("\t\t, __filename__ = '{}'\n".format(i.__filename__))
                        file.write("\t\t, path = ''\n")
                        for p in [p for p in self.Props(i) if p[0]!="path"]:                            
                            file.write("\t\t, {} = {} \n".format(p[0] , p[1]))

                        file.write("\t)\n")
                        file.write("\tlabel.add ( {} )\n\n".format(i.__name__.replace(" ","_")))

                    case sType.text:
                        file.write("\t{} = Label ( \n".format(i.__name__.replace(" ","_")))
                        file.write("\t\t__name__ = '{}'\n".format(i.__name__))
                        file.write("\t\t, __formatStr__ = '{}'\n".format(i.__formatStr__.replace("\n","\\n")))                        
                        for p in [p for p in self.Props(i) ]:
                            file.write("\t\t, {} = {} \n".format(p[0] , p[1]))

                        file.write("\t)\n")
                        file.write("\tlabel.add ( {} )\n\n".format(i.__name__.replace(" ","_")))

                    case sType.select:
                        pass # Don't save the cursor
            
            file.write("\tmkBarcode(label , obj , uuid.uuid4())\n")
        
        self.l = labelDef(fname)
        self.drawSelect()
        self.drawCombo()
        self.render()
        self.objectSelection()
        self.dockProperties.raise_()

    def SaveLabelDef(self):    
        with open(self.labeldefs.__file__, "w") as file:
            file.write("import labels\n\n")
            for i in self.lspecs:
                file.write("{} = labels.Specification( \n".format(i.name.replace(" ","_")))
                f = True
                for p in [p for p in self.Props(i) if p[0] not in ["name" , "default" , "readonly"]]:
                    file.write("\t{} {} = {} \n".format("" if f else ",",p[0] , p[1]))
                    f = False
                file.write(")\n")

                file.write("setattr({}, 'name' , '{}')\n".format(i.name.replace(" ","_") , i.name))
                file.write("setattr({}, 'default' , {})\n".format(i.name.replace(" ","_") , i.default))
                file.write("setattr({}, 'readonly' , {})\n\n".format(i.name.replace(" ","_") , i.readonly))               
        
        self.labeldefs.hasChanges = False
        self.loadLabelDef()

#endregion

#region "Main"

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)  # Create the application object
    MainWindow = MyForm()                   # Create the main window    
    ui = LandlordUI()                       # Create the UI    
    ui.setupUi(MainWindow)                  # Load the UI    
    ui.makeFile("settings.ini")             # Unpack setting.ini    
    ui.makeFile("LabelSpec.py")             # Unpack LabelSpec.py    
    ui.loadLabelDef()                       # Load the label definitions    
    ui.connectHandlers(MainWindow)          # Connect the handlers    
    ui.refreshFonts(add=False)              # Load fonts    
    ui.setUI(False)                         # Set the UI read only    
    MainWindow.show()                       # Show the main window 
    sys.exit(app.exec())

#endregion