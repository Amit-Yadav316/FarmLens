from __future__ import annotations

from farmlens.features.schemes.schemas import Scheme

SCHEMES: list[Scheme] = [
    Scheme(
        name="PM-KISAN",
        name_hi="पीएम-किसान",
        description="Income support of Rs 6000/year to small and marginal farmers.",
        description_hi="छोटे और सीमांत किसानों को 6000 रु/वर्ष की आय सहायता।",
        eligibility="Small and marginal farmers owning up to 2 hectares.",
        benefit="Rs 2000 every 4 months directly to bank account.",
        url="https://pmkisan.gov.in",
    ),
    Scheme(
        name="PM Fasal Bima Yojana",
        name_hi="प्रधानमंत्री फसल बीमा योजना",
        description="Crop insurance scheme providing financial support for crop failure.",
        description_hi="फसल नुकसान पर वित्तीय सहायता प्रदान करने वाली बीमा योजना।",
        eligibility="All farmers growing notified crops.",
        benefit="Insurance coverage for crop loss due to natural calamities.",
        url="https://pmfby.gov.in",
    ),
    Scheme(
        name="Kisan Credit Card",
        name_hi="किसान क्रेडिट कार्ड",
        description="Provides short-term credit to farmers for crop cultivation.",
        description_hi="किसानों को फसल खेती के लिए अल्पकालिक ऋण प्रदान करता है।",
        eligibility="All farmers, sharecroppers, and tenant farmers.",
        benefit="Revolving credit up to Rs 3 lakh at subsidised interest.",
        url="https://www.nabard.org/content1.aspx?id=591",
    ),
]
