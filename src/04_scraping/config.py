# src/04_scraping/config.py
from __future__ import annotations

# Ventana temporal del plan (feb–abr 2025)
SINCE = "2025-02-01"
UNTIL = "2025-05-01"  # until suele ser exclusivo

# Regex útiles (puedes ampliar)
IA_REGEX = r"\bia\b|inteligencia artificial|bots?\b|deepfake(s)?|desinformaci[oó]n|fake news"
CANDIDATE_NOB = r"\bnoboa\b|daniel noboa"
CANDIDATE_LUI = r"\bluisa\b|luisa gonz[aá]lez|luisa gonzalez"
