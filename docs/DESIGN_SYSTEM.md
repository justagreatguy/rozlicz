# Rozlicz — Design System

## Brand Identity

### Nazwa
**Rozlicz** — krótko, zrozumiale, akcja-oriented ("rozlicz się z podatków")

### Logo Concept
- Minimalistyczny "R" z elementem faktury/dokumentu
- Lub: Abstract symbol rozliczenia (np. balans/znak równości)
- Style: Flat, modern, tech-forward

## Color Palette

### Primary Colors
| Nazwa | HEX | Użycie |
|-------|-----|--------|
| **Rozlicz Blue** | `#2563EB` | Primary actions, links, brand |
| **Rozlicz Dark** | `#1E293B` | Headers, text, dark mode bg |
| **Rozlicz Light** | `#F8FAFC` | Backgrounds, cards |

### Semantic Colors
| Nazwa | HEX | Użycie |
|-------|-----|--------|
| **Success** | `#10B981` | Success states, positive taxes |
| **Warning** | `#F59E0B` | Warnings, pending |
| **Error** | `#EF4444` | Errors, negative states |
| **Info** | `#3B82F6` | Info, neutral |

### Extended Palette
- **Gray Scale:** Slate palette (slate-50 do slate-950)
- **Accent:** Cyan `#06B6D4` dla highlights

## Typography

### Font Family
- **Primary:** Inter (Google Fonts)
- **Monospace:** JetBrains Mono (for numbers, codes)

### Scale
| Style | Size | Weight | Line Height |
|-------|------|--------|-------------|
| **H1** | 36px | 700 | 1.2 |
| **H2** | 30px | 600 | 1.3 |
| **H3** | 24px | 600 | 1.3 |
| **H4** | 20px | 500 | 1.4 |
| **Body** | 16px | 400 | 1.5 |
| **Small** | 14px | 400 | 1.5 |
| **Caption** | 12px | 400 | 1.4 |

## Components

### Buttons

**Primary Button**
- Background: Rozlicz Blue `#2563EB`
- Text: White
- Border radius: 8px
- Padding: 12px 24px
- Hover: Darken 10%

**Secondary Button**
- Background: White
- Border: 1px solid slate-300
- Text: Slate-700
- Hover: Slate-50 background

**Ghost Button**
- Background: Transparent
- Text: Rozlicz Blue
- Hover: Blue-50 background

### Cards
- Background: White
- Border radius: 12px
- Shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Padding: 24px

### Forms
- Input border: 1px solid slate-300
- Border radius: 8px
- Focus: Blue ring, border blue-500
- Label: 14px, slate-600, weight 500

### Data Display

**Tax Estimate Card**
- Large number: 32px, bold
- Label: 14px, slate-500
- Trend indicator: up/down arrow + %

**Invoice List Item**
- Compact, border-bottom separator
- Status badge (color-coded)
- Amount: monospace, right-aligned

## Key Screens

### 1. Landing Page

**Hero Section**
- Headline: "Automatyczna księgowość dla e-commerce"
- Subheadline: "400 zł netto. Bez limitu faktur. KSeF włączony."
- CTA: "Rozpocznij bezpłatnie" / "Zobacz jak to działa"
- Visual: Dashboard mockup or abstract illustration

**Social Proof**
- Logos: Allegro, Shopify, WooCommerce
- Testimonials (placeholder for now)

**Pricing Section**
- Single tier: 400 zł netto/miesiąc
- Features list with checkmarks
- CTA button

**FAQ Section**
- Collapsible questions
- Common concerns addressed

### 2. Dashboard

**Layout**
- Sidebar: Navigation (Dashboard, Documents, Taxes, Settings)
- Header: Search, notifications, profile
- Main content area

**Widgets**
- Tax estimate cards (PIT, VAT, ZUS)
- Recent documents list
- Upcoming deadlines
- Quick actions

### 3. KSeF Connection Flow

**Step 1: Welcome**
- Explanation of KSeF integration
- Benefits listed

**Step 2: Authorization**
- Two options: ePUAP or Certificate
- Clear instructions for each

**Step 3: Success**
- Confirmation of connection
- First sync status
- Next steps

### 4. Tax Estimates

**Real-time Display**
- Current month estimates
- Year-to-date summary
- Breakdown by category
- Comparison to previous period

## Responsive Breakpoints

| Breakpoint | Width | Target |
|------------|-------|--------|
| **Mobile** | < 640px | Phones |
| **Tablet** | 640-1024px | Tablets |
| **Desktop** | > 1024px | Laptops/Desktops |

## Dark Mode (Future)

- Background: Slate-900
- Cards: Slate-800
- Text: Slate-100
- Primary: Blue-400

---

*Version: 1.0*
*Last Updated: 2026-03-10*
