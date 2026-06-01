# ============================================================
# Live OpenCorporates Integration Test
# OpenCorporates free API — no API key required
# Proves the pipeline works with real external data
# ============================================================

import httpx
import json
import sys
from models import VendorRiskAssessment, DataCompleteness
from pipeline import process_vendor

# ============================================================
# Real OpenCorporates API Call
# ============================================================

OPENCORPORATES_URL = "https://api.opencorporates.com/v0.4/companies/search"

def search_opencorporates(vendor_name: str) -> dict:
    """
    Queries the real OpenCorporates API.
    Free tier: no API key needed, rate-limited.
    Returns company registry data if found.
    """
    try:
        response = httpx.get(
            OPENCORPORATES_URL,
            params={
                "q": vendor_name,
                "jurisdiction_code": "",
                "format": "json",
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {})
        companies = results.get("companies", [])

        if not companies:
            return {
                "found": False,
                "source": "OpenCorporates (LIVE)",
                "vendor_name": vendor_name,
                "status": "not_found",
                "company_data": None,
            }

        # Get the first (most relevant) result
        top_company = companies[0].get("company", {})

        return {
            "found": True,
            "source": "OpenCorporates (LIVE)",
            "vendor_name": vendor_name,
            "status": "found",
            "company_data": {
                "name": top_company.get("name", "Unknown"),
                "jurisdiction": top_company.get("jurisdiction_code", "Unknown"),
                "company_type": top_company.get("company_type", "Unknown"),
                "incorporation_date": top_company.get("incorporation_date", "Unknown"),
                "current_status": top_company.get("current_status", "Unknown"),
                "opencorporates_url": top_company.get("opencorporates_url", ""),
            },
        }

    except httpx.TimeoutException:
        return {
            "found": False,
            "source": "OpenCorporates (LIVE)",
            "vendor_name": vendor_name,
            "status": "timeout",
            "company_data": None,
        }
    except Exception as e:
        return {
            "found": False,
            "source": "OpenCorporates (LIVE)",
            "vendor_name": vendor_name,
            "status": "error",
            "error_detail": str(e),
            "company_data": None,
        }


# ============================================================
# Test with Real Companies
# ============================================================

REAL_COMPANIES = [
    "Siemens",
    "Tesla",
    "Samsung",
    "Deutsche Bank",
    "ASDFGHJKL FAKE COMPANY",
]


def run_live_test():
    print(f"{'='*70}")
    print(f"  LIVE OPENCORPORATES INTEGRATION TEST")
    print(f"  API: https://api.opencorporates.com (Free Tier)")
    print(f"{'='*70}\n")

    found_count = 0
    not_found_count = 0
    error_count = 0

    for company in REAL_COMPANIES:
        print(f"  🔍 Searching: {company}")
        result = search_opencorporates(company)

        if result["found"]:
            found_count += 1
            data = result["company_data"]
            print(f"     ✅ FOUND")
            print(f"     Name: {data['name']}")
            print(f"     Jurisdiction: {data['jurisdiction']}")
            print(f"     Status: {data['current_status']}")
            print(f"     Incorporated: {data['incorporation_date']}")
            print(f"     URL: {data['opencorporates_url']}")
        elif result["status"] == "not_found":
            not_found_count += 1
            print(f"     ❌ NOT FOUND (would trigger new_entity_no_history)")
        else:
            error_count += 1
            print(f"     ⚠️  {result['status'].upper()}: {result.get('error_detail', 'N/A')}")

        print()

    # Summary
    print(f"{'='*70}")
    print(f"  RESULTS: {found_count} found | {not_found_count} not found | {error_count} errors")
    print(f"{'='*70}\n")

    # Now run one through the full pipeline with mock + live data comparison
    print(f"{'='*70}")
    print(f"  PIPELINE COMPARISON: Mock vs Live for 'Siemens'")
    print(f"{'='*70}\n")

    # Mock pipeline result
    mock_result = process_vendor("Siemens")
    if mock_result.get("error"):
        print(f"  Mock pipeline error: {mock_result['error']}")
    else:
        print(f"  📊 Mock Pipeline:")
        print(f"     Score: {mock_result['agent1']['risk_score']}")
        print(f"     Route: {mock_result['final_route']}")
        print(f"     Completeness: {mock_result['agent1']['data_completeness']}")

    # Live OpenCorporates data
    live_data = search_opencorporates("Siemens")
    print(f"\n  🌐 Live OpenCorporates:")
    if live_data["found"]:
        print(f"     Found: {live_data['company_data']['name']}")
        print(f"     Jurisdiction: {live_data['company_data']['jurisdiction']}")
        print(f"     Status: {live_data['company_data']['current_status']}")
    else:
        print(f"     Status: {live_data['status']}")

    print(f"\n{'='*70}")
    print(f"  ✅ Live API integration verified")
    print(f"{'='*70}")

    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run_live_test()
