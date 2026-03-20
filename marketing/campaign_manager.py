#!/usr/bin/env python3
"""
Campaign Manager for Rozlicz.app
Create and manage Facebook/Instagram ad campaigns
"""

import json
import argparse
from datetime import datetime
from meta_api import MetaAPIClient, MetaAPIError


class CampaignManager:
    """Manage Meta ad campaigns for Rozlicz.app"""
    
    # Targeting presets for Polish e-commerce JDG
    TARGETING_PRESETS = {
        "ecommerce_jdg": {
            "geo_locations": {
                "countries": ["PL"]
            },
            "age_min": 22,
            "age_max": 45,
            "interests": [
                {"id": 6003340414839, "name": "Online shopping"},
                {"id": 6003052207407, "name": "E-commerce"},
                {"id": 6003140615227, "name": "Allegro"}
            ],
            "behaviors": [
                {"id": 6071631541183, "name": "Small business owners"}
            ],
            "languages": ["pl"]
        },
        "allegro_sellers": {
            "geo_locations": {"countries": ["PL"]},
            "age_min": 25,
            "age_max": 50,
            "interests": [
                {"id": 6003140615227, "name": "Allegro"},
                {"id": 6003340414839, "name": "Online shopping"}
            ],
            "languages": ["pl"]
        },
        "shopify_pl": {
            "geo_locations": {"countries": ["PL"]},
            "age_min": 24,
            "age_max": 40,
            "interests": [
                {"id": 6003340414839, "name": "Online shopping"},
                {"id": 6002968507763, "name": "Shopify"}
            ],
            "languages": ["pl"]
        }
    }
    
    # Campaign objectives mapping
    OBJECTIVES = {
        "traffic": "OUTCOME_TRAFFIC",
        "leads": "OUTCOME_LEADS",
        "awareness": "OUTCOME_AWARENESS",
        "sales": "OUTCOME_SALES"
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.client = MetaAPIClient(config_path)
    
    def create_fake_door_campaign(self, name: str = None, budget_pln: float = 50.0,
                                   audience: str = "ecommerce_jdg"):
        """
        Create a fake door test campaign
        
        Args:
            name: Campaign name (auto-generated if None)
            budget_pln: Daily budget in PLN
            audience: Targeting preset name
        """
        if name is None:
            name = f"Rozlicz Fake Door {datetime.now().strftime('%Y-%m-%d')}"
        
        budget_cents = int(budget_pln * 100)  # Convert to cents
        
        print(f"🚀 Creating fake door campaign: {name}")
        print(f"   Budget: {budget_pln} PLN/day")
        print(f"   Audience: {audience}")
        
        # Create campaign
        try:
            campaign = self.client.create_campaign(
                name=name,
                objective=self.OBJECTIVES["traffic"],
                daily_budget=budget_cents,
                status="PAUSED"  # Start paused for review
            )
            print(f"✅ Campaign created: {campaign.get('id')}")
            
            # Create ad set
            adset = self._create_adset(
                campaign_id=campaign["id"],
                name=f"{name} - AdSet",
                audience_preset=audience,
                budget_cents=budget_cents
            )
            print(f"✅ AdSet created: {adset.get('id')}")
            
            return {
                "campaign_id": campaign["id"],
                "adset_id": adset["id"],
                "name": name,
                "budget_pln": budget_pln,
                "audience": audience
            }
            
        except MetaAPIError as e:
            print(f"❌ Error: {e}")
            return None
    
    def _create_adset(self, campaign_id: str, name: str, audience_preset: str, 
                      budget_cents: int):
        """Create ad set with targeting"""
        targeting = self.TARGETING_PRESETS.get(audience_preset, self.TARGETING_PRESETS["ecommerce_jdg"])
        
        return self.client.create_adset(
            campaign_id=campaign_id,
            name=name,
            targeting=targeting,
            daily_budget=budget_cents,
            optimization_goal="LINK_CLICKS"
        )
    
    def create_ad_creative(self, headline: str, body: str, link: str = "https://rozlicz.app"):
        """Create ad creative (simplified)"""
        # Full implementation requires page access and asset uploads
        # This is a template for the creative structure
        return {
            "object_story_spec": {
                "page_id": self.client.config.get("page_id"),
                "link_data": {
                    "message": body,
                    "link": link,
                    "name": headline,
                    "description": "Automatyczna księgowość dla e-commerce"
                }
            }
        }
    
    def list_campaigns(self, status: str = None):
        """List all campaigns"""
        campaigns = self.client.get_campaigns(status=status)
        
        print(f"\n📊 Campaigns ({len(campaigns)} total):")
        print("-" * 80)
        
        for camp in campaigns:
            status_icon = "🟢" if camp.get("status") == "ACTIVE" else "⚫"
            print(f"{status_icon} {camp.get('name')[:40]:<40} | {camp.get('status'):<10} | {camp.get('id')}")
        
        return campaigns
    
    def pause_campaign(self, campaign_id: str):
        """Pause a campaign"""
        try:
            result = self.client.update_campaign(campaign_id, status="PAUSED")
            print(f"⏸️ Campaign paused: {campaign_id}")
            return result
        except MetaAPIError as e:
            print(f"❌ Error: {e}")
            return None
    
    def activate_campaign(self, campaign_id: str):
        """Activate a campaign"""
        try:
            result = self.client.update_campaign(campaign_id, status="ACTIVE")
            print(f"▶️ Campaign activated: {campaign_id}")
            return result
        except MetaAPIError as e:
            print(f"❌ Error: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Rozlicz Meta Campaign Manager")
    parser.add_argument("action", choices=["create", "list", "pause", "activate"])
    parser.add_argument("--name", help="Campaign name")
    parser.add_argument("--budget", type=float, default=50.0, help="Daily budget in PLN")
    parser.add_argument("--audience", default="ecommerce_jdg", 
                       choices=["ecommerce_jdg", "allegro_sellers", "shopify_pl"],
                       help="Target audience preset")
    parser.add_argument("--campaign-id", help="Campaign ID for pause/activate")
    
    args = parser.parse_args()
    
    manager = CampaignManager()
    
    if args.action == "create":
        result = manager.create_fake_door_campaign(
            name=args.name,
            budget_pln=args.budget,
            audience=args.audience
        )
        if result:
            print(f"\n📋 Campaign Summary:")
            print(json.dumps(result, indent=2))
    
    elif args.action == "list":
        manager.list_campaigns()
    
    elif args.action == "pause":
        if not args.campaign_id:
            print("❌ --campaign-id required")
            return
        manager.pause_campaign(args.campaign_id)
    
    elif args.action == "activate":
        if not args.campaign_id:
            print("❌ --campaign-id required")
            return
        manager.activate_campaign(args.campaign_id)


if __name__ == "__main__":
    main()
