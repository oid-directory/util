/*
draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
Jesse Coretta (08/27/2024)

Execute oid2dn and/or dn2oid as needed. Both operations are
entirely string-based. This is to (easily) get around Go's
annoying uint64 ceiling, which breaks X.667 UUID OIDs, among
other number form values greater than ^uint64(0).

If arbitrary precision of any magnitude is desired, see my
go-objectid package at the following URL and adjust this
main example accordingly:

  - https://github.com/JesseCoretta/go-objectid
*/

package main

import (
	"fmt"
	"strings"
)

func main() {
	dn := oid2dn(`1.3.6.1.4.1.56521`)
	oid := dn2oid(dn)

	fmt.Printf("dn: %s\n", dn)
	fmt.Printf("oid: %v\n", oid)
}

/*
RegistrationBase is a global constant that contains a string distinguished name
indicative of the location of registration entries within the RA DIT.

Tweak as needed. As matching is not case sensitive, feel free to use the
proper case-folding scheme desired for your DIT.
*/
const RegistrationBase = `ou=Registrations,o=RA`

/*
oid2dn returns a string distinguished name (dn) based on the input
dotNotation (dot) string value.

See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
*/
func oid2dn(dot string) (dn string) {
	if len(dot) == 0 {
		return
	}

	var arcs []string = strings.Split(dot, `.`)
	// Reverse the arcs slice
	for i, j := 0, len(arcs)-1; i < j; i, j = i+1, j-1 {
		arcs[i], arcs[j] = arcs[j], arcs[i]
	}

	dn = `n=` + strings.Join(arcs, `,n=`) + `,` + RegistrationBase
	return
}

/*
dn2oid returns a string dotNotation (dot) based on the input distinguished
name (dn) string value.

See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.

NOTE: case is not significant in the suffix matching process.
*/
func dn2oid(dn string) (dot string) {
	dn = strings.ToLower(dn)
	base := strings.ToLower(RegistrationBase)

	if !strings.HasSuffix(dn, base) || len(dn)+1 < len(base) {
		return
	}

	component := strings.Split(strings.TrimSuffix(dn, `,`+base), `,`)
	var _dot []string
	// Iterate DN in reverse order to produce the
	// correctly-ordered dotNotation.
	for i := len(component); i > 0; i-- {
		n := strings.Split(component[i-1], `=`)
		if len(n) != 2 {
			// The slices should never be anything other
			// than n=<digit+> (exactly 2 values)
			return
		}
		_dot = append(_dot, n[1])
	}

	dot = strings.Join(_dot, `.`)

	return
}
