# Form + Meta Pixel Setup

## 1. Formspree Setup (Email Collection)

Formspree is a free service for collecting form submissions (50/month free).

### Steps:
1. Go to https://formspree.io/
2. Sign up with your email
3. Create new form → Copy the endpoint URL (e.g., `https://formspree.io/f/xnqkvnop`)
4. Replace `YOUR_FORM_ID` in `index.html`:
   ```html
   action="https://formspree.io/f/xnqkvnop"
   ```

### Test the form:
- Submit a test email
- Check your Formspree dashboard
- You'll receive email notifications for each submission

## 2. Meta Pixel Setup

### Get Pixel ID:
1. Go to https://business.facebook.com/events_manager
2. Click "Add Data Source" → "Web"
3. Name: "Rozlicz.app"
4. Copy the Pixel ID (15-16 digits, e.g., `123456789012345`)

### Update index.html:
Replace `YOUR_PIXEL_ID` in TWO places:

```javascript
// In the script tag
fbq('init', '123456789012345');
```

```html
<!-- In the noscript tag -->
<img height="1" width="1" style="display:none" 
src="https://www.facebook.com/tr?id=123456789012345&ev=PageView&noscript=1"/>
```

## 3. Track Events in Meta Ads Manager

After setup, you'll see these events in Events Manager:

| Event | Trigger |
|-------|---------|
| `PageView` | Every page load |
| `Lead` | Form submission |
| `CTAClick` | Click on CTA buttons |

## 4. Testing

### Test Form:
1. Open rozlicz.app
2. Submit test email
3. Check Formspree dashboard
4. Check Meta Events Manager (events should appear within 15 minutes)

### Test Pixel:
1. Install Meta Pixel Helper Chrome extension
2. Open rozlicz.app
3. Verify pixel is firing (green icon)
4. Submit form → verify Lead event fires

## Files Modified

- `index.html` - Added pixel code, form handling, event tracking

## Next Steps

Once working:
1. Create Meta ad campaign with "Lead" optimization
2. Set up retargeting for visitors who didn't submit
3. A/B test different form copy

## Alternative: Telegram Notifications

If you prefer Telegram over email:
1. Create bot via @BotFather
2. Get bot token and chat ID
3. Replace Formspree endpoint with webhook URL
4. Contact me to set up Telegram integration
