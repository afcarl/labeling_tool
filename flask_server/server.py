import os
import errno
import sql_interface as sql
from datetime import datetime


ROOT_DIR = os.getcwd()
print("Application Root Directory:",ROOT_DIR)

def result_store( pcname, meshname, matrix, user, other=None):
    return sql.registerMatch(pcname, meshname, matrix, user, other)
    """
    #remove file extensions, if any
    pcname = os.path.splitext(pcname)[0]
    meshname = os.path.splitext(meshname)[0]

    mkdirp(ROOT_DIR, 'uploads',pcname)
    with open(os.path.join(ROOT_DIR,'uploads',pcname,meshname), 'w') as f:
        f.write("pointcloud = "+pcname+"\n")
        f.write("mesh = "+meshname+"\n")
        f.write("matrix =")
        for n in matrix:
            f.write(' ')
            f.write(str(n))
        f.write("\n")

        #write other fields
        if other:
            for k in other:
                f.write(k+" = "+other[k]+"\n")
        f.close()
    """

def result_get( pcname, meshname):
    return sql.getMatchStr(pcname, meshname)
    """
    with open(os.path.join(ROOT_DIR,'uploads',pcname,meshname), 'r') as f:   
        return f.read()
    return None
    """


def parseMatrix(m):
    m=m.strip()
    if m is None:
        raise SyntaxError('Request must contain matrix')
    mat = m.split(' ')
    if len(mat) != 16:
        raise SyntaxError('4x4 Matrix must have 16 elements')
    #print("nums:",mat, "type: ",type(mat))
    def cast(x):
        return float(x)
    mat = list(map(cast, mat))
    return (mat)


def mkdirp(*paths):
    path = os.path.join(*paths)

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
         "Oct", "Nov", "Dec"]
def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = weekdays[dt.weekday()]
    month = months[dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

def getDateStr():
    return httpdate(datetime.utcnow())