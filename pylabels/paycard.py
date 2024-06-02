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
    "PAR1": "Test Data 1",
    "PAR2": "Test Data 2",
    "PAR3": "Test Data 3",
    "PAR4": "Test Data 4",
    "PAR5": "Test Data 5",
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
    "PAR20": "Test Data 20"
})

def draw_label(label, width, height, obj):

	Side_Text = Label ( 
		__name__ = 'Side Text'
		, __formatStr__ = '<P5>\n<P3>\n<P6>'
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
		, x = 110.00000000000001 
		, y = 20 
	)
	label.add ( Side_Text )

	Bottom_Text = Label ( 
		__name__ = 'Bottom Text'
		, __formatStr__ = '<P1> (<P2>)'
		, boxAnchor = 'nw' 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(0,0,0,1) 
		, fontName = 'Helvetica' 
		, fontSize = 12 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, visible = 1 
		, x = 8 
		, y = 12 
	)
	label.add ( Bottom_Text )

	QRcode_1 = shapes.Image ( 
		__name__ = 'QRcode 1'
		, __formatStr__ = '<QR>'
		, __encoding__ = 'QRCODE'
		, __filename__ = '8eed70e1-783c-4d6e-a57e-34b8dca71bcf'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 89.57777777777775 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 89.57777777777775 
		, x = 10.000000000000002 
		, y = 11.422222222222263 
	)
	label.add ( QRcode_1 )

	mkBarcode(label , obj , uuid.uuid4())
