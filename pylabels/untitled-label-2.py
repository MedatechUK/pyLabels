import sys , uuid
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label 
from reportlab.lib.colors import Color
from MedatechUK.Landlord.label import mkBarcode
specs = sys.modules['label.labeldefs'].L7161 
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
    "PAR20": "Test Data 20",
    "clean": [
        "M:\\python\\ap\\pyLabels\\tmp\\1b5e8294-bd19-41aa-ab18-ec5521a364904ca20132-124d-4fdb-a544-5a1b170cc2ff.png",
        "M:\\python\\ap\\pyLabels\\tmp\\1b5e8294-bd19-41aa-ab18-ec5521a3649020427446-96b7-494f-be4c-e5022b90987d.png",
        "M:\\python\\ap\\pyLabels\\tmp\\1b5e8294-bd19-41aa-ab18-ec5521a3649034ddc8ef-c2df-4715-a44a-d00bbeeabdfe.png"
    ]
})

def draw_label(label, width, height, obj):

	Text_Box_1 = Label ( 
		__name__ = 'Text Box 1'
		, __formatStr__ = 'Some Value'
		, boxAnchor = 'nw' 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(0,0,0,1) 
		, fontName = 'Helvetica' 
		, fontSize = 12 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, visible = 1 
		, x = 16.285714285714285 
		, y = 137.19470699432893 
	)
	label.add ( Text_Box_1 )

	Image_1 = shapes.Image ( 
		__name__ = 'Image 1'
		, __filename__ = 'circle-check.png'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 90.3111111111111 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 90.3111111111111 
		, x = 9.000000000000005 
		, y = 6.7536849484845956 
	)
	label.add ( Image_1 )

	Barcode_1 = shapes.Image ( 
		__name__ = 'Barcode 1'
		, __formatStr__ = '123123123123'
		, __encoding__ = 'EAN13'
		, __filename__ = '4ca20132-124d-4fdb-a544-5a1b170cc2ff'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 60.76630550244317 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 113.50277777777777 
		, x = 157.71428571428572 
		, y = 85.57471529150769 
	)
	label.add ( Barcode_1 )

	QRcode_1 = shapes.Image ( 
		__name__ = 'QRcode 1'
		, __formatStr__ = '<QR>'
		, __encoding__ = 'QRCODE'
		, __filename__ = '20427446-96b7-494f-be4c-e5022b90987d'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 55.577777777777754 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 55.577777777777754 
		, x = 140.85714285714283 
		, y = 0.4433942449065569 
	)
	label.add ( QRcode_1 )

	QRcode_2 = shapes.Image ( 
		__name__ = 'QRcode 2'
		, __formatStr__ = '<QR>'
		, __encoding__ = 'QRCODE'
		, __filename__ = '34ddc8ef-c2df-4715-a44a-d00bbeeabdfe'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 55.577777777777754 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 55.577777777777754 
		, x = 85.0 
		, y = 83.60632818248718 
	)
	label.add ( QRcode_2 )

	mkBarcode(label , obj , uuid.uuid4())
