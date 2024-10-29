#!/usr/bin/python3

## oiddir-schema-extract.py :: oiddir schema extractor
##
## $ ./oiddir-schema-extract.py [options]
##
## Jesse Coretta - 09/07/2024
##
## Simple extraction of LDAP schema definitions from any
## revision of draft-coretta-oiddir-schema. The extracted
## content is written to STDOUT and is formatted for 389DS,
## OpenDJ or OpenLDAP.
##
## The script is written in procedural style and is meant to
## be easily understood, read and modified.
##
## WARNING: The subject matter of this I-D series is entirely
## an EXPERIMENTAL concept. None of this should be used within
## production or mission-critical environments. This material
## is provided for testing, PoC or work-in-progress cases only.
##
## Note in its current state, this script will not work for
## other RFCs or I-Ds as the matching pattern only accepts a
## very specific OID prefix (1.3.6.1.4.1.56521.101.2.(1|3|5|7)).
##
## Also note that in the case of 389DS, version >=1.4.3 MUST
## be used due to use of the UUID syntax and relevant matching
## rules defined in RFC 4530.
##
## Users should feel free to modify this script to suit other
## output formats, such as CSV or XML.
##
## Go users: The output produced can be parsed into usable Go
## types using my go-schemax package, freely available at:
##
##   - https://github.com/JesseCoretta/go-schemax
##
## Enjoy :)
##
##   - NOTE: Written and tested on Linux.
##
################################################################
##
## MIT License
##
## Copyright (c) 2024 Jesse Coretta
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.

import re
import sys
import getopt

## usage message to print when something goes
## sideways, or when the user needs help.
usage = '''$ ./oiddir-schema-extract.py
    -h                                      ; show this text and then sys.exit(1)
    -t (opendj|openldap|389ds)              ; output format type
    -f /path/to/draft-coretta-oiddir-schema ; draft-coretta-oiddir-schema revision to parse
    -n                                      ; no newlines in definitions
    -s                                      ; use custom syntaxes (OpenDJ only)
    -x                                      ; do not include eXtensions'''

try:
    opts, args = getopt.getopt(sys.argv[1:], 't:f:hnsx', ['type=', 'file=', 'help',
        'use-custom-syntaxes',
        'no-extensions',
        'no-newlines'])
except getopt.GetoptError:
    print("Getopt error - check syntax")
    print(usage)
    sys.exit(2)

## define core config vars for later
## interrogation.
ftyp = ''
doc = ''
nonl = False
noxo = False
csyn = False

## scan for config options
for opt, arg in opts:
    if opt in ('-h', '--help'):
        print(usage)
        sys.exit(1)
    elif opt in ('-t', '--type'):
        ftyp = arg.lower()
    elif opt in ('-s', '--use-custom-syntaxes'):
        csyn = True
    elif opt in ('-n', '--no-newlines'):
        nonl = True
    elif opt in ('-x', '--no-extensions'):
        noxo = True
    elif opt in ('-f', '--file'):
        doc = arg
    else:
        ## unknown option
        print(usage)
        sys.exit(2)

## ensure the core required parameters
## have been satisfied.
if not (ftyp == "openldap" or ftyp == "389ds" or ftyp == "opendj"):
    print("No format type specified")
    print(usage)
    sys.exit(2)
elif len(doc) == 0:
    print("No text draft specified")
    print(usage)
    sys.exit(2)

# read file
with open(doc, 'r') as file:
    text = file.read()

# Specify matching pattern. This requires all of the following to
# evaluate as true for each definition:
#
#  - Empty line immediately before each definition
#  - Exactly six (6) spaces, followed by an opening parenthesis, one
#    space and the official OID prefix all represent the beginning of
#    each definition, regardless of type
#  - Interim content represents the continuation of the current
#    definition, likely on a new line
#  - The occurrence of a closing parenthesis and newline, followed by
#    an empty line all represent the end of the current definition
schema_pattern = re.compile(
    r'^$\n^(\s{6,}\(\s1\.3\.6\.1\.4\.1\.56521\.101\.2\.(1|3|5|7)\.\d+.+?\)(?=\n^$))',
    re.DOTALL | re.MULTILINE
)

# custom ldap syntaxes (for OpenDJ only). These satisfy
# syntax concerns mentioned within Section 2.1 of the
# RASCHEMA I-D. These do NOT extend from the I-D series,
# and exist only to demonstrate the means for satisfying
# the aforementioned concerns.
syntaxes = r'''
      ( 1.3.6.1.4.1.56521.101.2.1.3
          DESC 'X.680, cl. 34: OID-IRI'
          X-PATTERN '^(\/[A-Za-z0-9\-._~]+|[\uA0000-\uD7FF]+|[\uF900}-\uFDCF]+|[\uFDF0}-\uFFEF]+|[\u10000}-\u1FFFD]+|[\u20000}-\u2FFFD]+|[\u30000}-\u3FFFD]+|[\u40000}-\u4FFFD]+|[\u50000}-\u5FFFD]+|[\u60000}-\u6FFFD]+|[\u70000}-\u7FFFD]+|[\u80000}-\u8FFFD]+|[\u90000}-\u9FFFD]+|[\uA0000}-\uAFFFD]+|[\uB0000}-\uBFFFD]+|[\uC0000}-\uCFFFD]+|[\uD0000}-\uDFFFD]+|[\uE1000}-\uEFFFD]+)+$' )

      ( 1.3.6.1.4.1.56521.101.2.1.4
          DESC 'X.680, cl 32.3: ObjectIdentifierValue'
          X-PATTERN '^\{([a-z](-?[A-Za-z0-9]+)*(\(\d+\))?)(\s([a-z](-?[A-Za-z0-9]+)*(\(\d+\))))*\}$' )

      ( 1.3.6.1.4.1.56521.101.2.1.5
          DESC 'X.660, cl 7.5: non-integer Unicode label'
          X-PATTERN '^([A-Za-z0-9\-._~]+|[\uA0000-\uD7FF]+|[\uF900}-\uFDCF]+|[\uFDF0}-\uFFEF]+|[\u10000}-\u1FFFD]+|[\u20000}-\u2FFFD]+|[\u30000}-\u3FFFD]+|[\u40000}-\u4FFFD]+|[\u50000}-\u5FFFD]+|[\u60000}-\u6FFFD]+|[\u70000}-\u7FFFD]+|[\u80000}-\u8FFFD]+|[\u90000}-\u9FFFD]+|[\uA0000}-\uAFFFD]+|[\uB0000}-\uBFFFD]+|[\uC0000}-\uCFFFD]+|[\uD0000}-\uDFFFD]+|[\uE1000}-\uEFFFD]+)+$' )

      ( 1.3.6.1.4.1.56521.101.2.1.7
          DESC 'X.680, cl. 12.3: Identifier'
          X-PATTERN '^[a-z](-?[A-Za-z0-9]+)*$' )

      ( 1.3.6.1.4.1.56521.101.2.1.18
          DESC 'X.660, cl. A.2-A.3: StandardizedNameForm'
          X-PATTERN '^\{(([a-z](-?[A-Za-z0-9]+)*)|\d+)+\}$' )

      ( 1.3.6.1.4.1.56521.101.2.1.19
          DESC 'X.680, cl. 32.3: NameAndNumberForm'
          X-PATTERN '^[a-z](-?[A-Za-z0-9]+)*(\(\d+\))$' )

      ( 1.3.6.1.4.1.56521.101.2.1.20
          DESC 'X.660, cl. A.7: Long Arc'
          X-PATTERN '^\/([A-Za-z0-9\-._~]+|[\uA0000-\uD7FF]+|[\uF900}-\uFDCF]+|[\uFDF0}-\uFFEF]+|[\u10000}-\u1FFFD]+|[\u20000}-\u2FFFD]+|[\u30000}-\u3FFFD]+|[\u40000}-\u4FFFD]+|[\u50000}-\u5FFFD]+|[\u60000}-\u6FFFD]+|[\u70000}-\u7FFFD]+|[\u80000}-\u8FFFD]+|[\u90000}-\u9FFFD]+|[\uA0000}-\uAFFFD]+|[\uB0000}-\uBFFFD]+|[\uC0000}-\uCFFFD]+|[\uD0000}-\uDFFFD]+|[\uE1000}-\uEFFFD]+)+$' )
'''

# Match text
if ftyp == 'opendj' and csyn:
    text = syntaxes + text
schema_matches = schema_pattern.findall(text)

## Make sure we got something
if len(schema_matches) == 0:
    print("# No definitions parsed")
    sys.exit(2)

at = 'attributetype '
ls = 'ldapsyntax' # OpenDJ only
oc = 'objectclass '
nf = 'nameform ' # just guessing; not supported

## specify a header to place the the top of
## the output stream.
header = '## OID Directory schema - EXPERIMENTAL USE ONLY\n'
header = header + '## Formatted for ' + ftyp + '\n'
header = header + '## Sourced from ' + doc + '\n##'

## syntax replacements (OpenDJ only)
syn_repls = {}

## adjust our presentation just a tad in the
## event we're formatting for 389DS or OpenDJ
if ftyp == '389ds':
    header = header + "\n## NOTE: 389DS >=1.4.3 required for UUID support"
    header = header + "\n#\ndn: cn=schema\n#"
    at = 'attributetypes: '
    oc = 'objectclasses: '
    nf = 'nameforms: ' # just guessing; not supported
elif ftyp == 'opendj':
    header = header + "\n#\ndn: cn=schema\n"
    header = header + "objectClass: top\n"
    header = header + "objectClass: ldapSubentry\n"
    header = header + "objectClass: subschema\n#"
    at = 'attributeTypes: '
    ls = 'ldapSyntaxes: '
    oc = 'objectClasses: '
    nf = 'nameForms: '
    ## syntax replacement dict structure:
    ##
    ##     attributeOID(k) : replacementSyntaxOID(v)
    ##
    ## Note that some syntaxes are used by
    ## more than one attribute type
    syn_repls = {
        '1.3.6.1.4.1.56521.101.2.3.3':'1.3.6.1.4.1.56521.101.2.1.3',
        '1.3.6.1.4.1.56521.101.2.3.4':'1.3.6.1.4.1.56521.101.2.1.4',
        '1.3.6.1.4.1.56521.101.2.3.5':'1.3.6.1.4.1.56521.101.2.1.5',
        '1.3.6.1.4.1.56521.101.2.3.6':'1.3.6.1.4.1.56521.101.2.1.5',
        '1.3.6.1.4.1.56521.101.2.3.7':'1.3.6.1.4.1.56521.101.2.1.7',
        '1.3.6.1.4.1.56521.101.2.3.8':'1.3.6.1.4.1.56521.101.2.1.7',
        '1.3.6.1.4.1.56521.101.2.3.18':'1.3.6.1.4.1.56521.101.2.1.18',
        '1.3.6.1.4.1.56521.101.2.3.19':'1.3.6.1.4.1.56521.101.2.1.19',
        '1.3.6.1.4.1.56521.101.2.3.20':'1.3.6.1.4.1.56521.101.2.1.20'}

ats = [] # attribute types
lss = [] # ldap syntaxes
ocs = [] # object classes
nfs = [] # name forms
unk = [] # unknown items

xorigin = "X-ORIGIN 'draft-coretta-oiddir-schema' )"
ten_lead = "          "

# Collect the schema definitions, separating them
# in appropriate list instances and performing any
# touch-ups per user config ...
for val in schema_matches:
    value = val[0].strip()

    if not noxo:
        ## Include the X-ORIGIN of the I-D for tracking
        ## purposes, taking into account newline prefs.
        if nonl:
           value = value[:-1] + xorigin
        else:
           value = value[:-1] + "\n" + ten_lead + xorigin

    if value.startswith('( 1.3.6.1.4.1.56521.101.2.1') and ftyp == 'opendj':
        if nonl:
            ## remove newlines and collapse consecutive spaces
            value = value.replace("\r", "").replace("\n", "")
            value = re.sub(' +', ' ', value)
        lss.append(ls + value)
    elif value.startswith('( 1.3.6.1.4.1.56521.101.2.3'):
        if ftyp == 'opendj' and csyn:
            ## if type is opendj and custom syntaxes
            ## have been enabled, adjust eligible attrs
            ## as needed ...

            ## o is the numeric OID of the attr, which
            ## is the key of an attr in the syn_repls
            ## dict. Presence in this dict means that
            ## a custom syntax will be imposed upon attr.
            o = value[2:].split(' ')[0].replace("\r", "").replace("\n", "")
            modt = 'replacement'

            ## handle syntax replacements
            if o in syn_repls:
                explsyn = r"SYNTAX\s(0|1|2)(\.\d+)+"
                subt = r"SUP\s\w+"
                repl = 'SYNTAX ' + syn_repls[o]
            
                if re.search(explsyn, value):
                    value = re.sub(explsyn, repl, value)
                else:
                    match = re.search(subt, value)
                    if match:
                        value = f"{value[:match.end()]}\n{ten_lead}SYNTAX {syn_repls[o]}{value[match.end():]}"

                ## Add a warning eXtension to let administrators
                ## know that we've supplanted some of the syntax
                ## definitions used in the I-D series with custom
                ## syntaxes that address the concerns stated in
                ## Section 2.1 of the RASCHEMA I-D, et al.
                value = value.replace('draft-coretta-oiddir-schema\'',
                    "draft-coretta-oiddir-schema'\n" + ten_lead +
                    "X-WARNING 'syntax " + modt + "'")

        if nonl:
            ## remove newlines and collapse consecutive spaces
            value = value.replace("\r", "").replace("\n", "")
            value = re.sub(' +', ' ', value)
        ats.append(at + value)
    elif value.startswith('( 1.3.6.1.4.1.56521.101.2.5'):
        if nonl:
            ## remove newlines and collapse consecutive spaces
            value = value.replace("\r", "").replace("\n", "")
            value = re.sub(' +', ' ', value)
        ocs.append(oc + value)
    elif value.startswith('( 1.3.6.1.4.1.56521.101.2.7'):
        if ftyp == 'opendj':
            if nonl:
                ## remove newlines and collapse consecutive spaces
                value = value.replace("\r", "").replace("\n", "")
                value = re.sub(' +', ' ', value)
            nfs.append(nf + value)
        else:
            # nameForms aren't supported by either OpenLDAP or 389DS
            # so we'll comment those definitions out, and leave them
            # in place just for reference.
            if nonl:
                ## remove newlines and collapse consecutive spaces
                value = value.replace("\r", "").replace("\n", "")
                value = re.sub(' +', ' ', value)
            else:
                ## disable individual line-based clauses
                value = value.replace("\r","\r#").replace("\n","\n#")
            nfs.append(nf + value)
    else:
        # We got something odd. Make a note of it.
        unk.append(value)

print(header)
if ftyp == 'opendj':
    print("# " + str(len(lss)) + ' CUSTOM ldap syntaxes\n#')
    for syn in lss:
        print(syn)
        print('#')

print("# " + str(len(ats)) + ' attribute types\n#')
for atype in ats:
    print(atype)
    print('#')

print("# " + str(len(ocs)) + ' object classes\n#')
for oclass in ocs:
    print(oclass)
    print('#')

if ftyp == 'opendj':
    print("# " + str(len(nfs)) + ' name forms\n#')
    for form in nfs:
        print(form)
        print('#')
else:
    print("# " + str(len(nfs)) + ' (disabled) name forms\n#')
    for form in nfs:
        print('#' + form)
        print('#')

## Ideally, the number of 'unknown elements' should
## always be zero (0).
if len(unk) > 0:
    print("# " + str(len(unk)) + ' unknown elements\n#')
    for wat in unk:
        print('#' + wat)
        print('#\n#')
    sys.exit(2)

## No apparent errors
sys.exit(0)

