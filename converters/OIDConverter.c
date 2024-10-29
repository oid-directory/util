/*
* draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
* Jesse Coretta (08/27/2024)
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

/*
* REGISTRATION_BASE is a global variable that contains a string distinguished name
* indicative of the location of registration entries within the RA DIT.
*
* Tweak as needed. As matching is not case sensitive, feel free to use the
* proper case-folding scheme desired for your DIT.
*/
#define REGISTRATION_BASE "ou=Registrations,o=rA"

void reverse(char *str, int length) {
    int start = 0;
    int end = length - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

/*
* oid2dn returns a string distinguished name (dn) based on the input
* dotNotation (dot) string value.
*
* See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
*/
char* oid2dn(const char *dot) {
    if (dot == NULL || strlen(dot) == 0) {
        return NULL;
    }

    char *dot_copy = strdup(dot);
    char *token = strtok(dot_copy, ".");
    char **arcs = NULL;
    int count = 0;

    // Tokenize the input and store components in a dynamic array
    while (token != NULL) {
        arcs = realloc(arcs, sizeof(char*) * (count + 1));
        arcs[count++] = token;
        token = strtok(NULL, ".");
    }

    char *dn = (char *)malloc(1024);
    strcpy(dn, "n=");

    // Assemble the DN by concatentation
    for (int i = count - 1; i >= 0; i--) {
        strcat(dn, arcs[i]);
        if (i > 0) {
            strcat(dn, ",n=");
        }
    }
    strcat(dn, ",");
    strcat(dn, REGISTRATION_BASE);

    free(dot_copy);
    free(arcs);

    return dn;
}

/*
* dn2oid returns a string dotNotation (dot) based on the input
* distinguished name (dn) string value.
*
* See Section 3.1.3 of 'draft-coretta-oiddir-radit' for details.
*
* NOTE: case is not significant in the suffix matching process.
*/
char* dn2oid(const char *dn) {
    if (dn == NULL || strlen(dn) == 0) {
        return NULL;
    }

    char *base = strdup(REGISTRATION_BASE);
    // convert REGISTRATION_BASE to lowercase
    for (int i = 0; base[i]; i++) {
        base[i] = tolower(base[i]);
    }

    // convert DN to lowercase
    char *dn_copy = strdup(dn);
    char *dn_lower = strdup(dn_copy);
    for (int i = 0; dn_lower[i]; i++) {
        dn_lower[i] = tolower(dn_lower[i]);
    }

    // Make sure the suffix matches (save for
    // any variations in case folding).
    if (!strstr(dn_lower, base)) {
        free(dn_copy);
        free(base);
        free(dn_lower);
        return NULL;
    }

    // Tokenize the input and store components in a dynamic array
    char **components = NULL;
    int count = 0;
    char *component = strtok(dn_copy, ",");
    while (component != NULL) {
        components = realloc(components, sizeof(char*) * (count + 1));
        components[count++] = component;
        component = strtok(NULL, ",");
    }

    // Process the components in reverse order
    char *dot = (char *)malloc(1024);
    dot[0] = '\0';
    for (int i = count - 1; i >= 0; i--) {
        component = components[i];
        if (strstr(component, "n=") == component) {
            char *value = component + 2;
            if (strlen(dot) > 0) {
                strcat(dot, ".");
            }
            strcat(dot, value);
        }
    }

    free(dn_copy);
    free(base);
    free(dn_lower);
    free(components);
    return dot;
}

int main() {
    char *dn = oid2dn("1.3.6.1.4.1.56521");
    char *oid = dn2oid(dn);

    printf("dn: %s\n", dn);
    printf("oid: %s\n", oid);

    free(dn);
    free(oid);

    return 0;
}

