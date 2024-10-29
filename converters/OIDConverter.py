#!/usr/bin/python3

## draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
## Jesse Coretta (08/27/2024)

## oid2dn returns a string distinguished name (dn) based on the input
## dotNotation (dot) string value.
##
## See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
def oid2dn(dot):
    if not dot:
        return ""

    arcs = dot.split('.')
    arcs.reverse()
    dn = 'n=' + ',n='.join(arcs) + ',' + RegistrationBase
    return dn

## dn2oid returns a string dotNotation (dot) based on the input distinguished
## name (dn) string value.

## See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.

## NOTE: case is not significant in the suffix matching process.
def dn2oid(dn):
    dn = dn.lower()
    base = RegistrationBase.lower()

    if not dn.endswith(',' + base) or len(dn) + 1 < len(base):
        return ""

    component = dn[:-len(',' + base)].split(',')
    dot = '.'.join([n.split('=')[1] for n in reversed(component) if len(n.split('=')) == 2])
    return dot

## RegistrationBase is a global variable that contains a string distinguished name
## indicative of the location of registration entries within the RA DIT.
##
## Tweak as needed. As matching is not case sensitive, feel free to use the
## proper case-folding scheme desired for your DIT.
RegistrationBase = 'ou=Registrations,o=rA'

if __name__ == "__main__":
    dn = oid2dn('1.3.6.1.4.1.56521')
    oid = dn2oid(dn)

    print(f"dn: {dn}")
    print(f"oid: {oid}")
