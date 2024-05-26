from reportlab.pdfgen import canvas
import os , sys
import importlib.util
from pathlib import Path
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPM
from decimal import Decimal
from reportlab.lib.units import mm

mm = Decimal(mm)

WorkingDir = Path(__file__).parent
if "python" not in sys.executable: WorkingDir = Path(sys.executable).parent
WorkingDir = os.path.join(WorkingDir , "pyLabels")

spec = importlib.util.spec_from_file_location("label.labeldefs", os.path.join(WorkingDir , '{}.py'.format( "LabelSpec" )))
labeldefs = importlib.util.module_from_spec(spec)
sys.modules["label.labeldefs"] = labeldefs
spec.loader.exec_module(labeldefs)

spec = importlib.util.spec_from_file_location("label.template", os.path.join(WorkingDir , '{}.py'.format( 'paycard' )))
template = importlib.util.module_from_spec(spec)
sys.modules["label.template"] = template
spec.loader.exec_module(template)

c = Drawing(
    float(template.specs.label_width*mm)
    , float(template.specs.label_height*mm)
)
template.draw_label(
    c
    , float(template.specs.label_width*mm)
    , float(template.specs.label_height*mm)
    , ({
        "QR" : os.path.join(WorkingDir , 'qr.png')
        , "COUNT"  : 1
        , 'PAR1' : "Test Data"
        , 'PAR2' : "Test Data"
        , 'PAR3' : "Test Data"
        , 'PAR4' : "Test Data"
        , 'PAR5' : "Test Data"
        , 'PAR6' : "Test Data"
        , 'PAR7' : "Test Data"
        , 'PAR8' : "Test Data"
        , 'PAR9' : "Test Data"
        , 'PAR10' : "Test Data"
        , 'PAR11' : "Test Data"
        , 'PAR12' : "Test Data"
        , 'PAR13' : "Test Data"
        , 'PAR14' : "Test Data"
        , 'PAR15' : "Test Data"
        , 'PAR16' : "Test Data"
        , 'PAR17' : "Test Data"
        , 'PAR18' : "Test Data"
        , 'PAR19' : "Test Data"
        , 'PAR20' : "Test Data"
    })
)
renderPM.drawToFile(c, os.path.join(WorkingDir, 'example1.png'), 'PNG')

for i in c.contents:
    match str(type(i)) :
        case "<class 'reportlab.graphics.shapes.Image'>":
            pass
        case "<class 'reportlab.graphics.shapes.String'>":
            pass
        case "<class 'reportlab.graphics.charts.textlabels.Label'>":
            pass