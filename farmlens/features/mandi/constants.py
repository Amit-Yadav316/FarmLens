from __future__ import annotations

# Maps Hindi/regional crop names to English API names
CROP_MAP: dict[str, str] = {
    "गेहूं": "Wheat",
    "चावल": "Rice",
    "मक्का": "Maize",
    "प्याज": "Onion",
    "आलू": "Potato",
    "टमाटर": "Tomato",
    "सोयाबीन": "Soyabean",
    "कपास": "Cotton",
    "गन्ना": "Sugarcane",
    "सरसों": "Mustard",
}

# Maps state names to Agmarknet state codes
STATE_CODE_MAP: dict[str, str] = {
    "Uttar Pradesh": "UP",
    "Maharashtra": "MH",
    "Punjab": "PB",
    "Haryana": "HR",
    "Madhya Pradesh": "MP",
    "Rajasthan": "RJ",
    "Gujarat": "GJ",
    "Karnataka": "KA",
    "Andhra Pradesh": "AP",
    "Tamil Nadu": "TN",
}
