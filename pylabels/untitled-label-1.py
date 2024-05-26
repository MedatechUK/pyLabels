import sys , uuid
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label 
from reportlab.lib.colors import Color
from Landlord.Unpack import mkBarcode

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

	QRcode_1 = shapes.Image ( 
		__name__ = 'QRcode 1'
		, __formatStr__ = '<QR>'
		, __encoding__ = 'QRCODE'
		, __filename__ = '811c95c7-d161-460e-92a7-054c726bb9a7'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 71.57777777777775 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 71.57777777777775 
		, x = 105.66666666666669 
		, y = 34.42222222222227 
	)
	label.add ( QRcode_1 )

	Barcode_1 = shapes.Image ( 
		__name__ = 'Barcode 1'
		, __formatStr__ = '123123123123'
		, __encoding__ = 'EAN13'
		, __filename__ = '4e9ca29c-ac19-4a72-8103-43c1acf8e657'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 53.53728489483748 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 100 
		, x = 2.3333333333333304 
		, y = 41.93987677926494 
	)
	label.add ( Barcode_1 )

	mkBarcode(label , obj , uuid.uuid4())
