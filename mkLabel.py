import labels
import pyqrcode
import os
import json, uuid , shutil
from MedatechUK.oDataConfig import Config
from MedatechUK.cl import clArg
import debugpy
import os , time , sys
from pathlib import Path
import importlib.util

def main():
    arg = clArg()
    if arg.byName(["user","u"])==None:
        print ("No user specified.")
        return None
    if arg.byName(["env","e"])==None:
        print ("No environment specified.")
        return None
    if arg.byName(["env","e"])==None:
        print ("No environment specified.")
        return None
    if arg.byName(["save","s"])==None:
        print ("No save name specified.")
        return None

    WorkingDir = Path(__file__).parent
    if "python" not in sys.executable: WorkingDir = Path(sys.executable).parent
    WorkingDir = os.path.join(WorkingDir , "pyLabels")

    if not os.path.exists(os.path.join(WorkingDir, arg.byName(["save","s"]))):
        os.mkdir(os.path.join(WorkingDir, arg.byName(["save","s"])))

    debug = False
    config = Config(
        env = arg.byName(["env","e"])
        , path = WorkingDir
    )

    if "debug" in arg.kwargs():
        debug = True
        debugpy.configure(python="c:\\program files\\Python312\\python.exe")
        debugpy.listen( int( config.debug.port ) )
        debugpy.wait_for_client()

    spec = importlib.util.spec_from_file_location("label.labeldefs", os.path.join(WorkingDir , '{}.py'.format( "LabelSpec" )))
    labeldefs = importlib.util.module_from_spec(spec)
    sys.modules["label.labeldefs"] = labeldefs
    spec.loader.exec_module(labeldefs)
    
    cnxn = Config.cnxn(config)
    cursor = cnxn.cursor()
    cursor.execute("USE [{}]; ".format(config.environment))

    tsql = ("SELECT DISTINCT TOP (1) dbo.LABELSDEF.LABELPATH "
    + "FROM dbo.LABELS INNER JOIN dbo.LABELSDEF ON dbo.LABELS.LABELDEF = dbo.LABELSDEF.LABELDEF "
    + "WHERE (dbo.LABELS.T$USER = {}) ").format(
        arg.byName(["user","u"])
    )
    templates = cursor.execute(tsql)
    for row in templates:
        if not os.path.exists(os.path.join(WorkingDir , "{}.py".format( row[0] ))):
            return None

        # Create the sheet.
        spec = importlib.util.spec_from_file_location("label.template", os.path.join(WorkingDir , '{}.py'.format( row[0] )))
        template = importlib.util.module_from_spec(spec)
        sys.modules["label.template"] = template
        spec.loader.exec_module(template)

        template.debug = debug
        sheet = labels.Sheet(template.specs, template.draw_label, template.border)

        sql = ( " SELECT    dbo.LABELS.QR "
                + ", dbo.LABELS.LABELQUANT "
                + ", dbo.LABELS.PAR1, dbo.LABELS.PAR2, dbo.LABELS.PAR3, dbo.LABELS.PAR4, dbo.LABELS.PAR5, dbo.LABELS.PAR6 "
                + ", dbo.LABELS.PAR7, dbo.LABELS.PAR8, dbo.LABELS.PAR9, dbo.LABELS.PAR10, dbo.LABELS.PAR11, dbo.LABELS.PAR12 "
                + ", dbo.LABELS.PAR13, dbo.LABELS.PAR14, dbo.LABELS.PAR15, dbo.LABELS.PAR16, dbo.LABELS.PAR17 "
                + ", dbo.LABELS.PAR18, dbo.LABELS.PAR19, dbo.LABELS.PAR20 "
                + "FROM dbo.LABELS INNER JOIN dbo.LABELSDEF ON dbo.LABELS.LABELDEF = dbo.LABELSDEF.LABELDEF "
                + "WHERE 0=0 "
                + "AND   (dbo.LABELS.T$USER = {}) "
                + "AND   (dbo.LABELSDEF.LABELPATH = '{}') "
                + "ORDER BY dbo.LABELS.SORT ").format(
                    arg.byName(["user","u"])
                    , row[0]
                )
        tlabels = cursor.execute(sql)
        thisLabels = []
        for pars in tlabels:
            obj = ({
                "QR" : pars[0]
                , "COUNT"  : int(pars[1])
                , 'PAR1' : pars[2]
                , 'PAR2' : pars[3]
                , 'PAR3' : pars[4]
                , 'PAR4' : pars[5]
                , 'PAR5' : pars[6]
                , 'PAR6' : pars[7]
                , 'PAR7' : pars[8]
                , 'PAR8' : pars[9]
                , 'PAR9' : pars[10]
                , 'PAR10' : pars[11]
                , 'PAR11' : pars[12]
                , 'PAR12' : pars[13]
                , 'PAR13' : pars[14]
                , 'PAR14' : pars[15]
                , 'PAR15' : pars[16]
                , 'PAR16' : pars[17]
                , 'PAR17' : pars[18]
                , 'PAR18' : pars[19]
                , 'PAR19' : pars[20]
                , 'PAR20' : pars[21]              
            })
            thisLabels.append(obj)

        for i in thisLabels:
            QRs = ("SELECT QRNAME, QRVALUE "
                + "FROM  dbo.ZMED_QRLABELS "
                + "WHERE QR = '{}'").format(
                    i["QR"]
                ) 
            qr = cursor.execute(QRs)
            jstr = {}
            jstr["in"] = []
            for names in qr:
                this = {}
                this["i"] = names[0]
                this["v"] = names[1]
                jstr["in"].append(this)

            qrcode = pyqrcode.create(json.dumps(jstr))
            qrfile = os.path.join(WorkingDir, arg.byName(["save","s"]) , '{}.png'.format( str(uuid.uuid4())))
            qrcode.png(qrfile, scale=8)
            i["QR"] = qrfile

            for repeat in range( i["COUNT"] ):
                sheet.add_label(i)

        sheet.save(
            os.path.join(
                config.config.file.savedir
                , "{}.pdf".format( arg.byName(["save","s"]))
            )
        )
        shutil.rmtree(os.path.join(WorkingDir, arg.byName(["save","s"])), ignore_errors=True)

    cursor.close()

if __name__ == '__main__':
    sys.exit(main())