from __future__ import annotations

# Maps all supported language crop names → English Agmarknet API name
CROP_MAP: dict[str, str] = {
    # Hindi
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
    # Punjabi
    "ਕਣਕ": "Wheat",
    "ਚਾਵਲ": "Rice",
    "ਮੱਕੀ": "Maize",
    "ਪਿਆਜ਼": "Onion",
    "ਆਲੂ": "Potato",
    # Marathi
    "गहू": "Wheat",
    "तांदूळ": "Rice",
    "मका": "Maize",
    "कांदा": "Onion",
    "बटाटा": "Potato",
    # Telugu
    "గోధుమ": "Wheat",
    "బియ్యం": "Rice",
    "మొక్కజొన్న": "Maize",
    "ఉల్లిపాయ": "Onion",
    "బంగాళాదుంప": "Potato",
    # Tamil
    "கோதுமை": "Wheat",
    "அரிசி": "Rice",
    "சோளம்": "Maize",
    "வெங்காயம்": "Onion",
    "உருளைக்கிழங்கு": "Potato",
    # English passthrough
    "Wheat": "Wheat",
    "Rice": "Rice",
    "Maize": "Maize",
    "Onion": "Onion",
    "Potato": "Potato",
    "Tomato": "Tomato",
    "Soyabean": "Soyabean",
    "Cotton": "Cotton",
    "Sugarcane": "Sugarcane",
    "Mustard": "Mustard",
}

# Maps city/market names → state name for Agmarknet API filter
LOCATION_MAP: dict[str, str] = {
    "Delhi": "Delhi",
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Nashik": "Maharashtra",
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Varanasi": "Uttar Pradesh",
    "Patna": "Bihar",
    "Bhopal": "Madhya Pradesh",
    "Indore": "Madhya Pradesh",
    "Ludhiana": "Punjab",
    "Amritsar": "Punjab",
    "Chandigarh": "Punjab",
    "Ahmedabad": "Gujarat",
    "Surat": "Gujarat",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
}
