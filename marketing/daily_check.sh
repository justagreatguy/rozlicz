#!/bin/bash
# Daily Meta Ads optimization script

# Change to script directory
cd "$(dirname "$0")"

# Generate daily report
python3 analytics.py --days 1 > reports/daily_$(date +%Y%m%d).txt

# Auto-pause underperforming campaigns (CTR < 0.5% after 3 days)
# Add logic here when ready

echo "✅ Meta ads daily check completed: $(date)"
