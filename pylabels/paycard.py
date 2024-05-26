# Uses: https://docs.reportlab.com/reportlab/userguide/ch11_graphics/

import sys
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label

specs = sys.modules["label.labeldefs"].L7160 
border = False
debug = False

testdata = ({
    "QR" : {"in":[{"i":"PROJACT","v":3411},{"i":"CAT","v":14}]}
    , "COUNT"  : 1
    , 'PAR1' : "Test Data 1"
    , 'PAR2' : "Test Data 2"
    , 'PAR3' : "Test Data 3"
    , 'PAR4' : "Test Data 4"
    , 'PAR5' : "Test Data 5"
    , 'PAR6' : "Test Data 6"
    , 'PAR7' : "Test Data 7"
    , 'PAR8' : "Test Data 8"
    , 'PAR9' : "Test Data 9"
    , 'PAR10' : "Test Data 10"
    , 'PAR11' : "Test Data 11"
    , 'PAR12' : "Test Data 12"
    , 'PAR13' : "Test Data 13"
    , 'PAR14' : "Test Data 14"
    , 'PAR15' : "Test Data 15"
    , 'PAR16' : "Test Data 16"
    , 'PAR17' : "Test Data 17"
    , 'PAR18' : "Test Data 18"
    , 'PAR19' : "Test Data 19"
    , 'PAR20' : "Test Data 20"
})

def draw_label(label, width, height, obj):        

    lab1 = Label( __formatStr__="<P5>\n<P3>\n<P6>" , __name__="Side Text" , boxAnchor = 'nw' , angle = 90 , fontName="Helvetica", fontSize=12 )
    lab1.setOrigin(height+2,20)        
    lab1.setText("{}\n{}\n{}".format( 
        obj["PAR5"] 
        , obj["PAR3"] 
        , obj["PAR6"]         
    ))

    lab2 = Label( __formatStr__="<P1> (<P2>)" , __name__="Bottom Text" , boxAnchor = 'nw' , angle = 0 , fontName="Helvetica", fontSize=12 )
    lab2.setOrigin(8,12)        
    lab2.setText("{} ({})".format( 
        obj["PAR1"] 
        , obj["PAR2"]         
    ))

    label.add ( shapes.Image ( 3 , 5 , height-1, height-1, obj["QR"], __name__="qr" ))    
    label.add ( lab1 )
    label.add ( lab2 )
    