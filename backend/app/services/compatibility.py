"""
Centralized Blood Compatibility Service.
Standard ABO and Rh D blood type compatibility rules matrix for whole blood / packed red blood cells (RBC).
"""

COMPATIBILITY_MATRIX = {
    # Recipient: [Compatible Donors]
    "O-":  ["O-"],
    "O+":  ["O-", "O+"],
    "A-":  ["A-", "O-"],
    "A+":  ["A+", "A-", "O+", "O-"],
    "B-":  ["B-", "O-"],
    "B+":  ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
}

def is_blood_compatible(donor_group: str, recipient_group: str) -> bool:
    """
    Returns True if donor_group can donate RBC/whole blood to recipient_group.
    Handles exact casing and whitespace.
    """
    d_grp = donor_group.strip().upper()
    r_grp = recipient_group.strip().upper()
    compatible_donors = COMPATIBILITY_MATRIX.get(r_grp, [])
    return d_grp in compatible_donors

def get_compatible_donors(recipient_group: str) -> list[str]:
    """
    Returns list of donor blood groups compatible with the recipient blood group.
    """
    r_grp = recipient_group.strip().upper()
    return COMPATIBILITY_MATRIX.get(r_grp, [r_grp])
