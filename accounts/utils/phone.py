import re

MZ_MOBILE_RE = re.compile(r"^\+258(82|83|84|85|86|87)\d{7}$")


def normalize_mz_phone(raw: str) -> str:
    """
    Normalize Mozambique mobile numbers to E.164:
    +258XXXXXXXXX  (9 digits after country code)

    Accepts inputs like:
      841234567
      0841234567
      +258841234567
      258841234567
      84 123 4567
    """
    if raw is None:
        raise ValueError("Phone number is required")

    s = str(raw).strip()
    s = s.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    # Convert "258..." to "+258..."
    if s.startswith("258"):
        s = "+" + s

    # Convert "0XXXXXXXXX" to "+258XXXXXXXXX"
    if s.startswith("0") and len(s) == 10:
        s = "+258" + s[1:]

    # Convert "XXXXXXXXX" to "+258XXXXXXXXX" (9-digit local mobile)
    if re.fullmatch(r"\d{9}", s):
        s = "+258" + s

    # If already +258...
    if not s.startswith("+"):
        raise ValueError("Invalid phone number format")

    if not MZ_MOBILE_RE.fullmatch(s):
        raise ValueError("Invalid Mozambique mobile number")

    return s
