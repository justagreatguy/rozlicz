# Meta Marketing API Manager

## Setup

1. Create Facebook App at https://developers.facebook.com/apps/
   - Type: Business
   - Name: Rozlicz Marketing
   - Link to your BM

2. Add App to Business Portfolio
   - BM Settings → Apps → Add Apps

3. Create System User
   - BM Settings → System Users → Add
   - Name: Rozlicz Automation
   - Generate Token with permissions:
     - ads_management
     - ads_read
     - business_management

4. Add token to config.json

## Files

- `meta_api.py` — Core API client
- `campaign_manager.py` — Create/manage campaigns
- `analytics.py` — Reporting and metrics
- `config.json` — Settings and credentials
- `campaigns/` — Campaign definitions

## Usage

```bash
# Create campaign
python campaign_manager.py create --config campaigns/fake_door.json

# Get analytics
python analytics.py --campaign-id 123456 --days 7

# Pause campaign
python campaign_manager.py pause --campaign-id 123456
```
