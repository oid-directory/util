## draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
## Jesse Coretta (08/27/2024)
##
## Usage: source from your `.bashrc` (or `.bash_profile` on some
## distros) and execute either function as needed.  Don't forget
## to (persistently!) set your $REGISTRATION_BASE env var ...

## oid2dn (3D) :: See Section 3.1.3 of 'draft-coretta-oiddir-radit' 
function oid2dn() {
        if [[ -z $1 ]]; then
                ## no input == fail
                return
        fi
        
        if [[ -z $REGISTRATION_BASE ]]; then
                ## Use default base if otherwise unspecified
                REGISTRATION_BASE='ou=Registrations,o=rA'
        fi
        
        echo -n $1 | sed 's/n=//g' | sed 's/\,/./g' | awk -F. '{for(i=NF;i>0;i--) printf "n=%s,", $i} END {print "'$REGISTRATION_BASE'"}' | sed 's/,$//'
}                                                                       
                                                                        
## dn2oid (3D) :: See Section 3.1.3 of 'draft-coretta-oiddir-radit'
## NOTE: case is not significant in the suffix matching process.
function dn2oid() {
        if [[ -z $1 ]]; then
                ## no input == fail
                return
        fi

        if [[ -z $REGISTRATION_BASE ]]; then
                ## Use default base if otherwise unspecified
                REGISTRATION_BASE='ou=Registrations,o=rA'
        fi

        ## caseIgnoreMatch the registration base as the
        ## suffix of the input value ("ends with").  If
        ## no match, nothing is returned.
        if [[ "${1,,}" = *"${REGISTRATION_BASE,,}" ]]; then
            echo -n $1 | sed "s/,$REGISTRATION_BASE//I" | sed 's/n=//g' | sed 's/\,/./g' | awk -F. '{for(i=NF;i>0;i--) printf "%s%s", $i, (i>1?".":"")}'
        fi
}
