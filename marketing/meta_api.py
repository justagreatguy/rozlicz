#!/usr/bin/env python3
"""
Meta Marketing API Client
Handles authentication and base API requests
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class MetaAPIClient:
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, config_path: str = "config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.access_token = self.config["access_token"]
        self.ad_account_id = self.config["ad_account_id"]
        self.business_id = self.config.get("business_id")
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict:
        """Make authenticated request to Meta API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
        elif method == "DELETE":
            response = requests.delete(url, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        result = response.json()
        
        if "error" in result:
            raise MetaAPIError(result["error"])
        
        return result
    
    def get_account_info(self) -> Dict:
        """Get ad account information"""
        return self._make_request(
            self.ad_account_id,
            params={"fields": "name,currency,timezone_name,account_status,spend_cap"}
        )
    
    def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """List campaigns for ad account"""
        params = {
            "fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time"
        }
        if status:
            params["filtering"] = json.dumps([{"field": "status", "operator": "EQUAL", "value": status}])
        
        result = self._make_request(f"{self.ad_account_id}/campaigns", params=params)
        return result.get("data", [])
    
    def create_campaign(self, name: str, objective: str, daily_budget: int, 
                       status: str = "PAUSED") -> Dict:
        """
        Create a new campaign
        
        Args:
            name: Campaign name
            objective: OUTCOME_LEADS, OUTCOME_TRAFFIC, OUTCOME_SALES, etc.
            daily_budget: Budget in cents (e.g., 2000 = 20.00 PLN)
            status: ACTIVE or PAUSED
        """
        data = {
            "name": name,
            "objective": objective,
            "status": status,
            "daily_budget": daily_budget,
            "buying_type": "AUCTION",
            "special_ad_categories": []  # Add if targeting specific categories
        }
        
        return self._make_request(
            f"{self.ad_account_id}/campaigns",
            method="POST",
            data=data
        )
    
    def update_campaign(self, campaign_id: str, **kwargs) -> Dict:
        """Update campaign settings"""
        return self._make_request(
            campaign_id,
            method="POST",
            data=kwargs
        )
    
    def create_adset(self, campaign_id: str, name: str, targeting: Dict, 
                     daily_budget: int, optimization_goal: str = "LINK_CLICKS") -> Dict:
        """Create ad set within campaign"""
        data = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": daily_budget,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": optimization_goal,
            "targeting": targeting,
            "status": "PAUSED"
        }
        
        return self._make_request(
            f"{self.ad_account_id}/adsets",
            method="POST",
            data=data
        )
    
    def create_ad(self, adset_id: str, name: str, creative: Dict) -> Dict:
        """Create ad with creative"""
        data = {
            "name": name,
            "adset_id": adset_id,
            "creative": creative,
            "status": "PAUSED"
        }
        
        return self._make_request(
            f"{self.ad_account_id}/ads",
            method="POST",
            data=data
        )


class MetaAPIError(Exception):
    """Meta API Error"""
    def __init__(self, error_data: Dict):
        self.code = error_data.get("code")
        self.message = error_data.get("message", "Unknown error")
        self.type = error_data.get("type", "Unknown")
        super().__init__(f"[{self.type}] {self.code}: {self.message}")


if __name__ == "__main__":
    # Test connection
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python meta_api.py test")
        sys.exit(1)
    
    client = MetaAPIClient()
    
    if sys.argv[1] == "test":
        try:
            info = client.get_account_info()
            print(f"✅ Connected to: {info.get('name')}")
            print(f"   Currency: {info.get('currency')}")
            print(f"   Timezone: {info.get('timezone_name')}")
            print(f"   Status: {info.get('account_status')}")
        except MetaAPIError as e:
            print(f"❌ Error: {e}")
