import sys , uuid
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label 
from reportlab.lib.colors import Color
from MedatechUK.Landlord.label import mkBarcode

specs = sys.modules['label.labeldefs'].L7160 
border = False
debug = False

testdata = ({
    "QR": {
        "in": [
            {
                "i": "PROJACT",
                "v": 3411
            },
            {
                "i": "CAT",
                "v": 14
            }
        ]
    },
    "COUNT": 1,
    "PAR1": "Hello!",
    "PAR2": "Test!",
    "PAR3": "Wow!",
    "PAR4": "Test Data 4",
    "PAR5": "Here",
    "PAR6": "Test Data 6",
    "PAR7": "Test Data 7",
    "PAR8": "Test Data 8",
    "PAR9": "Test Data 9",
    "PAR10": "Test Data 10",
    "PAR11": "Test Data 11",
    "PAR12": "Test Data 12",
    "PAR13": "Test Data 13",
    "PAR14": "Test Data 14",
    "PAR15": "Test Data 15",
    "PAR16": "Test Data 16",
    "PAR17": "Test Data 17",
    "PAR18": "Test Data 18",
    "PAR19": "Test Data 19",
    "PAR20": "Test Data 20",
    "clean": [
        "M:\\python\\ap\\pyLabels\\tmp\\1659203f-a551-4e92-bb82-ebfdd3079e05QWERTYUIOP123456789.png"
    ]
})

def draw_label(label, width, height, obj):

	Text_0 = Label ( 
		__name__ = 'Text 0'
		, __formatStr__ = '<P5>'
		, boxAnchor = 'nw' 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(0,0,0,1) 
		, fontName = 'Helvetica' 
		, fontSize = 12 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, visible = 1 
		, x = 6.7999999999999945 
		, y = 84.40000000000002 
	)
	label.add ( Text_0 )

	Text_45 = Label ( 
		__name__ = 'Text 45'
		, __formatStr__ = '<P2>'
		, angle = 45 
		, boxAnchor = 'nw' 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(0,0,0,1) 
		, fontName = 'Helvetica' 
		, fontSize = 12 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, visible = 1 
		, x = 24.800000000000004 
		, y = 43.20000000000001 
	)
	label.add ( Text_45 )

	Text_90 = Label ( 
		__name__ = 'Text 90'
		, __formatStr__ = '<P1>'
		, angle = 90 
		, boxAnchor = 'nw' 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(0,0,0,1) 
		, fontName = 'Helvetica' 
		, fontSize = 12 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, visible = 1 
	)
	label.add ( Text_90 )

	QRcode = shapes.Image ( 
		__name__ = 'QRcode'
		, __formatStr__ = '<QR>'
		, __encoding__ = 'QRCODE'
		, __filename__ = 'QWERTYUIOP123456789'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 100.0 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 100 
		, x = 79.39999999999999 
		, y = 10.199999999999998 
	)
	label.add ( QRcode )

	mkBarcode(label , obj , uuid.uuid4())
