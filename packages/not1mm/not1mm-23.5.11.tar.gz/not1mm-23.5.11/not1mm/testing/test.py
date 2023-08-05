"""d"""

columns = {
    0: "YYYY-MM-DD HH:MM:SS",
    1: "Call",
    2: "Freq",
    3: "Snt",
    4: "Rcv",
    5: "SentNr",
    6: "RcvNr",
    7: "Exchange1",
    8: "Sect",
    9: "WPX",
    10: "Power",
    11: "M1",
    12: "ZN",
    13: "M2",
    14: "PFX",
    15: "PTS",
    16: "Name",
    17: "Comment",
    18: "UUID",
    19: "",
    20: "",
}


def get_column(name: str) -> int:
    """d"""
    for key, value in columns.items():
        if value == name:
            return key


print(get_column("Exchange1"))

for a in ("wee", "nis"):
    print(a)
