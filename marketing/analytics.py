#!/usr/bin/env python3
"""
Analytics and Reporting for Meta Campaigns
"""

import json
import argparse
from datetime import datetime, timedelta
from meta_api import MetaAPIClient, MetaAPIError


class MetaAnalytics:
    """Generate reports for Meta ad campaigns"""
    
    def __init__(self, config_path: str = "config.json"):
        self.client = MetaAPIClient(config_path)
    
    def get_campaign_insights(self, campaign_id: str, days: int = 7):
        """Get insights for a specific campaign"""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "fields": "campaign_name,impressions,clicks,spend,ctr,cpc,actions,cost_per_action_type",
            "time_range": json.dumps({"since": since, "until": until}),
            "time_increment": 1
        }
        
        result = self.client._make_request(
            f"{campaign_id}/insights",
            params=params
        )
        
        return result.get("data", [])
    
    def get_account_insights(self, days: int = 7):
        """Get insights for entire ad account"""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "fields": "campaign_name,impressions,clicks,spend,ctr,cpc,actions",
            "time_range": json.dumps({"since": since, "until": until})
        }
        
        result = self.client._make_request(
            f"{self.client.ad_account_id}/insights",
            params=params
        )
        
        return result.get("data", [])
    
    def generate_report(self, days: int = 7):
        """Generate formatted report"""
        insights = self.get_account_insights(days=days)
        
        if not insights:
            print("📊 No data available for the selected period")
            return
        
        # Aggregate data
        total_spend = sum(float(d.get("spend", 0)) for d in insights)
        total_impressions = sum(int(d.get("impressions", 0)) for d in insights)
        total_clicks = sum(int(d.get("clicks", 0)) for d in insights)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        
        # Get campaign list
        campaigns = self.client.get_campaigns()
        campaign_status = {c["id"]: c["status"] for c in campaigns}
        
        # Print report
        print(f"\n📈 ROZLICZ.APP META ADS REPORT")
        print(f"Period: Last {days} days ({datetime.now().strftime('%Y-%m-%d')})")
        print("=" * 60)
        
        print(f"\n💰 SPEND: {total_spend:.2f} PLN")
        print(f"👁️  IMPRESSIONS: {total_impressions:,}")
        print(f"🖱️  CLICKS: {total_clicks:,}")
        print(f"📊 CTR: {avg_ctr:.2f}%")
        print(f"💵 CPC: {avg_cpc:.2f} PLN")
        
        print(f"\n📋 CAMPAIGNS:")
        print("-" * 60)
        
        for insight in insights[:10]:  # Top 10
            camp_name = insight.get("campaign_name", "Unknown")[:35]
            camp_spend = float(insight.get("spend", 0))
            camp_clicks = int(insight.get("clicks", 0))
            camp_impr = int(insight.get("impressions", 1))
            camp_ctr = camp_clicks / camp_impr * 100
            
            status = "🟢" if campaign_status.get(insight.get("campaign_id")) == "ACTIVE" else "⚫"
            
            print(f"{status} {camp_name:<35} | {camp_spend:>7.2f} PLN | {camp_ctr:>5.2f}% CTR")
        
        return {
            "total_spend": total_spend,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "ctr": avg_ctr,
            "cpc": avg_cpc
        }
    
    def export_csv(self, days: int = 30, output: str = "meta_report.csv"):
        """Export data to CSV"""
        insights = self.get_account_insights(days=days)
        
        import csv
        
        with open(output, 'w', newline='') as f:
            if insights:
                writer = csv.DictWriter(f, fieldnames=insights[0].keys())
                writer.writeheader()
                writer.writerows(insights)
        
        print(f"✅ Report exported to {output}")


def main():
    parser = argparse.ArgumentParser(description="Rozlicz Meta Analytics")
    parser.add_argument("--days", type=int, default=7, help="Number of days to report")
    parser.add_argument("--export", help="Export to CSV file")
    parser.add_argument("--campaign-id", help="Get insights for specific campaign")
    
    args = parser.parse_args()
    
    analytics = MetaAnalytics()
    
    if args.export:
        analytics.export_csv(days=args.days, output=args.export)
    elif args.campaign_id:
        insights = analytics.get_campaign_insights(args.campaign_id, days=args.days)
        print(json.dumps(insights, indent=2))
    else:
        analytics.generate_report(days=args.days)


if __name__ == "__main__":
    main()
