/*
* draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
* Jesse Coretta (08/27/2024)
*/

/*
* RegistrationBase is a global variable that contains a string distinguished name
* indicative of the location of registration entries within the RA DIT.
*
* Tweak as needed. As matching is not case sensitive, feel free to use the
* proper case-folding scheme desired for your DIT.
*/
const RegistrationBase = 'ou=Registrations,o=rA';

/*
* oid2dn returns a string distinguished name (dn) based on the input
* dotNotation (dot) string value.
*
* See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
*/
function oid2dn(dot) {
    if (!dot) {
        return "";
    }

    let arcs = dot.split('.');
    arcs.reverse();
    let dn = 'n=' + arcs.join(',n=') + ',' + RegistrationBase;
    return dn;
}

/*
* dn2oid returns a string dotNotation (dot) based on the input distinguished name (dn) string value.
*
* See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
*
* NOTE: case is not significant in the suffix matching process.
*/
function dn2oid(dn) {
    dn = dn.toLowerCase();
    let base = RegistrationBase.toLowerCase();

    if (!dn.endsWith(',' + base) || dn.length + 1 < base.length) {
        return "";
    }

    let component = dn.slice(0, -(',' + base).length).split(',');
    let dot = component.reverse().map(n => n.split('=')[1]).join('.');
    return dot;
}

let dn = oid2dn('1.3.6.1.4.1.56521');
let oid = dn2oid(dn);

console.log(`dn: ${dn}`);
console.log(`oid: ${oid}`);
