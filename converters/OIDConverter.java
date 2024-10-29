/*
* draft-coretta-oiddir-radit dn2oid/oid2dn (3D) converters
* Jesse Coretta (08/27/2024)
*
* Name this file OIDConverter.java.
*
* See draft-coretta-oiddir-radit Section 3.1.3 for details.
*/

public class OIDConverter {

    // RegistrationBase is a global variable that contains a string distinguished name
    // indicative of the location of registration entries within the RA DIT.
    private static final String RegistrationBase = "ou=Registrations,o=rA";

    // oid2dn returns a string distinguished name (dn) based on the input dotNotation (dot) string value.
    public static String oid2dn(String dot) {
        if (dot == null || dot.isEmpty()) {
            return "";
        }

        String[] arcs = dot.split("\\.");
        StringBuilder dn = new StringBuilder("n=");
        for (int i = arcs.length - 1; i >= 0; i--) {
            dn.append(arcs[i]);
            if (i > 0) {
                dn.append(",n=");
            }
        }
        dn.append(",").append(RegistrationBase);
        return dn.toString();
    }

    // dn2oid returns a string dotNotation (dot) based on the input distinguished name (dn) string value.
    // NOTE: case is not significant in the suffix matching process.
    public static String dn2oid(String dn) {
        if (dn == null || dn.isEmpty()) {
            return "";
        }

        dn = dn.toLowerCase();
        String base = RegistrationBase.toLowerCase();

        if (!dn.endsWith("," + base) || dn.length() + 1 < base.length()) {
            return "";
        }

        String[] components = dn.substring(0, dn.length() - ("," + base).length()).split(",");
        StringBuilder dot = new StringBuilder();
        for (int i = components.length - 1; i >= 0; i--) {
            String[] parts = components[i].split("=");
            if (parts.length == 2) {
                dot.append(parts[1]);
                if (i > 0) {
                    dot.append(".");
                }
            }
        }
        return dot.toString();
    }

    public static void main(String[] args) {
        String dn = oid2dn("1.3.6.1.4.1.56521");
        String oid = dn2oid(dn);

        System.out.println("dn: " + dn);
        System.out.println("oid: " + oid);
    }
}

