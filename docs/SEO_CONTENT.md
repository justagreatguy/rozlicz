# SEO Content — Rozlicz.pl

Dokument zawierający metadane SEO dla strony głównej Rozlicz.pl.

---

## Meta Title

```
Rozlicz.pl — Księgowość dla E-commerce JDG | VAT UE, OSS/IOSS | 400 zł/mc
```

*Maks. 60 znaków: 67 znaków (zoptymalizowane dla branding + keywords)*

Alternatywny (krótszy):
```
Księgowość E-commerce JDG | VAT UE, Amazon, Allegro | Rozlicz.pl
```

---

## Meta Description

```
Profesjonalna księgowość dla przedsiębiorców e-commerce prowadzących JDG. VAT UE, OSS/IOSS, Amazon, Allegro, Shopify. Stała cena 400 zł netto/mc — bez ukrytych kosztów. Bezpłatna konsultacja.
```

*Maks. 160 znaków: 200 znaków (można skrócić)*

Skrócona wersja:
```
Księgowość dla e-commerce JDG. VAT UE, OSS/IOSS, Amazon, Allegro. Od 400 zł/mc. Specjalizacja w sprzedaży online.
```

---

## Keywords

### Primary Keywords (główne)
- księgowość e-commerce
- księgowość dla JDG
- biuro rachunkowe e-commerce
- VAT UE dla e-commerce
- księgowość Warszawa

### Secondary Keywords (wtórne)
- OSS IOSS Polska
- księgowość Amazon FBA
- księgowość Allegro
- rozliczenia Shopify Polska
- księgowość dla sprzedawców online
- JPK dla e-commerce
- rejestracja OSS
- VAT UE Amazon

### Long-tail Keywords
- biuro księgowe dla sprzedawców Allegro
- księgowość dla dropshippingu Polska
- rozliczenia VAT UE dla JDG
- księgowość WooCommerce Warszawa
- cennik księgowości e-commerce

---

## OpenGraph Tags (Facebook, LinkedIn, Slack)

```html
<!-- Podstawowe OG -->
<meta property="og:title" content="Rozlicz.pl — Księgowość dla E-commerce JDG">
<meta property="og:description" content="Profesjonalna księgowość dla przedsiębiorców e-commerce. VAT UE, OSS/IOSS, Amazon, Allegro. Stała cena 400 zł netto/mc.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://rozlicz.pl">
<meta property="og:site_name" content="Rozlicz.pl">
<meta property="og:locale" content="pl_PL">

<!-- Obraz OG (zalecane 1200x630px) -->
<meta property="og:image" content="https://rozlicz.pl/images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Rozlicz.pl - księgowość dla e-commerce">

<!-- Dodatkowe dla biznesu -->
<meta property="og:locale:alternate" content="en_US">
```

---

## Twitter Cards

```html
<!-- Twitter Card Summary Large Image -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Rozlicz.pl — Księgowość dla E-commerce JDG">
<meta name="twitter:description" content="Profesjonalna księgowość dla przedsiębiorców e-commerce. VAT UE, OSS/IOSS, Amazon, Allegro. 400 zł/mc.">
<meta name="twitter:image" content="https://rozlicz.pl/images/twitter-card.jpg">
<meta name="twitter:image:alt" content="Rozlicz.pl - księgowość dla e-commerce JDG">
<!-- <meta name="twitter:site" content="@rozliczpl"> -->
<!-- <meta name="twitter:creator" content="@rozliczpl"> -->
```

---

## JSON-LD Structured Data

### LocalBusiness + AccountingService

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://rozlicz.pl/#business",
      "name": "Rozlicz.pl",
      "alternateName": "Biuro Rachunkowe Rozlicz",
      "description": "Profesjonalna księgowość dla przedsiębiorców e-commerce prowadzących JDG. Specjalizacja w VAT UE, OSS/IOSS, Amazon, Allegro.",
      "url": "https://rozlicz.pl",
      "email": "kontakt@rozlicz.pl",
      "telephone": "+48-123-456-789",
      "priceRange": "400 PLN",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "ul. Przykładowa 1",
        "addressLocality": "Warszawa",
        "addressRegion": "mazowieckie",
        "postalCode": "00-001",
        "addressCountry": "PL"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 52.2297,
        "longitude": 21.0122
      },
      "areaServed": {
        "@type": "Country",
        "name": "Polska"
      },
      "serviceType": [
        "Księgowość dla JDG",
        "Obsługa VAT UE",
        "Rejestracja OSS/IOSS",
        "Rozliczenia e-commerce",
        "Prowadzenie KPiR",
        "Rozliczenia ryczałtowe"
      ],
      "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": [
          "Monday",
          "Tuesday",
          "Wednesday",
          "Thursday",
          "Friday"
        ],
        "opens": "08:00",
        "closes": "17:00"
      },
      "sameAs": []
    },
    {
      "@type": "Service",
      "@id": "https://rozlicz.pl/#service",
      "serviceType": "Księgowość dla e-commerce",
      "provider": {
        "@id": "https://rozlicz.pl/#business"
      },
      "areaServed": {
        "@type": "Country",
        "name": "Polska"
      },
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Usługi księgowe",
        "itemListElement": [
          {
            "@type": "Offer",
            "itemOffered": {
              "@type": "Service",
              "name": "Prowadzenie księgowości JDG e-commerce"
            },
            "price": "400.00",
            "priceCurrency": "PLN",
            "priceValidUntil": "2026-12-31",
            "availability": "https://schema.org/InStock",
            "url": "https://rozlicz.pl/cennik"
          }
        ]
      }
    },
    {
      "@type": "WebSite",
      "@id": "https://rozlicz.pl/#website",
      "url": "https://rozlicz.pl",
      "name": "Rozlicz.pl",
      "description": "Księgowość dla przedsiębiorców e-commerce",
      "publisher": {
        "@id": "https://rozlicz.pl/#business"
      },
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://rozlicz.pl/szukaj?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "WebPage",
      "@id": "https://rozlicz.pl/#webpage",
      "url": "https://rozlicz.pl",
      "name": "Księgowość dla E-commerce JDG | Rozlicz.pl",
      "isPartOf": {
        "@id": "https://rozlicz.pl/#website"
      },
      "about": {
        "@id": "https://rozlicz.pl/#business"
      },
      "primaryImageOfPage": {
        "@type": "ImageObject",
        "url": "https://rozlicz.pl/images/og-image.jpg"
      },
      "breadcrumb": {
        "@id": "https://rozlicz.pl/#breadcrumb"
      },
      "inLanguage": "pl-PL"
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://rozlicz.pl/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Strona główna",
          "item": "https://rozlicz.pl"
        }
      ]
    }
  ]
}
```

---

## FAQPage Schema (opcjonalnie — do sekcji FAQ)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Czy obsługujecie sprzedaż na Amazon/Allegro/Shopify?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tak — specjalizujemy się w e-commerce. Obsługujemy wszystkie główne platformy sprzedażowe, w tym rynki europejskie wymagające VAT UE."
      }
    },
    {
      "@type": "Question",
      "name": "Czy cena zależy od liczby transakcji?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Nie — 400 zł netto to stała miesięczna stawka, niezależna od sezonowych wzrostów czy spadków sprzedaży."
      }
    },
    {
      "@type": "Question",
      "name": "Czy obsługujecie podatek VAT UE i OSS/IOSS?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tak — to nasza specjalność. Prowadzimy rejestrację OSS/IOSS, składamy deklaracje VAT UE i dbamy o zgodność z regulacjami europejskimi."
      }
    },
    {
      "@type": "Question",
      "name": "Jak wygląda przekazanie dokumentów?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Możesz wysyłać faktury e-mailem, przez aplikację lub zdjęciem. Integrujemy się również z popularnymi systemami fakturowania i platformami sprzedażowymi."
      }
    }
  ]
}
```

---

## Canonical URL

```html
<link rel="canonical" href="https://rozlicz.pl/">
```

---

## Hreflang (jeśli będą wersje językowe)

```html
<link rel="alternate" hreflang="pl" href="https://rozlicz.pl/">
<link rel="alternate" hreflang="en" href="https://rozlicz.pl/en/">
<link rel="alternate" hreflang="x-default" href="https://rozlicz.pl/">
```

---

## Robots Meta

```html
<meta name="robots" content="index, follow">
<meta name="googlebot" content="index, follow">
```

---

## Dodatkowe tagi

```html
<meta name="author" content="Rozlicz.pl">
<meta name="copyright" content="Rozlicz.pl">
<meta name="language" content="Polish">
<meta name="revisit-after" content="7 days">
```

---

**Notatki implementacyjne:**
- Zastąp placeholder obrazów (`og-image.jpg`, `twitter-card.jpg`) rzeczywistymi grafikami (1200x630px)
- Zaktualizuj adres i telefon na rzeczywiste dane
- Dodaj linki do mediów społecznościowych w `sameAs`
- Przetestuj struktury danych w [Google Rich Results Test](https://search.google.com/test/rich-results)
