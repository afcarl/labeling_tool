import re
import struct

"""
PLY Parser

Usage:
There are 2 relevant functions:
-- To extract header info, call getHeaderInfo(filename)
-- To parse a file call parsePLY(filename, callback)
    Callback is a function with the following parameters: (element_name, element_args, count)
    'element_name' is the name of a defined element in the PLY file. Ex. 'vertex' or 'face'
    'element_args' is a dictionary mapping {property_names: property_values}
                Ex. A 'vertex' element might have defined the properties 'float x','float y',and 'float z'
                Therefore, the callback could receive:
                element_name = 'vertex'
                element_args = {'y':1.0223, 'x':2.00, 'z':-5.3334}
    'count' is an integer indicating which instance of the element is being parsed. 'count' starts at 0

    To extend this parser to support more variable types / PLY file formats, add to
    the section of code labeled "TYPE HANDLING FUNCTIONS"

"""


MODULE_NAME = 'PLY Parser'
#Regular expressions for parsing the header:
ply_re = re.compile('ply[\s]+')
format_re = re.compile('format (?P<format>([\w]*))\s+(?P<vers>([0-9.]+))')
comment_re = re.compile('comment[\s]*.*')
end_header_re = re.compile('end_header[\s]*')
element_re = re.compile('element (?P<name>([\w]+)) (?P<count>([0-9]+))')
property_re = re.compile('property (?P<type>([\w ]+)) (?P<name>([\w]+))')


#
# TYPE HANDLING FUNCTIONS
# If you need to add support for new file formats (ex. ascii, big endian)
# or new variable types modify here.
# Lists are handled automatically (you only need to specify non-list types)
#

def _ble_float(f): #Binary Little Endian - float
    return struct.unpack('f',f.read(4))[0]

def _ble_int(f): #Binary Little Endian - int
    return struct.unpack('i',f.read(4))[0]

def _ble_uchar(f): #Binary Little Endian - uchar
    return ord(f.read(1))

_ble_dict = { 'float':_ble_float,
              'float32':_ble_float,
               'uchar':_ble_uchar,
               'int8':_ble_uchar,
               'int':_ble_int,
               'int32':_ble_int}
_ascii_dict = {} #Unimplemented
_bbe_dict = {} #Unimplemented

#
# END OF TYPE HANDLING FUNCTIONS
#

"""
Parse function accessor.
Returns a function of the form func(filestream)
which will return the next instance of 'vartype' in the stream.
"""
def getParseFun(fileformat, vartype):

    #Check for lists
    split = vartype.split(' ')
    if( split[0] == "list"): #Parsing lists
        if( len(split) != 3):
            raise SyntaxError(MODULE_NAME+": Invalid list type declaration: "+vartype)
        length_parser = getParseFun(fileformat, split[1])
        content_parser = getParseFun(fileformat, split[2])
        def listParser(f):
            length = length_parser(f)
            lst = []
            for i in xrange(0,length):
                new_elem = content_parser(f)
                lst.append(new_elem)
            return lst
        return listParser

    #For non-list types
    if (fileformat == 'binary_little_endian'):
        if vartype in _ble_dict:
            return _ble_dict[vartype];
        else:
            raise NotImplementedError(MODULE_NAME +": Variable type '"+vartype+"' not supported in binary little endian")
    elif (fileformat == 'ascii'):
        raise NotImplementedError(MODULE_NAME +": PLY Format '"+fileformat+"' not supported")
    elif (fileformat == 'binary_big_endian'):
        raise NotImplementedError(MODULE_NAME +": PLY Format '"+fileformat+"' not supported")
    else:
        raise SyntaxError(MODULE_NAME +": Invalid PLY format: '"+fileformat)

"""
Returns info stored in header in a more user-friendly format than _parseHeader

Returns a header object:

header.format = The Ply format
header.elements = A dictionary of {element_name => element},
    where an element is an object with these fields:
    element.count = The number of instances of this element specified by the PLY header.
    element.props = A dictionary of {property_name => property type}
"""
def getHeaderInfo(filename):
    f = open(filename, 'rb')
    return getHeaderInfoStream(f)


def getHeaderInfoStream(filestream):
    def header(): pass
    elements, plyformat = _parseHeader(filestream);

    header.format = plyformat 
    header.elements = {}

    for elem in elements:
        name = elem[0]
        count = elem[1]
        props = elem[2]
        propdict = {}
        for prop in props:
            propname = prop[0]
            proptype = prop[1]
            propdict[propname] = proptype

        def element(): pass
        element.count = count
        element.properties = propdict
        header.elements[name] = element
    return header

"""
Parses the header of a PLY file. Consumes the stream up to the end of
the header.
Returns the information of the header in a somewhat messy format,
but that shouldnt matter since this functions should be used internally
by the parser.
This function does not close the stream.

Returns a list of [element_name, count, [ list of [property_names,type] ] ]
and the ply format
"""
def _parseHeader(f):
    elements = [] # list of [element_name, count, [ [property_names,type]... ] ]
    plyformat = None
    try:
        #read header
        ply_line = ply_re.match(f.readline());
        if not ply_line:
            raise SyntaxError(MODULE_NAME+": Ply file must start with the line 'ply'")

        format_line = format_re.match(f.readline())
        if not format_line:
            raise SyntaxError(MODULE_NAME+": Second line must be a format specifier")
        plyformat = format_line.group('format')
        vers = format_line.group('vers')
                
        if not (vers == "1.0"):
            raise NotImplementedError(MODULE_NAME +": Only v1.0 formats are supported. Received: "+vers)
        
        #enter main header parsing loop
        current_elem_name = None
        current_elem_count = None
        current_elem_properties = [] # [ [property_name,type]...]
        props_found = {}
        def finalize_element(name, count, props):
            if name and props:
                new_element = [name, count, props]
                elements.append(new_element)
        
        while True:
            line = f.readline()
            #print "Parsing line ",line,

            if comment_re.match(line):
                continue
            if end_header_re.match(line):
                finalize_element(current_elem_name,current_elem_count,current_elem_properties)
                break

            elem_line = element_re.match(line)
            if elem_line: #New element declaration!
                #record previous element
                finalize_element(current_elem_name,current_elem_count,current_elem_properties)
                
                current_elem_name = elem_line.group('name')
                current_elem_count = int(elem_line.group('count'))
                current_elem_properties = []
                props_found = {}
                continue

            prop_line = property_re.match(line)
            if prop_line:
                if current_elem_name:
                    new_type = prop_line.group('type')
                    new_name = prop_line.group('name')
                    if new_name in props_found:
                        raise SyntaxError(MODULE_NAME +": Repeated definition of property "+new_name)
                    current_elem_properties.append([new_name,new_type])
                else:
                    raise SyntaxError(MODULE_NAME +": Property defined before element")
    finally:
        #f.close()
        pass
    return elements, plyformat

"""
Parse a PLY file given a filename
"""
def parsePLY(filename, callback):
    parsePLYstream(open(filename,'rb'), callback)

"""
Parse a PLY file given a stream.
THe options 'rb' should be enabled when opening the file stream.
This function automatically closes the stream when finished.
"""
def parsePLYstream(f, callback):
    elements, plyformat = _parseHeader(f)
    try:
        #Parse body
        for elem in elements:
            name = elem[0]
            count = elem[1]
            params = elem[2] #[ [property_names,type]... ]

            for i in xrange(0,count):
                args = {}
                for param in params:
                    param_name = param[0]
                    param_type = param[1]
                    parse_fun = getParseFun(plyformat,param_type)
                    val = parse_fun(f)
                    args[param_name] = val
                callback(name, args, i)     
    finally:
        f.close()
    #end function

#Testing
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]

    hdr = getHeaderInfo(filename)
    print "Format: ",hdr.format
                
    for e in hdr.elements:
        print "Element: %s (x%d)" % (e, hdr.elements[e].count)
        for p in hdr.elements[e].properties:
            print "\t%s %s" % ( hdr.elements[e].properties[p],p)

    def testCallback(name, args, count):
        tot_count = hdr.elements[name].count
        if (count % max(int(tot_count/10),1) == 0):
            print "%s %s %s" % (str(name),str(args),str(count))
                
    parsePLY(filename, testCallback)

