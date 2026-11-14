# luehr.dev

Static HTML website for Marc-Hendric Lühr. No browser framework or runtime dependencies.

## Edit and generate

`tools/build_site.py` contains the shared page layout, bilingual copy and training definitions.
`tools/existing-content.json` preserves the original training topics and source legal wording.
Edit those sources, then regenerate the tracked HTML and sitemap:

```sh
python3 tools/build_site.py
python3 tools/check_site.py
node tools/check_preferences.cjs
```

Python 3.10+ and Node.js 18+ are sufficient. No package installation is needed.
The generated HTML remains directly deployable. The GitHub Pages workflow regenerates,
validates and copies only public website files into its deployment artifact.

## Preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/de/` or `http://127.0.0.1:8765/`.

The general root entry follows the saved language or browser locale. Explicit German
and English content URLs are respected. Language links save the choice and pair the
same content. Without JavaScript, both language versions remain navigable.

Theme selection follows the operating system unless overridden. Preferences use local
storage when available; blocked storage does not prevent page use. CSS and script URLs
carry content hashes so a deployment does not mix old assets with new HTML.

## Fonts

IBM Plex Sans Regular and SemiBold, and IBM Plex Mono Regular are locally hosted WOFF2
files from the official IBM Plex repository. Copyright and SIL OFL 1.1 license are in
`assets/fonts/OFL.txt`. Existing Geist assets are retained but no longer referenced or deployed.

## Implementation notes

- Existing `/embedded-rust-training.html` and `/embedded-rust-schulung.html` URLs and
  their `#basics`, `#embedded-linux` and `#no-std` anchors remain available.
- All four trainings have German and English landing pages with self canonicals,
  reciprocal language alternates, breadcrumbs and Course structured data.
- Existing developer training pricing, travel inclusion and the exceptional remote
  format for no_std are preserved. The manager workshop lists the supplied prices
  plus VAT, without assuming a participant limit.
- Fonts, scripts and images are first-party assets. External GitHub statistics,
  icon scripts and the remote insurance badge have been replaced by ordinary links.
- English legal pages preserve the existing legal wording except for descriptions
  of changed storage and asset behavior. German translations are provided.

## Remaining review

The manager workshop prices are confirmed as €500 remote and €700 on-site, plus VAT.
Production Core Web Vitals and external search performance require measurements after deployment. Local checks do not establish
Google rich-result eligibility or search rankings.

## Phase 4 verification, 2026-11-14

- Manager workshop: €500 remote / €700 on-site, both plus VAT, in German and English
  summaries, facts and relevant FAQ answers.
- Blue palette in light and dark themes. Automated contrast checks cover text,
  secondary text, links and primary buttons on both page surfaces.
- All 16 pages checked in the browser at viewport widths 320, 390, 768 and 1440 px.
  No horizontal page overflow, missing images or extra/missing H1 headings remained.
- All 16 pages additionally checked in dark mode at 390 px. Theme persists on navigation.
- Keyboard checks: corresponding-language navigation, FAQ expansion and skip link.
  The skip link now moves focus into the main content.
- Unique titles and descriptions, social metadata, heading levels, image dimensions,
  canonicals, reciprocal language alternates, sitemap membership, eight localized
  Course entries and breadcrumb structure pass the static checker.
- Browser warning/error log was empty after final checks. Local generation and
  JavaScript preference tests pass; generated output is reproducible.
- Booking, three linked projects, blog and insurance link each returned HTTP 200.
  No booking form or email was submitted.
- The browser initially reused an old root-page cache entry. After reload, the current
  English home page passed the same viewport checks.
- Found and fixed: narrow-screen legal-heading overflow and skip-link focus behavior.

Performance scope: the client script is about 2.4 KB and CSS about 14 KB before
compression. Fonts and the portrait are local, with no third-party script or image
requests required for page rendering. This is an asset and implementation check,
not a Lighthouse score, production LCP/CLS/INP measurement or screen-reader audit.
Core Web Vitals field data and search indexing remain post-deployment checks.

## Content and character restored after review

The home pages retain all original service topics and all seven “Tools of the Trade”
categories, including hardware, interfaces, networking, security and testing details.
Coaching, consulting and implementation are explicit offers again. Content is kept in
`tools/existing-content.json` with localized German and English wording.

IPv6 Router Advertisement, Homeautomation and Curvyo each have their own equal project
article. Curvyo describes its vector-production use cases, platforms, Rust/Tauri stack
and Marc’s role in directing and reviewing agent-developed software.

The personal “Just Marc is perfectly fine” introduction, localized as “Marc reicht
völlig”, and the original five circular contact/profile buttons are restored. Icons
are inline SVG, with no CDN dependency. Two technical graphics illustrate developer
training paths and a schematic embedded board; the training path has a readable
stacked layout on smaller screens.

Both updated home pages pass checks at 320, 390, 768 and 1440 px, with additional
320/390 px checks in dark mode. The static checker now guards against accidentally
omitting service details, expertise categories, project articles or profile buttons.

Profile buttons now sit in the home-page header, above its divider line. Their visible circles are 36 px,
with 44 px click targets. The SWD/JTAG label sits to the right of its connector,
clear of the wiring. Go is listed second after Rust in both language versions;
Security & Integrity includes secure firmware / OTA updates.
