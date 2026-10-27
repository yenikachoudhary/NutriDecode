"""Source-backed evidence service for food additives.

Provides structured, authority-backed scientific and regulatory evidence
from the WHO/FAO Joint Expert Committee on Food Additives (JECFA) and the
Food Safety and Standards Authority of India (FSSAI).
"""

from copy import deepcopy

# Primary regulatory and scientific sources with traceable roots
SOURCES = {
    "fssai": {
        "name": "Food Safety and Standards Authority of India",
        "title": "FSS (Food Products Standards and Food Additives) Regulations",
        "url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        "source_type": "Indian regulatory reference",
        "jurisdiction": "India",
    },
    "jecfa": {
        "name": "WHO/FAO Joint Expert Committee on Food Additives (JECFA)",
        "title": "JECFA Chemical Evaluation & Toxicological Monograph Database",
        "url": "https://apps.who.int/food-additives-contaminants-jecfa-database/",
        "source_type": "International scientific evaluation",
        "jurisdiction": "Global / WHO-FAO",
    },
}

# Additive catalogue with authoritative JECFA evaluation records,
# direct URLs, verified ADI values, and FSSAI functional classifications.
ADDITIVE_EVIDENCE = {
    "330": {
        "code": "330",
        "name": "Citric acid",
        "ins_number": "INS 330",
        "e_number": "E330",
        "purpose": "Acidity regulator",
        "functional_classes": ["Acidity regulator", "Antioxidant synergist", "Sequestrant"],
        "chemical_identity": {
            "cas_number": "77-92-9",
            "formula": "C6H8O7",
            "synonyms": ["2-hydroxypropane-1,2,3-tricarboxylic acid"],
        },
        "evidence_status": "identity_reference",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Acceptable Daily Intake without numerical limit when used per Good Manufacturing Practice)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 17th Report (TRS 539, 1973)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011 (Appendix A)",
            "conditions": "Permitted according to Good Manufacturing Practice (GMP) in processed fruits, beverages, confectionery, and seasonings.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/1410",
            "summary": "Citric acid is a normal intermediary constituent of cellular metabolism (Krebs cycle) in human and animal tissues.",
            "acute_effects": "Low acute toxicity. Concentrated solutions may cause dental enamel erosion or mucous membrane irritation due to acidity.",
            "excessive_exposure": "High concentrated intake can cause gastric discomfort in sensitive individuals.",
            "chronic_effects": "No evidence of carcinogenicity, mutagenicity, or reproductive toxicity in long-term animal studies.",
            "sensitivities": "True allergic reactions are exceptionally rare; intolerance is occasionally reported with concentrated citrus extracts.",
        },
    },
    "296": {
        "code": "296",
        "name": "Malic acid",
        "ins_number": "INS 296",
        "e_number": "E296",
        "purpose": "Acidity regulator",
        "functional_classes": ["Acidity regulator", "Flavouring agent"],
        "chemical_identity": {
            "cas_number": "6915-15-7",
            "formula": "C4H6O5",
            "synonyms": ["DL-malic acid", "hydroxybutanedioic acid"],
        },
        "evidence_status": "identity_reference",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified for adults; D(-)-malic acid not recommended for infant foods due to incomplete metabolic clearance",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 13th Report (TRS 445, 1969)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in general processed foods at GMP. Restrictions apply to infant foods.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/1865",
            "summary": "L-Malic acid is a naturally occurring intermediate of carbohydrate metabolism. DL-malic acid is metabolized efficiently in adults.",
            "acute_effects": "Low acute toxicity. High local acidity may cause mucosal irritation.",
            "excessive_exposure": "May cause gastrointestinal irritation if ingested in high unbuffered concentrations.",
            "chronic_effects": "No evidence of chronic toxic effects or cumulative toxicity observed.",
            "sensitivities": "No significant allergenicity established.",
        },
    },
    "334": {
        "code": "334",
        "name": "Tartaric acid",
        "ins_number": "INS 334",
        "e_number": "E334",
        "purpose": "Acidity regulator",
        "functional_classes": ["Acidity regulator", "Antioxidant synergist", "Sequestrant"],
        "chemical_identity": {
            "cas_number": "87-69-4",
            "formula": "C4H6O6",
            "synonyms": ["L(+)-tartaric acid", "dihydroxysuccinic acid"],
        },
        "evidence_status": "identity_reference",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 30.0,
            "status": "numeric",
            "text": "0 - 30 mg/kg body weight/day (as L(+)-tartaric acid)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 21st Report (TRS 617, 1977)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in specified fruit products, confectionery, and powdered beverage mixes with category-specific maximum levels.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2890",
            "summary": "Occurs naturally in grapes and wine. Poorly absorbed in human intestine (~20%); remainder metabolized by colonic flora.",
            "acute_effects": "Large single doses can act as a laxative due to osmotic effects.",
            "excessive_exposure": "Excessive intake (>200 mg/kg) may cause renal or intestinal irritation.",
            "chronic_effects": "Long-term studies showed no chronic toxicity below the NOAEL (3000 mg/kg bw/day).",
            "sensitivities": "Non-allergenic.",
        },
    },
    "551": {
        "code": "551",
        "name": "Silicon dioxide",
        "ins_number": "INS 551",
        "e_number": "E551",
        "purpose": "Anti-caking agent",
        "functional_classes": ["Anti-caking agent", "Carrier", "Defoaming agent"],
        "chemical_identity": {
            "cas_number": "7631-86-9",
            "formula": "SiO2",
            "synonyms": ["Amorphous silica", "synthetic amorphous silica"],
        },
        "evidence_status": "identity_reference",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Synthetic amorphous silica, food grade)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 29th Report (TRS 733, 1985)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted up to 2.0% (20,000 mg/kg) in dry seasoning mixes, salt, and powdered food matrices.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/3028",
            "summary": "Food-grade amorphous silica is biologically inert and essentially unabsorbed through the gastrointestinal tract, excreted unchanged in feces.",
            "acute_effects": "Negligible oral toxicity.",
            "excessive_exposure": "Oral exposure does not present the pulmonary hazards associated with crystalline silica inhalation.",
            "chronic_effects": "No cumulative toxicity, carcinogenicity, or genotoxicity in dietary animal studies.",
            "sensitivities": "No allergenicity reported.",
        },
    },
    "160c": {
        "code": "160c",
        "name": "Paprika extract",
        "ins_number": "INS 160c",
        "e_number": "E160c",
        "purpose": "Colouring agent",
        "functional_classes": ["Colouring agent", "Natural extract"],
        "chemical_identity": {
            "cas_number": "465-42-9 / 470-38-2",
            "formula": "Mixture (Capsanthin, Capsorubin)",
            "synonyms": ["Paprika oleoresin", "capsanthin extract"],
        },
        "evidence_status": "identity_reference",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 1.5,
            "status": "numeric",
            "text": "0 - 1.5 mg/kg body weight/day (expressed as total carotenoids)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 69th Report (TRS 952, 2008)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted natural colouring agent in snack foods, spice seasonings, soups, and processed meats under GMP/specified limits.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/4758",
            "summary": "Obtained by solvent extraction of dried pods of Capsicum annuum L. Principal pigment compounds are capsanthin and capsorubin.",
            "acute_effects": "Low acute oral toxicity.",
            "excessive_exposure": "High intake may cause temporary benign skin discoloration (carotenodermia).",
            "chronic_effects": "Long-term feeding trials in rats showed no carcinogenic effect or reproductive impairment.",
            "sensitivities": "Occasional sensitivity in persons allergic to nightshade (Solanaceae) species.",
        },
    },
    "150d": {
        "code": "150d",
        "name": "Caramel IV (Sulphite ammonia caramel)",
        "ins_number": "INS 150d",
        "e_number": "E150d",
        "purpose": "Colouring agent",
        "functional_classes": ["Colouring agent"],
        "chemical_identity": {
            "cas_number": "8028-89-5",
            "formula": "Complex polymer",
            "synonyms": ["Class IV caramel", "sulfite ammonia caramel"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 200.0,
            "status": "numeric",
            "text": "0 - 200 mg/kg body weight/day (on solids basis)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 29th Report (TRS 733, 1985)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in carbonated beverages, sauces, instant noodle tastemakers, and confectionery with specified limits.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/1701",
            "summary": "Produced by heat treatment of food carbohydrates in presence of sulfite and ammonium compounds. Evaluated comprehensively by JECFA and EFSA.",
            "acute_effects": "Low acute oral toxicity.",
            "excessive_exposure": "4-MEI (4-methylimidazole) impurity is strictly limited in regulatory specifications (<250 mg/kg on colour basis) to prevent neurotoxicity.",
            "chronic_effects": "No adverse effects in 2-year studies at levels within the acceptable daily intake.",
            "sensitivities": "May contain trace residual sulphites; individuals sensitive to sulphites should review declaring thresholds.",
        },
    },
    "322": {
        "code": "322",
        "name": "Lecithins",
        "ins_number": "INS 322",
        "e_number": "E322",
        "purpose": "Emulsifier",
        "functional_classes": ["Emulsifier", "Antioxidant synergist", "Stabilizer"],
        "chemical_identity": {
            "cas_number": "8002-43-5",
            "formula": "Phospholipid mixture",
            "synonyms": ["Soy lecithin", "sunflower lecithin", "phosphatidylcholine"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Essential natural nutrient component of cellular membranes)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 17th Report (TRS 539, 1973)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted at GMP in chocolate, bakery products, instant mixes, and margarines. Allergen labelling required if derived from soy.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/3828",
            "summary": "Phospholipid mixture essential in human diet and biological cell membranes. Hydrolyzed normally by digestive lipases.",
            "acute_effects": "Non-toxic dietary constituent.",
            "excessive_exposure": "Extremely high intake (>30 g/day) may cause mild gastrointestinal looseness.",
            "chronic_effects": "No chronic toxicity or oncogenicity identified.",
            "sensitivities": "Source-dependent: Soy-derived lecithin may contain trace soy proteins triggering reactions in severe soy-allergic consumers.",
        },
    },
    "500": {
        "code": "500",
        "name": "Sodium carbonates",
        "ins_number": "INS 500",
        "e_number": "E500",
        "purpose": "Raising agent",
        "functional_classes": ["Raising agent", "Acidity regulator", "Anti-caking agent"],
        "chemical_identity": {
            "cas_number": "144-55-8",
            "formula": "NaHCO3",
            "synonyms": ["Sodium hydrogen carbonate", "baking soda", "INS 500(ii)"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_limited",
            "text": "Not limited / Not specified (Normal electrolyte constituent)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 9th Report (TRS 309, 1965)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted at GMP in biscuits, noodles, cakes, and baking powders.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2056",
            "summary": "Common mineral salt that releases carbon dioxide during baking, providing leavening action.",
            "acute_effects": "Low acute toxicity; neutralizes gastric acid.",
            "excessive_exposure": "Excessive intake contributes to dietary sodium load.",
            "chronic_effects": "No chronic toxicity; safe when used as a leavening agent.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "503": {
        "code": "503",
        "name": "Ammonium carbonates",
        "ins_number": "INS 503",
        "e_number": "E503",
        "purpose": "Raising agent",
        "functional_classes": ["Raising agent", "Acidity regulator"],
        "chemical_identity": {
            "cas_number": "1066-33-7",
            "formula": "NH4HCO3",
            "synonyms": ["Ammonium hydrogen carbonate", "baker's ammonia", "INS 503(ii)"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Decomposes completely into ammonia and CO2 during baking)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 26th Report (TRS 683, 1982)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted at GMP in dry baked goods (biscuits, crackers) where residues evaporate completely.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/431",
            "summary": "Completely volatilizes above 60°C into ammonia, water, and carbon dioxide, leaving minimal residual salts in baked products.",
            "acute_effects": "Raw salt has pungent odour; decomposes fully during cooking.",
            "excessive_exposure": "Uncooked ingestion may cause gastric irritation; negligible risk in finished baked goods.",
            "chronic_effects": "No chronic dietary toxicity.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "627": {
        "code": "627",
        "name": "Disodium 5'-guanylate",
        "ins_number": "INS 627",
        "e_number": "E627",
        "purpose": "Flavour enhancer",
        "functional_classes": ["Flavour enhancer"],
        "chemical_identity": {
            "cas_number": "5550-12-9",
            "formula": "C10H12N5Na2O8P",
            "synonyms": ["Sodium guanylate", "GMP sodium salt"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Natural ribonucleotide constituent of foods)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 41st Report (TRS 837, 1993)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in snack foods, seasoning blends, and noodle seasonings under GMP.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2573",
            "summary": "Purine nucleotide naturally present in mushrooms, meats, and yeast. Acts synergistically with glutamate to enhance savoury/umami perception.",
            "acute_effects": "Low acute toxicity.",
            "excessive_exposure": "Metabolized to uric acid; individuals with gout or hyperuricemia should monitor dietary purine intake.",
            "chronic_effects": "No evidence of carcinogenicity or mutagenicity in 2-year rodent bioassays.",
            "sensitivities": "May trigger sensitivity in individuals with purine metabolism disorders.",
        },
    },
    "631": {
        "code": "631",
        "name": "Disodium 5'-inosinate",
        "ins_number": "INS 631",
        "e_number": "E631",
        "purpose": "Flavour enhancer",
        "functional_classes": ["Flavour enhancer"],
        "chemical_identity": {
            "cas_number": "4691-65-0",
            "formula": "C10H11N4Na2O8P",
            "synonyms": ["Sodium inosinate", "IMP disodium salt"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Natural cellular ribonucleotide)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 41st Report (TRS 837, 1993)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted under GMP in processed foods, often alongside INS 627.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2574",
            "summary": "Purine ribonucleotide naturally occurring in fish, meat, and fermented foods. Provides umami taste synergy.",
            "acute_effects": "Low acute toxicity.",
            "excessive_exposure": "Catabolized to uric acid. Caution recommended for patients on low-purine regimens for gout.",
            "chronic_effects": "No reproductive or chronic dietary hazards demonstrated.",
            "sensitivities": "Non-allergenic; caution for gout patients.",
        },
    },
    "635": {
        "code": "635",
        "name": "Disodium 5'-ribonucleotides",
        "ins_number": "INS 635",
        "e_number": "E635",
        "purpose": "Flavour enhancer",
        "functional_classes": ["Flavour enhancer"],
        "chemical_identity": {
            "cas_number": "4691-65-0 / 5550-12-9",
            "formula": "Equimolar mixture (IMP + GMP)",
            "synonyms": ["I+G", "sodium ribonucleotides"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (JECFA 18th Report, 1974)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 18th Report (TRS 557, 1974)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in instant noodles, seasoning mixes, chips, and snacks at GMP.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2575",
            "summary": "A 50:50 mixture of disodium inosinate and disodium guanylate, highly effective at reinforcing savory flavors at parts-per-million levels.",
            "acute_effects": "Low acute oral toxicity.",
            "excessive_exposure": "Metabolized to uric acid; requires moderation for gout sufferers.",
            "chronic_effects": "No chronic toxicity in extensive animal testing.",
            "sensitivities": "Occasional idiopathic pseudo-allergic rash reported in predisposed individuals at high doses.",
        },
    },
    "440": {
        "code": "440",
        "name": "Pectins",
        "ins_number": "INS 440",
        "e_number": "E440",
        "purpose": "Stabilizer / Thickener",
        "functional_classes": ["Gelling agent", "Thickener", "Stabilizer"],
        "chemical_identity": {
            "cas_number": "9000-69-5",
            "formula": "Poly-D-galacturonic acid methyl ester",
            "synonyms": ["Citrus pectin", "apple pectin"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Natural soluble dietary fiber)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 25th Report (TRS 669, 1981)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in fruit nectars, jams, jellies, and dairy desserts under GMP.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/4038",
            "summary": "Complex polysaccharide extracted from citrus peels or apple pomace. Acts as a soluble dietary fiber, fermented in the colon into beneficial short-chain fatty acids.",
            "acute_effects": "Non-toxic dietary fiber.",
            "excessive_exposure": "Excessive doses (>20 g/day) may cause bloating, flatulence, or mild loose stools.",
            "chronic_effects": "Promotes colonic health without toxic potential.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "300": {
        "code": "300",
        "name": "Ascorbic acid",
        "ins_number": "INS 300",
        "e_number": "E300",
        "purpose": "Antioxidant",
        "functional_classes": ["Antioxidant", "Flour treatment agent", "Nutrient supplement"],
        "chemical_identity": {
            "cas_number": "50-81-7",
            "formula": "C6H8O6",
            "synonyms": ["L-Ascorbic acid", "Vitamin C"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Essential water-soluble human vitamin)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 17th Report (TRS 539, 1973)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted at GMP in fruit beverages, flour, fats, and snacks as an antioxidant preventing oxidative rancidity.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/829",
            "summary": "Essential micronutrient required for collagen biosynthesis and antioxidant protection. Excess is eliminated safely in urine.",
            "acute_effects": "Low acute toxicity.",
            "excessive_exposure": "Massive supplemental doses (>2 g/day) may cause transient osmotic diarrhea or elevate oxalate excretion.",
            "chronic_effects": "Essential physiological requirement; completely non-toxic at food additive levels.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "160a": {
        "code": "160a",
        "name": "Beta-carotenes",
        "ins_number": "INS 160a",
        "e_number": "E160a",
        "purpose": "Colouring agent",
        "functional_classes": ["Colouring agent", "Pro-vitamin A fortifier"],
        "chemical_identity": {
            "cas_number": "7235-40-7",
            "formula": "C40H56",
            "synonyms": ["Beta-carotene (plant / synthetic)", "INS 160a(ii)"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 5.0,
            "status": "numeric",
            "text": "0 - 5 mg/kg body weight/day (as total carotenoids)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 57th Report (TRS 909, 2001)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in beverages, dairy, margarines, and bakery products up to specified category limits.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/1054",
            "summary": "Carotenoid pigment and provitamin A precursor found abundantly in carrots and green leafy vegetables.",
            "acute_effects": "Low acute oral toxicity.",
            "excessive_exposure": "Chronic extremely high intake can cause reversible harmless skin yellowing (carotenodermia).",
            "chronic_effects": "Safe at food additive concentrations. Note: high-dose pharmacological supplements (not food additive levels) in heavy smokers were studied in CARET trial.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "211": {
        "code": "211",
        "name": "Sodium benzoate",
        "ins_number": "INS 211",
        "e_number": "E211",
        "purpose": "Preservative",
        "functional_classes": ["Antimicrobial preservative"],
        "chemical_identity": {
            "cas_number": "532-32-1",
            "formula": "C7H5NaO2",
            "synonyms": ["Benzoate of soda"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 5.0,
            "status": "numeric",
            "text": "0 - 5 mg/kg body weight/day (expressed as benzoic acid equivalent)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 46th Report (TRS 868, 1996)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Class II preservative permitted in acidic foods (sauces, fruit juices, carbonated drinks) up to 100-750 mg/kg depending on category.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2761",
            "summary": "Inhibits mold, yeast, and bacteria in acidic environments (pH < 4.5). Rapidly conjugated with glycine in liver and excreted as hippuric acid.",
            "acute_effects": "Low acute oral toxicity (LD50 > 4000 mg/kg in rodents).",
            "excessive_exposure": "May form traces of benzene in presence of ascorbic acid (vitamin C) and transition metal catalysts under heat/UV exposure; monitored by food safety authorities.",
            "chronic_effects": "No carcinogenicity or mutagenicity in long-term rodent bioassays.",
            "sensitivities": "Can trigger pseudo-allergic symptoms, urticaria, or bronchospasm in asthmatic or salicylate-sensitive individuals.",
        },
    },
    "202": {
        "code": "202",
        "name": "Potassium sorbate",
        "ins_number": "INS 202",
        "e_number": "E202",
        "purpose": "Preservative",
        "functional_classes": ["Antimicrobial preservative"],
        "chemical_identity": {
            "cas_number": "24634-61-5",
            "formula": "C6H7KO2",
            "synonyms": ["Sorbic acid potassium salt"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_with_numeric_adi",
        "adi": {
            "value": 25.0,
            "status": "numeric",
            "text": "0 - 25 mg/kg body weight/day (expressed as sorbic acid)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 17th Report (TRS 539, 1973)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Class II preservative permitted in dairy, baked goods, juices, and sauces up to 1000 mg/kg.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2653",
            "summary": "Potassium salt of natural unsaturated fatty acid (sorbic acid). Metabolized like dietary fatty acids via beta-oxidation into water and carbon dioxide.",
            "acute_effects": "Extremely low acute oral toxicity (LD50 > 4000 mg/kg).",
            "excessive_exposure": "Well tolerated; non-toxic at dietary consumption levels.",
            "chronic_effects": "Extensively studied with no evidence of oncogenicity or reproductive impairment.",
            "sensitivities": "Occasional mild contact skin reactivity; oral allergic responses are very rare.",
        },
    },
    "307b": {
        "code": "307b",
        "name": "Mixed tocopherols concentrate",
        "ins_number": "INS 307b",
        "e_number": "E307b",
        "purpose": "Antioxidant",
        "functional_classes": ["Antioxidant"],
        "chemical_identity": {
            "cas_number": "1406-66-2",
            "formula": "C29H50O2 (alpha-tocopherol)",
            "synonyms": ["Vitamin E concentrate", "mixed tocopherols"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": 2.0,
            "status": "numeric",
            "text": "0 - 2 mg/kg body weight/day (as D-alpha-tocopherol)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 33rd Report (TRS 776, 1988)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted in vegetable oils, snacks, and bakery goods under GMP.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/4890",
            "summary": "Natural lipid-soluble antioxidant mixture containing alpha, beta, gamma, and delta tocopherols derived from edible vegetable oils.",
            "acute_effects": "Non-toxic physiological vitamin.",
            "excessive_exposure": "Very high supplemental doses (>800 mg/day) can antagonize vitamin K coagulation in clinical patients.",
            "chronic_effects": "Essential dietary micronutrient.",
            "sensitivities": "Non-allergenic.",
        },
    },
    "508": {
        "code": "508",
        "name": "Potassium chloride",
        "ins_number": "INS 508",
        "e_number": "E508",
        "purpose": "Gelling agent / Mineral salt",
        "functional_classes": ["Gelling agent", "Thickener", "Flavour enhancer", "Salt substitute"],
        "chemical_identity": {
            "cas_number": "7447-40-7",
            "formula": "KCl",
            "synonyms": ["Sylvite", "potassium muriate"],
        },
        "evidence_status": "verified_evidence",
        "assessment_status": "evaluated_safe_at_gmp",
        "adi": {
            "value": None,
            "status": "not_specified",
            "text": "Not specified (Essential dietary electrolyte)",
            "unit": "mg/kg body weight/day",
            "evaluation_reference": "JECFA 23rd Report (TRS 648, 1979)",
        },
        "regulatory_details": {
            "fssai_permitted": True,
            "standard": "FSS (Food Products Standards and Food Additives) Regulations, 2011",
            "conditions": "Permitted at GMP in processed foods, noodles, and low-sodium salt formulations.",
            "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Additives_Regulations.pdf",
        },
        "scientific_findings": {
            "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/2622",
            "summary": "Naturally occurring mineral salt used to impart potassium ions, strengthen hydrocolloid gels, or reduce sodium chloride content.",
            "acute_effects": "Low acute oral toxicity.",
            "excessive_exposure": "Individuals with chronic renal failure, hypoaldosteronism, or on potassium-sparing diuretics must limit potassium intake.",
            "chronic_effects": "Supports healthy blood pressure when substituting for sodium.",
            "sensitivities": "Non-allergenic; caution for patients with kidney disorders.",
        },
    },
}


def _build_assessment(additive: dict) -> dict:
    """Build a structured assessment response preserving backward compatibility."""
    evidence_status = additive.get("evidence_status", "identity_reference")
    adi_info = additive.get("adi", {})
    scientific = additive.get("scientific_findings", {})
    regulatory = additive.get("regulatory_details", {})

    # Create detailed short-term and long-term effects blocks
    short_term_details = None
    if "acute_effects" in scientific:
        short_term_details = {
            "acute_toxicity": scientific.get("acute_effects"),
            "excessive_exposure": scientific.get("excessive_exposure"),
            "sensitivities": scientific.get("sensitivities"),
            "evidence_type": "human_and_animal_evaluations",
            "status": "evaluated_by_jecfa",
        }

    long_term_details = None
    if "chronic_effects" in scientific:
        long_term_details = {
            "chronic_toxicity": scientific.get("chronic_effects"),
            "carcinogenicity": "No carcinogenic concern established at dietary usage levels",
            "evidence_quality": "multi_year_dietary_bioassays_evaluated_by_jecfa",
            "status": "evaluated_by_jecfa",
        }

    return {
        **deepcopy(additive),
        # Preserve original fields expected by tests and clients:
        "evidence_status": evidence_status,
        "assessment_status": additive.get("assessment_status", "insufficient_data"),
        "identity_status": "catalogue_match",
        "short_term_effects": {
            "status": "evaluated" if short_term_details else "not_assessed",
            "details": short_term_details,
        },
        "long_term_effects": {
            "status": "evaluated" if long_term_details else "not_assessed",
            "details": long_term_details,
        },
        "exposure_assessment": {
            "status": "not_calculable",
            "amount_in_product": None,
            "serving_size_g": None,
            "consumption_frequency": None,
            "body_weight_kg": None,
            "estimated_intake": None,
            "reference_intake": adi_info.get("text"),
            "applicable_adi_numeric": adi_info.get("value"),
            "reason": (
                "The additive concentration and consumption details "
                "are not declared on the package label. Do not infer exposure "
                "from ingredient order or presence alone."
            ),
        },
        "regulatory_status": (
            "fssai_permitted"
            if regulatory.get("fssai_permitted")
            else "not_verified"
        ),
        "safety_conclusion": None,  # System does not declare medical verdicts
        "evidence_quality": (
            "evaluated_by_who_fssai"
            if "jecfa_url" in scientific
            else "not_individually_verified"
        ),
        "sources": deepcopy(SOURCES),
        "limitations": [
            "A catalogue match does not independently verify the chemical purity on the package.",
            "Permitted uses depend on the specific food category under FSSAI regulations.",
            "An ADI comparison or safety evaluation requires knowing the exact concentration.",
            "Hazard under extreme or concentrated laboratory conditions does not equal risk at consumer intake quantities.",
            "This prototype provides educational intelligence and preliminary evidence, not medical diagnosis or safety certification.",
        ],
        "disclaimer": (
            "This is an evidence intelligence record, not medical advice or "
            "an authoritative determination that a product is safe or unsafe."
        ),
    }


def list_additive_evidence() -> dict:
    """Return all preliminary additive records and their assessment limitations."""
    records = [
        _build_assessment(ADDITIVE_EVIDENCE[code])
        for code in sorted(
            ADDITIVE_EVIDENCE,
            key=lambda value: (not value.isdigit(), value),
        )
    ]

    return {
        "count": len(records),
        "records": records,
        "disclaimer": (
            "Records are cross-referenced with WHO/FAO JECFA and FSSAI standards. "
            "Do not interpret missing exposure information as proof of safety or harm."
        ),
    }


def get_additive_evidence(code: str) -> dict | None:
    """Return one additive assessment by its numeric or alphanumeric code."""
    normalized_code = code.strip().lower()
    # Strip any leading 'ins' or 'e' prefix and strip roman numerals if needed
    cleaned_code = normalized_code
    if cleaned_code.startswith("ins"):
        cleaned_code = cleaned_code[3:].strip()
    elif cleaned_code.startswith("e"):
        cleaned_code = cleaned_code[1:].strip()

    # Try exact match first
    additive = ADDITIVE_EVIDENCE.get(cleaned_code)
    if not additive:
        # Try matching base number (e.g. 500ii -> 500)
        base = "".join(filter(str.isdigit, cleaned_code))
        if base and base in ADDITIVE_EVIDENCE:
            additive = ADDITIVE_EVIDENCE[base]
        else:
            # Case-insensitive search
            additive = next(
                (
                    item
                    for key, item in ADDITIVE_EVIDENCE.items()
                    if key.lower() in (cleaned_code, normalized_code)
                ),
                None,
            )

    return _build_assessment(additive) if additive else None
