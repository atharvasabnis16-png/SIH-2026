from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

SYSTEM_A_BASE = "http://localhost:5001"
SYSTEM_B_BASE = "http://localhost:5002"


@router.get("/")
def read_root():
    return {"status": "backend is running"}


@router.get("/status/{aadhaar}")
def get_status(aadhaar: str):
    ration_data = None
    employment_data = None
    missing_systems = []

    # --- System A: Ration Card ---
    try:
        resp_a = requests.get(f"{SYSTEM_A_BASE}/applicant/{aadhaar}", timeout=5)
        if resp_a.status_code == 200:
            body = resp_a.json()
            ration_data = {
                "name":          body.get("applicant_name"),
                "dob":           body.get("dob"),
                "address":       body.get("address"),
                "ration_status": body.get("card_status"),
            }
        else:
            missing_systems.append("System A (Ration Card)")
    except requests.exceptions.RequestException:
        missing_systems.append("System A (Ration Card)")

    # --- System B: Employment ---
    try:
        resp_b = requests.get(f"{SYSTEM_B_BASE}/applicant/{aadhaar}", timeout=5)
        if resp_b.status_code == 200:
            body = resp_b.json()
            employment_data = {
                "name":               body.get("full_name"),
                "dob":                body.get("date_of_birth"),
                "address":            body.get("residential_address"),
                "employment_status":  body.get("emp_status"),
            }
        else:
            missing_systems.append("System B (Employment)")
    except requests.exceptions.RequestException:
        missing_systems.append("System B (Employment)")

    # --- Both systems returned nothing ---
    if ration_data is None and employment_data is None:
        raise HTTPException(
            status_code=404,
            detail="No records found for this aadhaar in any system",
        )

    # --- Merge: System A is preferred; System B fills gaps ---
    merged = {
        "aadhaar":            aadhaar,
        "name":               None,
        "dob":                None,
        "address":            None,
        "ration_status":      None,
        "employment_status":  None,
    }

    if ration_data:
        merged["name"]    = ration_data["name"]
        merged["dob"]     = ration_data["dob"]
        merged["address"] = ration_data["address"]
        merged["ration_status"] = ration_data["ration_status"]

    if employment_data:
        # Fill name/dob/address from B only if A didn't provide them
        merged["name"]    = merged["name"]    or employment_data["name"]
        merged["dob"]     = merged["dob"]     or employment_data["dob"]
        merged["address"] = merged["address"] or employment_data["address"]
        merged["employment_status"] = employment_data["employment_status"]

    merged["missing_systems"] = missing_systems

    return merged
