# [\\bin.95\\mkLabel.exe](./mkLabel.py "\\bin.95\\mkLabel.exe")
This program prints QR labels from the Priority labels work area.

## Parameters
The following parameters are mandatory.
| Parameter   | Description                   |
|-------------|-------------------------------|
| -u / -user  | The Priority User (SQL.USER)  |
| -e / -env   | The Priority Company (SQL.ENV)|
| -s / -save  | A random filename (SQL.GUID)  |

The program can be called from Priority like so:
```sql
:PAR = :GUID = '';
SELECT SQL.GUID INTO :GUID FROM DUMMY ;
:U = STRCAT('-u ' , ITOA(SQL.USER )) ;
:E = STRCAT('-e ' , SQL.ENV ) ;
:S = STRCAT('-s ' , :GUID ) ;
SELECT STRCAT(:U , ' ' , :E, ' ' , :S ) INTO :PAR FROM DUMMY;
EXECUTE WINAPP 'C:\Priority\BIN.95', '-w','mklabel.exe', :PAR
;

```

Then you can use the GUID to open the created PDF, like this:
```sql
SELECT STRCAT
('https://some_url/primail/labels/'
, :GUID
, '.pdf'
)
FROM DUMMY
ASCII :$.URL;

```
## Label Templates
To set up a label defintion, use Priority label definitions to specify the python file (WITHOUT the .py ending) that contains the template.

The template file defined must reside in a sub-folder of \\Bin.95 called pyLabels.

The template must specify a pre-defined label stock. These formats are defined in the \\Bin.95\\[LabelSpec.py](./pylabels/LabelSpec.py "LabelSpec.py") file.
```python
specs = sys.modules["label.labeldefs"].L7160 

```

The template must contain a method to format the label called draw_label():
```python
def draw_label(label, width, height, obj): 

```
| Parameter   | Description                   |
|-------------|-------------------------------|
| label   | A drawing canvas for the current label |
| width   | The width of the current label |
| height  | The height of the current label   |
| obj     | An object containing the label data|

## Accessing Label Data
The obj data object contains the path of the image of the QR code, and parameters 1-20 from the Priority LABELS table.
```python
obj["QR"] # The path of the QR image
obj["PAR1"]
obj["PAR2"]
obj["PAR3"]
...

```
## Label design
Data is drawn on the canvas with [reportlab](https://docs.reportlab.com/reportlab/userguide/ch11_graphics/ "reportlab") objects.

For example, we can draw the QR code by adding an image shape to the label:
```python
label.add ( shapes.Image ( 3 , 5 , height-1, height-1, obj["QR"] ))

```
And we can add a text  string shape, using parameters from the LABELS table:
```python
label.add ( shapes.String ( 8, 2, obj["PAR1"] +" (" + obj["PAR2"] + ")", fontName="Helvetica", fontSize=12 ))

```

See full [template example](./pylabels/paycard.py "template example").