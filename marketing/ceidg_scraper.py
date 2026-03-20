#!/usr/bin/env python3
"""
CEIDG / BIR Company Database Scraper
Collects JDG data for e-commerce targeting

LEGAL NOTICE:
- Uses only publicly available data
- Respects rate limits
- For legitimate marketing purposes only

Data source: https://dane.biznes.gov.pl/ (public registry)
"""

import requests
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class Company:
    name: str
    nip: str
    regon: str
    pkd_code: str
    pkd_description: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    start_date: Optional[str] = None
    status: str = "active"


class CEIDGScraper:
    """
    Scraper for Polish CEIDG/BIR database
    Focuses on PKD codes related to e-commerce
    """
    
    # PKD codes for e-commerce and online sales
    ECOMMERCE_PKD = [
        "47.91.Z",  # Sprzedaż detaliczna prowadzona przez domy sprzedaży wysyłkowej lub internet
        "47.19.Z",  # Sprzedaż detaliczna prowadzona w niewyspecjalizowanych sklepach
        "47.41.Z",  # Sprzedaż detaliczna komputerów, urządzeń peryferyjnych i oprogramowania
        "47.42.Z",  # Sprzedaż detaliczna urządzeń telekomunikacyjnych
        "47.61.Z",  # Sprzedaż detaliczna książek
        "47.62.Z",  # Sprzedaż detaliczna gazet i artykułów papierniczych
        "47.63.Z",  # Sprzedaż detaliczna nagrań muzycznych i video
        "47.64.Z",  # Sprzedaż detaliczna artykułów sportowych
        "47.65.Z",  # Sprzedaż detaliczna gier i zabawek
        "47.74.Z",  # Sprzedaż detaliczna wyrobów medycznych
        "47.75.Z",  # Sprzedaż detaliczna kosmetyków i artykułów toaletowych
        "47.76.Z",  # Sprzedaż detaliczna kwiatów, roślin, nasion, nawozów
        "47.77.Z",  # Sprzedaż detaliczna zegarów, zegarków i biżuterii
        "47.78.Z",  # Sprzedaż detaliczna pozostałych artykułów użytkowych
        "47.79.Z",  # Sprzedaż detaliczna artykułów używanych
        "47.82.Z",  # Sprzedaż detaliczna artykułów tekstylnych, odzieży i obuwia
        "47.89.Z",  # Sprzedaż detaliczna prowadzona na straganach i targowiskach
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://dane.biznes.gov.pl/api/ceidg/v2"
        self.session = requests.Session()
        
        # Rate limiting
        self.delay = 1.0  # seconds between requests
        self.last_request = 0
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make rate-limited request"""
        # Rate limit
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            self.last_request = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ Rate limited, waiting 30s...")
                time.sleep(30)
                return self._make_request(endpoint, params)
            else:
                print(f"❌ Error {response.status_code}: {response.text[:200]}")
                return {}
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {}
    
    def search_by_pkd(self, pkd_code: str, limit: int = 100) -> List[Company]:
        """
        Search companies by PKD code
        
        Args:
            pkd_code: PKD code (e.g., "47.91.Z")
            limit: Max results per request
        """
        companies = []
        page = 0
        
        # Normalize PKD code
        pkd_normalized = pkd_code.replace(".", "").replace("Z", "")
        
        print(f"🔍 Searching PKD {pkd_code}...")
        
        while len(companies) < limit:
            params = {
                "pkd": pkd_normalized,
                "page": page,
                "size": 25
            }
            
            data = self._make_request("firmy", params)
            
            if not data or "firma" not in data:
                break
            
            for item in data.get("firma", []):
                company = self._parse_company(item)
                if company:
                    companies.append(company)
            
            print(f"   Found {len(companies)} companies...")
            
            if len(data.get("firma", [])) < 25:
                break
            
            page += 1
            
            if len(companies) >= limit:
                break
        
        return companies[:limit]
    
    def _parse_company(self, data: Dict) -> Optional[Company]:
        """Parse company data from API response"""
        try:
            name = data.get("nazwa", "")
            nip = data.get("nip", "")
            regon = data.get("regon", "")
            
            # Get PKD info
            pkd_code = ""
            pkd_desc = ""
            for pkd in data.get("pkd", []):
                if pkd.get("glowny"):  # Main PKD
                    pkd_code = pkd.get("kod", "")
                    pkd_desc = pkd.get("nazwa", "")
                    break
            
            # Contact info (may be empty for privacy)
            email = data.get("email")
            phone = data.get("telefon")
            website = data.get("www")
            
            # Date
            start_date = None
            for date_info in data.get("dataRozpoczecia", []):
                start_date = date_info.get("data")
                break
            
            # Only return if has email or website (for marketing)
            if not email and not website:
                return None
            
            return Company(
                name=name,
                nip=nip,
                regon=regon,
                pkd_code=pkd_code,
                pkd_description=pkd_desc,
                email=email,
                phone=phone,
                website=website,
                start_date=start_date
            )
            
        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            return None
    
    def collect_ecommerce_companies(self, days_recent: int = 365, 
                                     min_results: int = 100) -> List[Company]:
        """
        Collect e-commerce companies registered recently
        
        Args:
            days_recent: Only companies registered within last N days
            min_results: Minimum number of results to collect
        """
        all_companies = []
        
        for pkd in self.ECOMMERCE_PKD:
            companies = self.search_by_pkd(pkd, limit=100)
            
            # Filter by registration date if possible
            cutoff_date = datetime.now() - timedelta(days=days_recent)
            
            for company in companies:
                if company.start_date:
                    try:
                        reg_date = datetime.strptime(company.start_date, "%Y-%m-%d")
                        if reg_date >= cutoff_date:
                            all_companies.append(company)
                    except:
                        all_companies.append(company)  # Include if date parse fails
                else:
                    all_companies.append(company)
            
            if len(all_companies) >= min_results:
                break
            
            time.sleep(2)  # Be nice to API
        
        # Deduplicate by NIP
        seen = set()
        unique = []
        for c in all_companies:
            if c.nip not in seen:
                seen.add(c.nip)
                unique.append(c)
        
        return unique
    
    def export_csv(self, companies: List[Company], filename: str = "jdg_ecommerce.csv"):
        """Export to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Name', 'NIP', 'REGON', 'PKD Code', 'PKD Description',
                'Email', 'Phone', 'Website', 'Start Date'
            ])
            
            for c in companies:
                writer.writerow([
                    c.name, c.nip, c.regon, c.pkd_code, c.pkd_description,
                    c.email or '', c.phone or '', c.website or '', c.start_date or ''
                ])
        
        print(f"✅ Exported {len(companies)} companies to {filename}")
    
    def validate_emails(self, companies: List[Company]) -> Dict[str, List[Company]]:
        """
        Basic email validation (syntax only)
        For SMTP validation, use external service
        """
        valid = []
        invalid = []
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for c in companies:
            if c.email and email_pattern.match(c.email):
                valid.append(c)
            else:
                invalid.append(c)
        
        return {"valid": valid, "invalid": invalid}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CEIDG E-commerce Company Scraper")
    parser.add_argument("--api-key", help="dane.biznes.gov.pl API key (optional)")
    parser.add_argument("--days", type=int, default=365, help="Recent registration days")
    parser.add_argument("--limit", type=int, default=100, help="Min companies to collect")
    parser.add_argument("--output", default="jdg_ecommerce.csv", help="Output CSV file")
    parser.add_argument("--validate", action="store_true", help="Validate emails")
    
    args = parser.parse_args()
    
    scraper = CEIDGScraper(api_key=args.api_key)
    
    print("🚀 Starting CEIDG e-commerce company collection...")
    print(f"   Looking for companies registered in last {args.days} days")
    print(f"   Target: minimum {args.limit} companies")
    
    companies = scraper.collect_ecommerce_companies(
        days_recent=args.days,
        min_results=args.limit
    )
    
    print(f"\n📊 Collected {len(companies)} unique companies")
    
    if args.validate:
        validation = scraper.validate_emails(companies)
        print(f"   Valid emails: {len(validation['valid'])}")
        print(f"   Invalid/missing: {len(validation['invalid'])}")
    
    # Summary by PKD
    pkd_counts = {}
    for c in companies:
        pkd_counts[c.pkd_code] = pkd_counts.get(c.pkd_code, 0) + 1
    
    print("\n📈 Top PKD codes:")
    for pkd, count in sorted(pkd_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"   {pkd}: {count}")
    
    scraper.export_csv(companies, args.output)


if __name__ == "__main__":
    main()
