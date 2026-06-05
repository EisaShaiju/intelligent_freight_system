from langchain_core.tools import tool

# --- THE KNOWLEDGE BASE ---
COMPLIANCE_MANUAL = """
IBS AIRLINE LOGISTICS COMPLIANCE MANUAL - SECTION 4: DANGEROUS GOODS (DGR)

Clause 4.1 - Standard Goods Damage: 
Any standard consumer package with compromised outer packaging must be reinforced with heavy-duty tape and signed off by a Level 1 Supervisor.

Clause 4.2 - Heavy Machinery & Geotechnical Sensors: 
Standard mechanical parts without hazardous fluids can be re-crated using Grade-B lumber and cleared for air freight after a structural integrity check.

Clause 4.3 - Industrial Lithium-Ion Batteries (UN3480): 
This applies strictly to high-capacity power units used in heavy mining machinery and deep-shaft autonomous ventilation sensors. 
- SUB-CLAUSE A (DELAY): If delayed over 24 hours, thermal monitoring logs must be verified.
- SUB-CLAUSE B (DAMAGE): CRITICAL WARNING. If the outer packaging of industrial Lithium-Ion equipment is breached or crushed, it poses a severe thermal runaway risk, especially in enclosed transit.
  ACTION REQUIRED: 
  1. The package is permanently BANNED from Air Freight. 
  2. It must be immediately isolated in a Class-D Fireproof Quarantine Bin.
  3. All routing must be switched to Surface Transport (Rail/Truck) using a Hazmat-certified carrier.
"""

@tool
def query_compliance_manual(search_term: str) -> str:
    """
    Searches the official airline dangerous goods manual. 
    Always use this tool to check rules for damaged items, heavy machinery, or restricted goods.
    """
    return COMPLIANCE_MANUAL

@tool
def search_alternative_flights(current_location: str, destination: str) -> str:
    """Tool to find the next available cargo space for delayed routing."""
    return f"Found flight BA123 leaving {current_location} with available cargo capacity."

@tool
def find_nearest_staff(location: str) -> str:
    """Tool to query the HR API for available ground staff and their certifications."""
    return f"Employee ID 8842 (Hazmat & Heavy Machinery Certified) is currently available near {location}."