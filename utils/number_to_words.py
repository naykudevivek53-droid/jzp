# Currency number-to-words converter for Marathi and English

ONESH_MR = ["", "एक", "दोन", "तीन", "चार", "पाच", "सहा", "सात", "आठ", "ऊऊ", "दहा",
            "अकरा", "बारा", "तेरा", "चौदा", "पंधरा", "सोळा", "सतरा", "अठरा", "एकोणीस"]
TENS_MR = ["", "", "वीस", "तीस", "चाळीस", "पन्नास", "साठ", "सत्तर", "अंशी", "नव्वद"]

# Special Marathi numbers for smooth reading
SPECIAL_MR = {
    21: "एकवीस", 22: "बावीस", 23: "तेवीस", 24: "चौवीस", 25: "पंचवीस", 26: "सव्वीस", 27: "सत्तावीस", 28: "अठ्ठावीस", 29: "एकोणतीस",
    31: "एकतीस", 32: "बत्तीस", 33: "तेत्तीस", 34: "चौतीस", 35: "पस्तीस", 36: "छत्तीस", 37: "सदतीस", 38: "अडतीस", 39: "एकोणचाळीस",
    41: "एकचाळीस", 42: "बेचाळीस", 43: "त्र्याचाळीस", 44: "चौचाळीस", 45: "पंचचाळीस", 46: "शास्त्रीस", 47: "सत्तेचाळीस", 48: "अठ्ठाचाळीस", 49: "एकोणपन्नास",
    51: "एकावन्न", 52: "बावन्न", 53: "त्रेपन्न", 54: "चौपन्न", 55: "पंचावन्न", 56: "छापन्न", 57: "सत्तावन्न", 58: "अठ्ठावन्न", 59: "एकोणसाठ",
    61: "एकसाठ", 62: "बासाठ", 63: "त्रेसाठ", 64: "चौसाठ", 65: "पाचसाठ", 66: "छासाठ", 67: "सदुसाठ", 68: "अडसाठ", 69: "एकोणसत्तर",
    71: "एकत्तर", 72: "बाहत्तर", 73: "त्र्याहत्तर", 74: "चौहत्तर", 75: "पंचाहत्तर", 76: "शहात्तर", 77: "सतत्तर", 78: "अठ्ठाहत्तर", 79: "एकोणांशी",
    81: "एक्यांशी", 82: "ब्यांशी", 83: "त्र्यांशी", 84: "चौऱ्यांशी", 85: "पंच्यांशी", 86: "शहांशी", 87: "सत्त्यांशी", 88: "अठ्ठ्यांशी", 89: "एकोणनव्वद",
    91: "एक्याण्णव", 92: "ब्याण्णव", 93: "त्र्याण्णव", 94: "चौऱ्याण्णव", 95: "पंच्याण्णव", 96: "शहाण्णव", 97: "सत्त्याण्णव", 98: "अठ्ठ्याण्णव", 99: "एकोणशे"
}

def _two_digits_mr(n):
    if n == 0:
        return ""
    if n < 20:
        return ONESH_MR[n]
    if n in SPECIAL_MR:
        return SPECIAL_MR[n]
    tens = n // 10
    ones = n % 10
    return TENS_MR[tens] + (" " + ONESH_MR[ones] if ones > 0 else "")

def amount_to_words_mr(amount):
    try:
        n = int(round(float(amount)))
    except (ValueError, TypeError):
        return "शून्य रुपये फक्त"
    
    if n <= 0:
        return "शून्य रुपये फक्त"

    parts = []
    
    # Lakhs
    lakhs = n // 100000
    if lakhs > 0:
        parts.append(_two_digits_mr(lakhs) + " लाख")
        n %= 100000
        
    # Thousands
    thousands = n // 1000
    if thousands > 0:
        parts.append(_two_digits_mr(thousands) + " हजार")
        n %= 1000
        
    # Hundreds
    hundreds = n // 100
    if hundreds > 0:
        parts.append(ONESH_MR[hundreds] + "शे")
        n %= 100
        
    # Remainder
    if n > 0:
        parts.append(_two_digits_mr(n))
        
    return " ".join(parts) + " रुपये फक्त"

# English words
UNITS_EN = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
TENS_EN = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

def _two_digits_en(n):
    if n < 20:
        return UNITS_EN[n]
    return TENS_EN[n // 10] + (" " + UNITS_EN[n % 10] if n % 10 != 0 else "")

def amount_to_words_en(amount):
    try:
        n = int(round(float(amount)))
    except (ValueError, TypeError):
        return "Zero Rupees Only"
        
    if n <= 0:
        return "Zero Rupees Only"
        
    parts = []
    lakhs = n // 100000
    if lakhs > 0:
        parts.append(_two_digits_en(lakhs) + " Lakh")
        n %= 100000
        
    thousands = n // 1000
    if thousands > 0:
        parts.append(_two_digits_en(thousands) + " Thousand")
        n %= 1000
        
    hundreds = n // 100
    if hundreds > 0:
        parts.append(UNITS_EN[hundreds] + " Hundred")
        n %= 100
        
    if n > 0:
        parts.append(_two_digits_en(n))
        
    return " ".join(parts) + " Rupees Only"
