# Uses: https://docs.reportlab.com/reportlab/userguide/ch11_graphics/

import debugpy , sys
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label

specs = sys.modules["label.labeldefs"].L7160 
border = False
debug = False

def draw_label(label, width, height, obj):    

    if debug: debugpy.breakpoint()

    lab = Label(boxAnchor = 'nw' , angle = 90 , fontName="Helvetica", fontSize=12 )
    lab.setOrigin(height+2,20)        
    lab.setText("{}\n{}\n{}".format( 
        obj["PAR5"] 
        , obj["PAR3"] 
        , obj["PAR6"]         
    ))

    label.add ( shapes.Image ( 3 , 5 , height-1, height-1, obj["QR"] ))
    label.add ( shapes.String ( 8, 2, obj["PAR1"] +" (" + obj["PAR2"] + ")", fontName="Helvetica", fontSize=12 ))
    label.add ( lab )
    