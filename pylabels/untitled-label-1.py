import sys , uuid
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label 
from reportlab.lib.colors import Color
from MedatechUK.Landlord.Unpack import mkBarcode

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
    "PAR1": "Some data here",
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
        "M:\\python\\ap\\pyLabels\\tmp\\a152e422-7e5f-4517-8e75-0e1ca527d0c944c13b86-6d39-43c5-afae-a1ba93e8439d.png"
    ]
})

def draw_label(label, width, height, obj):

	Image_1 = shapes.Image ( 
		__name__ = 'Image 1'
		, __filename__ = 'circle-check.png'
		, path = ''
		, fillColor = Color(0,0,0,1) 
		, height = 90.3111111111111 
		, strokeColor = Color(0,0,0,1) 
		, strokeWidth = 1 
		, width = 90.3111111111111 
		, x = 2.6666666666666674 
		, y = 6.6666666666666945 
	)
	label.add ( Image_1 )

	Text_Box_1 = Label ( 
		__name__ = 'Text Box 1'
		, __formatStr__ = '<P1>'
		, bottomPadding = 4 
		, boxAnchor = 'nw' 
		, boxFillColor = Color(255,0,0,1) 
		, boxStrokeWidth = 0.5 
		, boxTarget = 'normal' 
		, fillColor = Color(255,255,255,1) 
		, fontName = 'Helvetica' 
		, fontSize = 17 
		, leftPadding = 4 
		, rightPadding = 4 
		, strokeWidth = 0.1 
		, textAnchor = 'start' 
		, topPadding = 4 
		, visible = 1 
		, x = 46.2857142857144 
		, y = 32.80952380952383 
	)
	label.add ( Text_Box_1 )

	mkBarcode(label , obj , uuid.uuid4())
