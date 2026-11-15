"""Render the static website with Python's standard library: python3 tools/build_site.py."""
from pathlib import Path
from html import escape, unescape
import json
import hashlib
import re

ROOT = Path(__file__).resolve().parent.parent
CONTENT = json.loads((ROOT / 'tools/existing-content.json').read_text())
PROJECTS = json.loads((ROOT / 'tools/projects.json').read_text())
BASE = 'https://luehr.dev'
BOOK = 'https://zeeg.me/marcluehr/getting-to-know'
NAME = 'Marc-Hendric Lühr'
PAGES = []

def version(asset):
    return hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:10]


def tr(lang, de, en):
    return de if lang == 'de' else en


COURSES = [
    dict(key='basics', paths={'de':'/rust-basics-schulung.html','en':'/rust-basics-training.html'},
         title={'de':'Rust Basics','en':'Rust Basics'},
         summary={'de':'Rust von Grund auf lernen und in einem zusammenhängenden Programm anwenden. Mit Ownership, Fehlerbehandlung, Tests und Cross-Compilation.', 'en':'Learn Rust from the ground up and apply it in a coherent program. Cover ownership, error handling, testing and cross-compilation.'},
         audience={'de':'Entwickler mit Grundkenntnissen einer Programmiersprache. C ist ideal; C++, Go oder Python sind ebenfalls ein guter Ausgangspunkt.', 'en':'Developers with basic knowledge of a programming language. C is ideal; C++, Go or Python are good starting points too.'},
         short={'de':'Für Entwickler, die mit Rust beginnen.', 'en':'For developers getting started with Rust.'},
         topics={'de':'Ownership · Traits · Testing · Cross-Compilation','en':'Ownership · Traits · Testing · Cross-compilation'},
         approach={'de':'Wir entwickeln gemeinsam ein kleines Spiel. Erst kommt die Aufgabe, dann das passende Sprachkonzept. Du arbeitest allein, im kleinen Team oder mit der ganzen Gruppe. Nach Absprache können wir stattdessen ein erstes produktives Programm aus eurem Arbeitsgebiet entwickeln.', 'en':'We develop a small game together. Each problem introduces the next language concept. You work individually, in small teams or as a group. By arrangement, we can build a first productive program from your domain instead.'}),
    dict(key='embedded-linux', paths={'de':'/rust-embedded-linux-schulung.html','en':'/rust-embedded-linux-training.html'},
         title={'de':'Rust Advanced: Embedded Linux','en':'Rust Advanced: Embedded Linux'},
         summary={'de':'Rust für Anwendungen und Dienste auf Embedded Linux. Nebenläufigkeit, D-Bus und Web-APIs, mit Tests und einer abgesicherten Build- und Release-Pipeline.', 'en':'Rust for applications and services on Embedded Linux. Concurrency, D-Bus and web APIs, with testing and a secured build and release pipeline.'},
         audience={'de':'Entwicklerteams, die Rust für Anwendungen und Dienste auf Linux-Geräten einsetzen möchten.', 'en':'Development teams using Rust for applications and services on Linux devices.'},
         short={'de':'Für Teams mit Anwendungen auf Linux-Geräten.','en':'For teams building applications on Linux devices.'},
         topics={'de':'Async Rust · D-Bus · axum · CI/CD','en':'Async Rust · D-Bus · axum · CI/CD'},
         approach={'de':'Viel selbst programmieren, technische Hintergründe dort besprechen, wo sie gebraucht werden. Das Übungsprogramm aus Rust Basics wächst um die neuen Themen. Die passenden Vorkenntnisse und Schwerpunkte klären wir im Vorgespräch.', 'en':'Plenty of coding, with technical explanations where they are needed. The exercise program from Rust Basics grows with each new topic. We discuss prior knowledge and suitable topics before the training.'}),
    dict(key='no-std', paths={'de':'/rust-no-std-schulung.html','en':'/rust-no-std-training.html'},
         title={'de':'Rust Advanced: Embedded no_std','en':'Rust Advanced: Embedded no_std'},
         summary={'de':'Rust direkt auf dem Mikrocontroller, ohne Standardbibliothek. Mit Embassy, Embedded-Traits, begrenztem Speicher und Hardware-Debugging.', 'en':'Rust directly on the microcontroller, without the standard library. Work with Embassy, embedded traits, constrained memory and hardware debugging.'},
         audience={'de':'Firmware- und Embedded-Entwickler, die Rust auf Mikrocontrollern einsetzen möchten.', 'en':'Firmware and embedded developers who want to use Rust on microcontrollers.'},
         short={'de':'Für Teams, die Firmware auf Mikrocontrollern entwickeln.','en':'For teams developing microcontroller firmware.'},
         topics={'de':'Embassy · embedded-hal · heapless · SWD/JTAG','en':'Embassy · embedded-hal · heapless · SWD/JTAG'},
         approach={'de':'Wir programmieren auf genau einer Plattform: STM32, nRF52 oder ESP32. Eure eigene Hardware kann ebenfalls behandelt werden. Das Übungsprogramm wird schrittweise um die Embedded-Themen erweitert. Plattform und Vorkenntnisse stimmen wir vorher ab.', 'en':'We work on one platform: STM32, nRF52 or ESP32. Your own custom hardware can be covered as well. The exercise program grows step by step with embedded topics. We agree on the platform and prior knowledge beforehand.'}),
    dict(key='managers', paths={'de':'/rust-fuer-engineering-manager.html','en':'/rust-for-engineering-managers.html'},
         title={'de':'Rust für Engineering Manager','en':'Rust for Engineering Managers'},
         summary={'de':'Chancen, Risiken und wirtschaftlichen Nutzen einer Rust-Einführung bewerten. Ein praktischer Einstieg in Kosten, technische Grenzen und mögliche Migrationswege.', 'en':'A practical introduction to the opportunities, costs and trade-offs of adopting Rust. Evaluate technical constraints and realistic migration strategies.'},
         audience={'de':'Engineering Manager, CTOs, technische Geschäftsführer, Software- und Firmware-Teamleiter, technische Projektleiter und Architekten mit Technologieverantwortung.', 'en':'Engineering managers, CTOs, technical directors, software and firmware team leads, technical project managers and architects responsible for technology decisions.'},
         short={'de':'Für technische Entscheider, die Rust evaluieren.','en':'For technical leaders evaluating Rust adoption.'},
         topics={'de':'Rust vs. C/C++ · Einführung · Migration · Entscheidung','en':'Rust vs. C/C++ · Adoption · Migration · Decision criteria'},
         approach={'de':'Wir betrachten Rust aus praktischer Embedded-Engineering-Perspektive. Technische Zusammenhänge werden verständlich erklärt, ohne unnötig tief in Syntax oder Implementierungsdetails einzusteigen. Ziel ist eine informierte Entscheidung, einschließlich der Frage, wann Rust sich nicht lohnt.', 'en':'We look at Rust from a practical embedded engineering perspective. Technical concepts are explained without going unnecessarily deep into syntax or implementation details. The goal is an informed decision, including when Rust is not worth adopting.'})
]
MANAGER_TOPICS = {
'de': [('Warum Rust?','Welche Probleme Rust bei Memory Safety, Nebenläufigkeit und Softwarezuverlässigkeit adressiert.'),('Rust und C/C++','Technische Unterschiede, Einschränkungen und Auswirkungen auf bestehende Embedded-Projekte.'),('Wirtschaftlicher Nutzen','Bestimmte Fehlerklassen reduzieren, Wartbarkeit verbessern und langfristige Softwarequalität beurteilen.'),('Hürden der Einführung','Lernkurve, Produktivität, Recruiting, Tooling, Bibliotheken und Integration in bestehende Codebasen.'),('Migrationsstrategien','Pilotprojekte, schrittweise Einführung, C/C++-Interoperabilität und realistische Einstiegspunkte.'),('Eine Entscheidung treffen','Kriterien dafür, wann Rust sinnvoll ist und wann der Aufwand den Nutzen übersteigt.')],
'en': [('Why Rust?','The problems Rust addresses in memory safety, concurrency and software reliability.'),('Rust vs. C/C++','Technical differences, constraints and their impact on existing embedded projects.'),('Business value','Reducing specific classes of bugs, improving maintainability and assessing long-term software quality.'),('Adoption challenges','Learning curve, productivity, recruiting, tooling, libraries and integration with existing codebases.'),('Migration strategies','Pilot projects, incremental adoption, C/C++ interoperability and realistic starting points.'),('Making the decision','Criteria for when Rust makes sense and when the effort outweighs the benefit.')]
}


def home(lang):
    return '/de/' if lang == 'de' else '/'


def overview(lang):
    return '/embedded-rust-schulung.html' if lang == 'de' else '/embedded-rust-training.html'


def link(url, label, cls=''):
    return f'<a class="{cls}" href="{escape(url, quote=True)}">{escape(label)}</a>'


def header(lang, paths):
    profiles=f'<div class="header-profiles">{social_links(lang)}</div>' if paths[lang]==home(lang) else ''
    sections = [('training','Trainings','Training'),('engineering','Engineering','Engineering'),('about','Über mich','About'),('contact','Kontakt','Contact')]
    nav = ''.join(link(home(lang)+'#'+key, tr(lang,de,en)) for key,de,en in sections)
    languages = ''.join(f'<a href="{paths[code]}" lang="{code}" hreflang="{code}" data-language="{code}"'+ (' aria-current="page"' if code==lang else '')+f'>{label}</a>' for code,label in [('de','Deutsch'),('en','English')])
    return f'''<a class="skip-link" href="#main">{tr(lang,'Zum Inhalt','Skip to content')}</a>
<header class="site-header wrap"><a class="wordmark" href="{home(lang)}">Marc-Hendric Lühr<span>Embedded engineering &amp; training</span></a>
<nav aria-label="{tr(lang,'Hauptnavigation','Main navigation')}">{nav}</nav>
<div class="preferences"><nav class="language-switch" aria-label="{tr(lang,'Sprache','Language')}">{languages}</nav><button id="theme-toggle" type="button" aria-label="{tr(lang,'Farbschema wechseln','Change color theme')}" aria-pressed="false"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg></button></div>{profiles}</header>'''


def footer(lang):
    return f'''<footer class="site-footer wrap"><div><strong>{NAME}</strong><p>{tr(lang,'Remote in Europa · Vor Ort nach Absprache','Remote across Europe · On-site by arrangement')}</p></div><nav aria-label="{tr(lang,'Weitere Links','Further links')}">{link('/impressum.html' if lang=='de' else '/imprint.html',tr(lang,'Impressum','Imprint'))}{link('/datenschutz.html' if lang=='de' else '/privacy.html',tr(lang,'Datenschutz','Privacy'))}{link('https://github.com/Th3Link','GitHub')}{link('https://linkedin.com/in/marcluehr','LinkedIn')}{link('https://blog.luehr.dev/','Blog')}{link('https://www.exali.de/siegel/Marc-Hendric-Luehr_1025',tr(lang,'Berufshaftpflicht','Professional liability insurance'))}</nav><small>© {NAME} · IBM Plex · <a href="/assets/fonts/OFL.txt">SIL Open Font License</a></small></footer>'''


def render(lang, paths, title, description, body, schema=(), auto=False):
    path=paths[lang]
    alternates=''.join(f'<link rel="alternate" hreflang="{code}" href="{BASE+url}">' for code,url in paths.items())
    graph=[{'@type':'Person','@id':BASE+'/#person','name':NAME,'url':BASE+'/','image':BASE+'/avatar.jpg','jobTitle':'Embedded Engineer & Trainer','sameAs':['https://github.com/Th3Link','https://linkedin.com/in/marcluehr']},{'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':'luehr.dev','inLanguage':['de','en']}]+list(schema)
    structured_data=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')
    page=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{BASE+path}">{alternates}<link rel="alternate" hreflang="x-default" href="{BASE+paths['en']}">
<meta property="og:type" content="website"><meta property="og:site_name" content="luehr.dev"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE}/avatar.jpg"><meta property="og:image:alt" content="{NAME}"><meta property="og:locale" content="{tr(lang,'de_DE','en_GB')}"><meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/fonts/IBMPlexSans-Regular.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/style.css?v={version('style.css')}"><script src="/theme.js?v={version('theme.js')}"></script>
<script type="application/ld+json">{structured_data}</script></head>
<body data-auto-language="{str(auto).lower()}">{header(lang,paths)}<main id="main" tabindex="-1">{body}</main>{footer(lang)}</body></html>'''
    target=ROOT / ('index.html' if path=='/' else path.lstrip('/')+('index.html' if path.endswith('/') else ''))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n'.join(line.rstrip() for line in page.replace('><', '>\n<').splitlines())+'\n')
    PAGES.append((path,paths))


def actions(lang, managers=False):
    subject=tr(lang,'Anfrage Rust Adoption Workshop' if managers else 'Anfrage Rust Teamtraining','Rust adoption workshop inquiry' if managers else 'Rust team training inquiry')
    primary=link('mailto:marc@luehr.dev?subject='+subject.replace(' ','%20'),tr(lang,'Workshop besprechen' if managers else 'Training anfragen','Discuss a Rust Adoption Workshop' if managers else 'Discuss your team’s training'),'button')
    secondary=link(overview(lang),tr(lang,'Technische Rust-Trainings ansehen','Explore Technical Rust Trainings'),'text-link') if managers else link(BOOK,tr(lang,'Erstgespräch buchen','Book an intro call'),'text-link')
    return f'<div class="actions">{primary}{secondary}</div>'


def facts(c, lang):
    key=c['key']; rows=[]
    if key=='managers':
        rows=[(tr(lang,'Dauer','Duration'),tr(lang,'½ Tag · ungefähr 4 Stunden','½ day · approximately 4 hours')),('Remote',tr(lang,'500 € zzgl. MwSt.','€500 plus VAT')),(tr(lang,'Vor Ort','On-site'),tr(lang,'700 € zzgl. MwSt.','€700 plus VAT')),(tr(lang,'Ort','Location'),tr(lang,'In der näheren Umgebung, nach geografischer Abstimmung.','In the nearby area, subject to agreement on location.'))]
    else:
        remote=tr(lang,'3–4 Tage','3–4 days') if key=='basics' else tr(lang,'3 Tage','3 days')
        if key=='no-std': remote=tr(lang,'Nur in Ausnahmefällen: ','Only in exceptional cases: ')+remote
        rows=[('Remote',remote+' · '+tr(lang,'12.000 € zzgl. MwSt.','€12,000 plus VAT')),(tr(lang,'Vor Ort','On-site'),tr(lang,'4 Tage, Dienstag bis Freitagmittag · 15.000 € zzgl. MwSt., inklusive Reisekosten','4 days, Tuesday to Friday noon · €15,000 plus VAT, travel included')),(tr(lang,'Teilnehmer','Participants'),tr(lang,'5–10 · Festpreis für das Team','5–10 · fixed price for the team'))]
    if key=='no-std':
        rows[0],rows[1]=rows[1],rows[0]
    rows.append((tr(lang,'Sprache','Language'),tr(lang,'Deutsch oder Englisch','English or German')))
    return '<dl class="facts">'+''.join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k,v in rows)+'</dl>'


def training_rows(lang):
    rows=[]
    for i,c in enumerate(COURSES):
        price=tr(lang,'½ Tag · 500 € remote / 700 € vor Ort, zzgl. MwSt.','½ day · €500 remote / €700 on-site, plus VAT') if c['key']=='managers' else (tr(lang,'4 Tage vor Ort · 15.000 € zzgl. MwSt.','4 days on-site · €15,000 plus VAT') if c['key']=='no-std' else tr(lang,'3–4 Tage · ab 12.000 € zzgl. MwSt.','3–4 days · from €12,000 plus VAT'))
        note=tr(lang,'Remote nur in Ausnahmefällen.','Remote only in exceptional cases.') if c['key']=='no-std' else tr(lang,'Vor Ort nach geografischer Abstimmung.','On-site subject to agreement on location.') if c['key']=='managers' else tr(lang,'Remote oder vor Ort · 5–10 Teilnehmer','Remote or on-site · 5–10 participants')
        rows.append(f'''<article class="training-row" id="{c['key']}"><span class="course-number">0{i+1}</span><div><p class="eyebrow">{c['short'][lang]}</p><h3>{link(c['paths'][lang],c['title'][lang])}</h3><p>{c['summary'][lang]}</p><p class="topic-line">{c['topics'][lang]}</p></div><div class="course-meta"><strong>{price}</strong><p>{note}</p>{link(c['paths'][lang],tr(lang,'Zum Training','Explore this training')+' →','text-link')}</div></article>''')
    return ''.join(rows)


def training_comparison(lang):
    starting_points = [
        tr(lang, 'Grundkenntnisse einer Programmiersprache; Rust ist neu für euch.', 'Basic knowledge of a programming language; you are new to Rust.'),
        tr(lang, 'Rust Basics oder entsprechende Kenntnisse; Anwendungen auf Linux sind euer Ziel.', 'Rust Basics or equivalent knowledge; your target is Linux applications.'),
        tr(lang, 'Rust Basics oder entsprechende Kenntnisse; ihr entwickelt Mikrocontroller-Firmware.', 'Rust Basics or equivalent knowledge; you develop microcontroller firmware.'),
        tr(lang, 'Technologieverantwortung und technisches Interesse; kein Programmierkurs.', 'Technology responsibility and technical interest; this is not a programming course.'),
    ]
    goals = [
        tr(lang, 'Ein eigenes Rust-Programm entwickeln: Ownership, Fehlerbehandlung, Tests und Cross-Compilation praktisch anwenden.', 'Build a Rust program: apply ownership, error handling, testing and cross-compilation.'),
        tr(lang, 'Linux-Anwendungen und Dienste entwickeln: Nebenläufigkeit, D-Bus, Web-APIs und Build-/Release-Pipeline.', 'Develop Linux applications and services: concurrency, D-Bus, web APIs and a build/release pipeline.'),
        tr(lang, 'Ohne Standardbibliothek auf Hardware arbeiten: Embassy, Embedded-Traits, Speicher und Debugging.', 'Work on hardware without the standard library: Embassy, embedded traits, memory and debugging.'),
        tr(lang, 'Rust-Einführung beurteilen: Nutzen, Aufwand, Grenzen und schrittweise Migration mit C/C++.', 'Assess Rust adoption: benefits, effort, constraints and incremental migration with C/C++.'),
    ]
    rows = []
    for course, start, goal in zip(COURSES, starting_points, goals):
        rows.append(f'<tr><th scope="row">{link(course["paths"][lang], course["title"][lang])}</th><td>{escape(start)}</td><td>{escape(goal)}</td><td>{facts(course, lang)}</td></tr>')
    headings = [tr(lang, 'Training', 'Training'), tr(lang, 'Euer Ausgangspunkt', 'Your starting point'), tr(lang, 'Woran wir arbeiten', 'What we work on'), tr(lang, 'Format & Preis', 'Format & pricing')]
    return f'''<section id="vergleich" class="section wrap comparison"><div class="section-heading"><p class="eyebrow">{tr(lang,'Trainingsvergleich','Training comparison')}</p><h2>{tr(lang,'Welcher Einstieg passt zu euch?','Where should your team start?')}</h2><p>{tr(lang,'Neu in Rust? Beginnt mit Basics. Danach entscheidet eure Zielplattform: Linux-Anwendung oder Mikrocontroller. Wer zunächst die Einführung bewerten möchte, wählt den Manager-Workshop.','New to Rust? Start with Basics. Your target platform then determines the next step: Linux applications or microcontrollers. Choose the managers workshop to evaluate adoption first.')}</p></div>{training_graphic(lang)}<p id="comparison-help" class="comparison-help">{tr(lang,'Auf kleinen Bildschirmen könnt ihr die Tabelle seitlich scrollen. Alle Preise zuzüglich MwSt.','On small screens, scroll the table sideways. All prices exclude VAT.')}</p><div class="comparison-scroll" role="region" aria-labelledby="comparison-caption" aria-describedby="comparison-help" tabindex="0"><table><caption id="comparison-caption">{tr(lang,'Die vier Rust-Angebote im direkten Vergleich','Compare the four Rust offerings')}</caption><thead><tr>{''.join(f'<th scope="col">{h}</th>' for h in headings)}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><p>{tr(lang,'Bei den Entwicklertrainings gilt der Festpreis für ein Team mit 5–10 Teilnehmern. Bei Vor-Ort-Terminen sind die Reisekosten enthalten. Plattform, Vorkenntnisse und mögliche Anpassungen klären wir im Vorgespräch.','Developer training has a fixed price for a team of 5–10 participants. On-site developer training includes travel. We discuss the platform, prior knowledge and possible adjustments before the training.')}</p>{link('#contact', tr(lang,'Noch unsicher? Lasst uns das gemeinsam klären.','Still unsure? Let’s work it out together.'), 'text-link')}</section>'''


def contact(lang, managers=False):
    booking = link(BOOK,tr(lang,'Erstgespräch buchen','Book an intro call'),'text-link') if managers else ''
    return f'''<section id="contact" class="contact-band"><div class="wrap contact-layout"><div><p class="eyebrow">{tr(lang,'Kontakt','Contact')}</p><h2>{tr(lang,'Bewerten wir eure Rust-Einführung.' if managers else 'Planen wir euer Rust-Training.','Let’s discuss Rust adoption.' if managers else 'Let’s plan your team’s Rust training.')}</h2><p>{tr(lang,'Welche Vorkenntnisse bringt ihr mit, und woran arbeitet ihr? Schreib mir oder vereinbare ein Erstgespräch.','What does your team already know, and what are you building? Send me an email or book an introductory call.')}</p></div><div>{actions(lang, managers)}{booking}<a class="email" href="mailto:marc@luehr.dev">marc@luehr.dev</a></div></div></section>'''


def home_contact(lang):
    project = link('mailto:marc@luehr.dev?subject='+tr(lang,'Anfrage%20Embedded-Projekt','Embedded%20project%20inquiry'), tr(lang,'Projekt besprechen','Discuss your project'), 'button')
    training = link(overview(lang), tr(lang,'Trainings ansehen','Explore training'), 'button')
    return f'''<section id="contact" class="contact-band"><div class="wrap contact-layout"><div><p class="eyebrow">{tr(lang,'Kontakt','Contact')}</p><h2>{tr(lang,'Woran arbeitet ihr gerade?','What are you working on?')}</h2><p>{tr(lang,'Ihr sucht Unterstützung für ein Embedded-Projekt oder möchtet Rust im Team lernen? Erzählt mir, worum es geht. Dann besprechen wir, wie ich euch unterstützen kann.','Need support for an embedded project or want to learn Rust as a team? Tell me what you are working on, and we can discuss how I can help.')}</p></div><div><div class="actions">{project}{training}</div><p>{link(BOOK,tr(lang,'Erstgespräch buchen','Book an intro call'),'text-link')}</p><a class="email" href="mailto:marc@luehr.dev">marc@luehr.dev</a></div></div></section>'''


def social_links(lang):
    links=CONTENT['social_links']
    if lang=='de': links=links.replace('aria-label="Email"','aria-label="E-Mail"')
    return f'<nav class="social-links" aria-label="{tr(lang,"Kontakt und Profile","Contact and profiles")}">{links}</nav>'


def training_graphic(lang):
    return f'''<figure class="technical-graphic training-graphic"><svg viewBox="0 0 520 206" role="img" aria-labelledby="training-path-title"><title id="training-path-title">{tr(lang,'Die Entwicklertrainings: Rust Basics als Grundlage, danach Embedded Linux oder no_std.','Developer training paths: Rust Basics as the foundation, followed by Embedded Linux or no_std.')}</title><g class="diagram-wire"><path d="M164 94h55V47h44M219 94v53h44"/><circle cx="219" cy="94" r="4"/></g><g class="diagram-block"><rect x="2" y="60" width="162" height="68" rx="5"/><rect x="265" y="14" width="253" height="68" rx="5"/><rect x="265" y="116" width="253" height="68" rx="5"/></g><g class="diagram-label"><text x="20" y="89">Rust Basics</text><text x="20" y="110" class="diagram-small">Ownership / Traits</text><text x="283" y="43">Embedded Linux</text><text x="283" y="65" class="diagram-small">std / Async / Services</text><text x="283" y="145">Embedded no_std</text><text x="283" y="167" class="diagram-small">Embassy / HAL / Debugging</text></g></svg><div class="training-map-mobile"><div class="training-node"><strong>Rust Basics</strong><span>Ownership / Traits</span></div><div class="training-branches"><div class="training-node"><strong>Embedded Linux</strong><span>std / Async / Services</span></div><div class="training-node"><strong>Embedded no_std</strong><span>Embassy / HAL / Debugging</span></div></div></div></figure>'''


def hardware_graphic(lang):
    return f'''<figure class="technical-graphic hardware-graphic"><svg viewBox="0 0 420 270" role="img" aria-labelledby="hardware-title"><title id="hardware-title">{tr(lang,'Schematische Embedded-Platine mit Prozessor, Firmware, Speicher und Schnittstellen.','Schematic embedded board with a processor, firmware, memory and interfaces.')}</title><rect class="diagram-board" x="24" y="24" width="372" height="222" rx="10"/><g class="diagram-wire"><path d="M168 104H91V67M168 117H64v70h38M232 104h47V67M232 117h116v70h-34M181 84V49m14 35V49m14 35V49m14 35V49M181 150v58m14-58v58m14-58v58m14-58v58"/><circle cx="91" cy="67" r="5"/><circle cx="279" cy="67" r="5"/><circle cx="48" cy="44" r="4"/><circle cx="372" cy="44" r="4"/><circle cx="48" cy="226" r="4"/><circle cx="372" cy="226" r="4"/></g><g class="diagram-block"><rect x="155" y="84" width="90" height="68" rx="3"/><rect x="102" y="171" width="48" height="30" rx="2"/><rect x="265" y="171" width="48" height="30" rx="2"/></g><g class="diagram-label"><text x="171" y="111">CPU</text><text x="171" y="133" class="diagram-small">Firmware</text><text x="109" y="191" class="diagram-small">I²C</text><text x="273" y="191" class="diagram-small">CAN</text><text x="105" y="72" class="diagram-small">SWD / JTAG</text><text x="290" y="63" class="diagram-small">{tr(lang,'Speicher','Memory')}</text><text x="70" y="231" class="diagram-small">{tr(lang,'Von der Hardware zur Software.','From hardware to software.')}</text></g></svg></figure>'''


def engineering_sections(lang):
    services=[]
    for index,item in enumerate(CONTENT['services']):
        items=''.join(f'<li>{escape(text)}</li>' for text in item['items'][lang])
        training_link=link(overview(lang),tr(lang,'Embedded-Rust-Trainings im Detail','Embedded Rust training details')+' →','text-link') if index==1 else ''
        services.append(f'<article><h3>{escape(item["title"][lang])}</h3><p>{escape(item["description"][lang])}</p><ul>{items}</ul>{training_link}</article>')
    expertise=[]
    for item in CONTENT['expertise']:
        items=''.join(f'<li>{escape(text)}</li>' for text in item['items'][lang])
        expertise.append(f'<article><h3>{escape(item["title"][lang])}</h3><ul>{items}</ul></article>')
    return f'''<section id="engineering" class="section wrap"><div class="engineering-intro"><div class="section-heading"><p class="eyebrow">02 / Freelance Engineering</p><h2>{tr(lang,'Mitarbeit an eurem Embedded-Projekt.','Hands-on support for your embedded project.')}</h2><p>{tr(lang,'Ich biete freiberufliche Mitarbeit an Embedded-Systemen: Architektur und Implementierung, Linux-Integration, Firmware, Tests und sichere Updates. Dazu kommen Beratung, Reviews und Coaching – passend zu der Aufgabe, die ihr lösen wollt.','I offer freelance work on embedded systems: architecture and implementation, Linux integration, firmware, testing and secure updates. Consulting, reviews and coaching can complement the work, depending on the problem you need to solve.')}</p></div>{hardware_graphic(lang)}</div><div class="services-grid">{''.join(services)}</div><div class="engineering-note"><p>{tr(lang,'Nicht jedes Problem passt in eine Kategorie. Manchmal ist es am sinnvollsten, sich zusammenzusetzen, gemeinsam hinzuschauen und pragmatisch weiterzuarbeiten.','Not every problem fits neatly into a category. Sometimes the best solution is simply to sit down, look at it together, and move forward pragmatically.')}</p><p>{tr(lang,'Ob eine klar abgegrenzte Aufgabe oder die Mitarbeit an einer bestehenden Codebasis: Wir besprechen Ziel, Umfang und Zusammenarbeit vorab. Projektarbeit biete ich remote und nach Absprache vor Ort an, insbesondere in Nord- und Mitteldeutschland.','Whether you need help with a defined task or an existing codebase, we discuss goals, scope and how to work together first. I offer remote project work and on-site collaboration by arrangement, particularly in Northern and Central Germany.')}</p>{link('#contact',tr(lang,'Über euer Projekt sprechen','Discuss your project'),'text-link')}</div></section>''', f'''<section id="expertise" class="section tinted"><div class="wrap"><div class="section-heading"><p class="eyebrow">{tr(lang,'Technologien & Fachgebiete','Technologies & domains')}</p><h2>Tools of the Trade</h2><p>{tr(lang,'Technologien sollten dem Produkt dienen. Moderne Embedded-Systeme brauchen einen Blick über einzelne Technologien hinaus. Meine Arbeit verbindet Linux, Firmware, Netzwerktechnik, Tests, Security und die Werkzeuge dazwischen. Mit diesen Technologien und Fachgebieten arbeite ich regelmäßig.','Technology choices should serve the product, not the other way around. Building modern embedded systems requires looking beyond individual technologies. My work regularly spans Linux, firmware, networking, testing, security and the tooling that connects them. These are some of the technologies and domains I work with on a regular basis.')}</p></div><div class="expertise-grid">{''.join(expertise)}</div></div></section>'''


def make_home(lang):
    paths={'en':'/','de':'/de/'}
    title=tr(lang,'Freelance Embedded Engineering & Rust-Trainings | Marc-Hendric Lühr','Freelance Embedded Engineering & Rust Training | Marc-Hendric Lühr')
    description=tr(lang,'Freiberufliches Embedded Engineering mit Marc-Hendric Lühr: Embedded Linux, Yocto, Rust und Firmware. Dazu praxisnahe Rust-Trainings für Entwicklerteams.','Freelance embedded engineering with Marc-Hendric Lühr: Embedded Linux, Yocto, Rust and firmware. Plus hands-on Rust training for engineering teams.')
    hero=f'''<section class="hero wrap"><div><p class="eyebrow">{tr(lang,'Freiberuflicher Embedded Engineer und Trainer','Freelance embedded engineer and trainer')}</p><h1>{tr(lang,'Embedded-Systeme entwickeln.<br>Wissen weitergeben.','Build embedded systems.<br>Share the knowledge.')}</h1><p class="intro">{tr(lang,'Embedded Engineering und Rust-Trainings. Ich unterstütze euch bei Embedded Linux, Yocto und Firmware – von Architektur und Implementierung bis zu Tests und langfristiger Wartung.','Embedded engineering and Rust training. I support your work on Embedded Linux, Yocto and firmware, from architecture and implementation to testing and long-term maintenance.')}</p><p>{tr(lang,'Ich bin Marc. Ihr könnt mich für die Mitarbeit an eurem Projekt oder für ein Training dazuholen. In beiden Fällen geht es darum, gemeinsam weiterzukommen und Wissen im Team zu verankern.','I’m Marc. Bring me in to work on your project or train your team. Both are about making progress together and helping the team build its own understanding.')}</p><div class="actions">{link('#contact',tr(lang,'Projekt besprechen','Discuss your project'),'button')}{link('#training',tr(lang,'Trainings ansehen','Explore training'),'button')}</div></div><figure class="portrait"><picture><source type="image/webp" srcset="/assets/images/marc-luehr-192.webp 192w, /assets/images/marc-luehr-320.webp 320w, /assets/images/marc-luehr-480.webp 480w, /assets/images/marc-luehr-720.webp 720w" sizes="(max-width: 700px) 88px, (max-width: 1050px) 200px, 240px"><img src="/avatar.jpg" width="1192" height="1299" alt="{tr(lang,'Marc-Hendric Lühr, Embedded Engineer und Trainer','Marc-Hendric Lühr, embedded engineer and trainer')}" fetchpriority="high"></picture><figcaption><strong>Marc-Hendric Lühr</strong><span class="personal-note">{tr(lang,'Marc reicht völlig.','Just Marc is perfectly fine.')}</span><span>{tr(lang,'Embedded Linux · Rust · Firmware','Embedded Linux · Rust · Firmware')}</span></figcaption></figure></section>'''
    training=f'''<section id="training" class="section wrap"><div class="section-heading"><p class="eyebrow">01 / {tr(lang,'Trainings','Training')}</p><h2>{tr(lang,'Das passende Training für euer Team.','Find the right training for your team.')}</h2><p>{tr(lang,'Drei Entwicklertrainings und ein Workshop für technische Entscheider. Auf Deutsch oder Englisch. Termine vereinbaren wir individuell.','Three developer trainings and a workshop for technical leaders. In English or German. Dates are arranged individually.')}</p></div>{training_rows(lang)}<p>{link(overview(lang)+"#vergleich",tr(lang,"Trainings direkt vergleichen →","Compare trainings side by side →"),"text-link")}</p></section>'''
    approach=f'''<section class="section tinted"><div class="wrap two-column"><div><p class="eyebrow">03 / {tr(lang,'Im Training','In training')}</p><h2>{tr(lang,'Selbst programmieren.<br>Zusammen verstehen.','Write the code.<br>Understand the decisions.')}</h2><p>{tr(lang,'Im Entwicklertraining lösen wir konkrete Aufgaben. Sprachkonzepte und technische Hintergründe kommen dann dazu, wenn sie gebraucht werden.','In developer training, we solve concrete problems. Language concepts and technical explanations follow when they are needed.')}</p></div><div class="prose">{training_graphic(lang)}<h3>{tr(lang,'Ein Programm, das mitwächst','A program that grows with you')}</h3><p>{tr(lang,'In Rust Basics entwickeln wir ein kleines Spiel und erweitern es mit jedem Thema. Die Advanced-Trainings bauen darauf auf. Nach Absprache ist in Basics auch ein erstes Programm aus eurem Arbeitsgebiet möglich.','In Rust Basics, we build a small game and extend it with each topic. The advanced trainings build on it. By arrangement, Basics can use a first program from your domain instead.')}</p><h3>{tr(lang,'Mit Blick auf euren Alltag','Connected to your work')}</h3><p>{tr(lang,'Cross-Compilation, Tests, Debugging und CI/CD gehören dazu. Themen und Technologien stimmen wir vorher ab. Mein Ziel ist, dass ihr danach selbstständig weiterarbeiten könnt.','Cross-compilation, tests, debugging and CI/CD are part of the work. We agree on topics and technologies beforehand. My goal is to help your team continue independently.')}</p><p>{tr(lang,'Ihr wollt Rust zunächst bewerten? Der Manager-Workshop behandelt Einführung, Aufwand und Entscheidungskriterien.','Want to evaluate Rust first? The managers workshop covers adoption, effort and decision criteria.')}</p>{link(COURSES[3]['paths'][lang],tr(lang,'Zum Workshop für Engineering Manager','Explore the engineering managers workshop'),'text-link')}</div></div></section>'''
    engineering,expertise=engineering_sections(lang)
    about=f'''<section id="about" class="section wrap"><div class="two-column"><div><p class="eyebrow">04 / {tr(lang,'Über mich','About')}</p><h2>{tr(lang,'Ich arbeite selbst<br>an diesen Themen.','I work on these<br>problems myself.')}</h2></div><div class="prose"><p>{tr(lang,'Ich nutze Open Source seit Beginn meiner beruflichen Laufbahn und bevorzuge offene Technologien, wo es sinnvoll ist. In eigenen Projekten verbinde ich Rust-Netzwerkbibliotheken, Hardware und Software zu vollständigen Systemen. Dabei probiere ich Ideen aus, überprüfe Ansätze und bleibe selbst nah an der praktischen Entwicklung.','I’ve relied on open source software throughout my entire career and strongly prefer open technologies whenever practical. My personal projects range from Rust networking libraries to complete hardware and software systems. They let me explore ideas, validate approaches and stay connected to hands-on engineering.')}</p><p>{tr(lang,'Technologien ändern sich. Gute Engineering-Praxis und Teams, die selbstständig weiterarbeiten können, bleiben wertvoll.','Technologies change. Sound engineering practices and teams that can work independently remain valuable.')}</p></div></div><div class="projects"><article id="ipv6-router-advertisement"><span class="eyebrow">Rust / Networking</span><h3>{link('https://github.com/Th3Link/ipv6-router-advertisement','IPv6 Router Advertisement')}</h3><p>{tr(lang,'Rust-Implementierung für IPv6 Router Advertisements. Mit Fokus auf Codequalität, Tests, Wartbarkeit und Embedded-Anwendungsfälle.','A Rust implementation for IPv6 Router Advertisement handling, developed with a focus on code quality, testing, maintainability and embedded use cases.')}</p></article><article id="homeautomation"><span class="eyebrow">Hardware / Firmware / Linux</span><h3>{link('https://github.com/Th3Link/homeautomation','Homeautomation')}</h3><p>{tr(lang,'Eine offene Hausautomationsplattform mit eigener Hardware, Embedded-Software und Systemintegration. In realen Umgebungen entwickelt und betrieben, mit Fokus auf skalierbarem Embedded-Design, langfristiger Wartbarkeit und kosteneffizientem Betrieb.','An open home automation platform combining custom hardware, embedded software and system integration. Developed and operated in real-world environments, the project demonstrates scalable embedded design, long-term maintainability and cost-efficient deployment.')}</p></article><article id="curvyo"><span class="eyebrow">Rust / Tauri / {tr(lang,'Vektorwerkzeuge','Vector tools')}</span><h3>{link('https://github.com/curvyo/curvyo','Curvyo')}</h3><p>{tr(lang,'Ein Vektorwerkzeug mit Rust und Tauri in früher Entwicklung. Zeichnen und Bearbeiten sind möglich; die Ausgabe für Lasercutter, Plotter, Stickmaschinen und CNC-Fräsen ist noch geplant. Desktop zuerst, Browser und mobile Begleiter später.','A vector tool built with Rust and Tauri, in early development. Drawing and editing are available; output for laser cutters, plotters, embroidery machines and CNC mills is still planned. Desktop first, with browser and mobile companions later.')}</p><p>{tr(lang,'Vollständig von KI-Agenten entwickelt, mit mir als Auftraggeber und technischer Leitung: Richtung vorgeben, technische Entscheidungen treffen, präzise spezifizieren, Reviews durchführen, testen und Fehler melden. Spezifikationsgetrieben, mit einer durchgängigen CI/CD-Pipeline.','Developed entirely by AI agents, with me as customer and technical lead: setting the direction, making technical decisions, specifying precisely, reviewing, testing and reporting bugs. Spec-driven, with CI/CD done properly.')}</p></article></div><p class="personal-statement">{tr(lang,'Ich berate nicht nur zu Embedded-Systemen. Ich entwickle und betreibe sie selbst.','I don’t just advise teams on embedded systems. I build and operate them myself.')}</p></section>'''
    for project in PROJECTS:
        marker = f'<article id="{project["key"]}">'
        start = about.index(marker)
        end = about.index('</article>', start)
        about = about[:end] + '<p>'+link(project_paths(project)[lang], tr(lang,'Projekteinblick lesen →','Read the case study →'),'text-link')+'</p>' + about[end:]
    render(lang,paths,title,description,hero+training+engineering+approach+expertise+about+home_contact(lang),auto=True)


def breadcrumbs(lang, c=None):
    items=[{'@type':'ListItem','position':1,'name':tr(lang,'Startseite','Home'),'item':BASE+home(lang)},{'@type':'ListItem','position':2,'name':tr(lang,'Trainings','Training'),'item':BASE+overview(lang)}]
    if c: items.append({'@type':'ListItem','position':3,'name':c['title'][lang],'item':BASE+c['paths'][lang]})
    return {'@type':'BreadcrumbList','itemListElement':items}


def project_paths(project):
    return {'de': f'/de/projekte/{project["key"]}/', 'en': f'/projects/{project["key"]}/'}


def make_project(project, lang):
    copy = project[lang]
    paths = project_paths(project)
    steps = ''.join(f'<li><strong>{escape(title)}</strong><span>{escape(note)}</span></li>' for title, note in copy['diagram'])
    sections = ''.join(f'<section><h2>{escape(title)}</h2><p>{escape(text)}</p></section>' for title, text in copy['sections'])
    related = ''.join(link(c['paths'][lang], c['title'][lang]+' →') for c in COURSES if c['key'] in project['courses'])
    sources = [(project['repo'], tr(lang, 'Quellcode & README', 'Source code & README'))]
    if project['key'] == 'ipv6-router-advertisement':
        sources += [('https://docs.rs/ipv6-router-advertisement', tr(lang, 'API-Dokumentation', 'API documentation'))]
    elif project['key'] == 'curvyo':
        sources += [('https://curvyo.org', 'curvyo.org')]
    source_links = ''.join(f'<li>{link(url, label)}</li>' for url, label in sources)
    trail = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': tr(lang, 'Startseite', 'Home'), 'item': BASE+home(lang)},
        {'@type': 'ListItem', 'position': 2, 'name': project['name'], 'item': BASE+paths[lang]},
    ]}
    article = {'@type': 'TechArticle', 'headline': copy['title'], 'description': copy['summary'], 'url': BASE+paths[lang], 'mainEntityOfPage': BASE+paths[lang], 'inLanguage': lang, 'author': {'@id': BASE+'/#person'}, 'citation': [url for url, _ in sources], 'dateModified': '2026-11-15'}
    body = f'''<section class="course-hero wrap"><nav class="breadcrumbs" aria-label="{tr(lang,'Brotkrumennavigation','Breadcrumbs')}">{link(home(lang),tr(lang,'Startseite','Home'))}<span>/</span>{link(home(lang)+'#about',tr(lang,'Eigene Projekte','Personal projects'))}</nav><p class="eyebrow">{tr(lang,'Projekteinblick','Project case study')} / {project['name']}</p><h1>{escape(copy['title'])}</h1><p class="intro">{escape(copy['summary'])}</p><p class="project-date">{tr(lang,'Projektstand geprüft am 15. November 2026','Project status checked on 15 November 2026')}</p></section><figure class="wrap project-flow"><figcaption>{tr(lang,'Der Ansatz im Überblick','The approach at a glance')}</figcaption><ol>{steps}</ol></figure><div class="wrap course-layout"><aside class="course-facts"><h2>{tr(lang,'Auf einen Blick','At a glance')}</h2><dl class="facts"><div><dt>{tr(lang,'Meine Rolle','My role')}</dt><dd>{escape(copy['role'])}</dd></div><div><dt>Stack</dt><dd>{escape(project['stack'])}</dd></div><div><dt>{tr(lang,'Stand','Status')}</dt><dd>{escape(copy['status'])}</dd></div></dl>{link(project['repo'],tr(lang,'Repository ansehen →','View repository →'),'text-link')}</aside><div class="course-content">{sections}<section><h2>{tr(lang,'Quellen & Projektstand','Sources & project status')}</h2><p>{tr(lang,'Die Beschreibung folgt dem öffentlich dokumentierten Projektstand zum oben genannten Datum. Den aktuellen Stand findet ihr im Repository.','This description follows the publicly documented project status on the date above. See the repository for the current status.')}</p><ul>{source_links}</ul></section><section><h2>{tr(lang,'Passende Trainings','Related training')}</h2><nav class="related" aria-label="{tr(lang,'Passende Trainings','Related training')}">{related}</nav></section><section><h2>{tr(lang,'Weitere eigene Projekte','More personal projects')}</h2><nav class="related" aria-label="{tr(lang,'Weitere Projekte','More projects')}">{''.join(link(project_paths(p)[lang],p['name']+' →') for p in PROJECTS if p!=project)}</nav></section></div></div>'''
    render(lang, paths, copy['title']+' | '+NAME, copy['summary'], body, [trail, article])


def make_course(c,lang):
    manager=c['key']=='managers'
    seo_names={
        'basics':tr(lang,'Rust Basics Schulung','Rust Basics Training'),
        'embedded-linux':tr(lang,'Rust Embedded Linux Schulung','Rust Embedded Linux Training'),
        'no-std':tr(lang,'Embedded Rust no_std Schulung','Embedded Rust no_std Training'),
        'managers':c['title'][lang],
    }
    title=seo_names[c['key']]+' | '+NAME
    prereq=tr(lang,'Technisches Interesse und Verantwortung für Technologieentscheidungen. Der Workshop ist eine verständliche Einführung und kein Programmierkurs.','Technical interest and responsibility for technology decisions. This workshop is an accessible introduction, rather than a programming course.') if manager else c['audience'][lang] if c['key']=='basics' else tr(lang,'Als Advanced-Training baut dieses Angebot auf Rust Basics auf. Welche Kenntnisse euer Team bereits mitbringt und welche Vorbereitung passt, klären wir im Vorgespräch.','As an advanced training, this course builds on Rust Basics. We discuss your team’s existing knowledge and suitable preparation before the training.')
    topics='<div class="curriculum">'+''.join(f'<article><h3>{escape(k)}</h3><p>{escape(v)}</p></article>' for k,v in MANAGER_TOPICS[lang])+'</div>' if manager else '<ul class="topic-list">'+''.join(f'<li>{escape(unescape(t))}</li>' for t in CONTENT['topics'][lang][c['key']])+'</ul>'
    qa=[(tr(lang,'Für wen ist der Workshop gedacht?','Who is the workshop for?'),c['audience'][lang]),(tr(lang,'Geht es um eine vollständige Migration?','Does this mean a complete migration?'),tr(lang,'Nein. Wir betrachten auch Pilotprojekte, schrittweise Einführung und die Interoperabilität mit C/C++.','No. We also look at pilot projects, incremental adoption and interoperability with C/C++.')),(tr(lang,'Wo kann der Workshop vor Ort stattfinden?','Where is the on-site workshop available?'),tr(lang,'In der näheren Umgebung, nach geografischer Abstimmung. Der Preis beträgt 700 € zzgl. MwSt.','In the nearby area, subject to agreement on location. The price is €700 plus VAT.'))] if manager else [(tr(lang,'Kann das Training angepasst werden?','Can the training be adapted?'),tr(lang,'Themen- und Technologiewünsche sind nach vorheriger Absprache möglich. Je nach Vorkenntnissen behandeln wir einzelne Themen kürzer oder vertiefen bestimmte Fragen.','Topic and technology requests are possible by prior agreement. Depending on prior knowledge, we spend less time on some topics and explore specific questions in depth.')),(tr(lang,'Wann findet das Training statt?','When does the training take place?'),tr(lang,'Termine vereinbaren wir individuell mit eurem Team.','Dates are arranged individually with your team.')),(tr(lang,'Gilt der Preis pro Person?','Is the price per person?'),tr(lang,'Nein. Es ist ein Festpreis für das Team mit 5–10 Teilnehmern, jeweils zuzüglich MwSt. Bei den Vor-Ort-Entwicklertrainings sind die Reisekosten enthalten.','No. It is a fixed price for a team of 5–10 participants, plus VAT. Travel is included in the on-site developer training price.'))]
    faq=''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in qa)
    related=''.join(link(x['paths'][lang],x['title'][lang]+' →') for x in COURSES if x!=c)
    body=f'''<section class="course-hero wrap"><nav class="breadcrumbs" aria-label="{tr(lang,'Brotkrumennavigation','Breadcrumbs')}">{link(home(lang),tr(lang,'Startseite','Home'))}<span>/</span>{link(overview(lang),tr(lang,'Trainings','Training'))}</nav><p class="eyebrow">{c['short'][lang]}</p><h1>{c['title'][lang]}</h1><p class="intro">{c['summary'][lang]}</p>{actions(lang,manager)}</section><section class="wrap course-layout"><aside class="course-facts"><h2>{tr(lang,'Auf einen Blick','At a glance')}</h2>{facts(c,lang)}</aside><div class="course-content"><section><h2>{tr(lang,'Für wen?','Who is it for?')}</h2><p>{c['audience'][lang]}</p><h3>{tr(lang,'Vorkenntnisse','Prior knowledge')}</h3><p>{prereq}</p></section><section><h2>{tr(lang,'Was wir behandeln','What we cover')}</h2>{topics}</section><section><h2>{tr(lang,'So arbeiten wir','How we work')}</h2><p>{c['approach'][lang]}</p></section><section><h2>{tr(lang,'Dein Trainer','Your trainer')}</h2><p>{tr(lang,'Ich bin Marc-Hendric Lühr, Embedded Engineer und Trainer. Meine Arbeit verbindet Embedded Linux, Firmwarearchitektur, Tests und Rust.','I’m Marc-Hendric Lühr, an embedded engineer and trainer. My work connects Embedded Linux, firmware architecture, testing and Rust.')}</p>{link(home(lang)+'#about',tr(lang,'Mehr über mich und meine Projekte','About me and my projects'),'text-link')}</section><section class="faq"><h2>{tr(lang,'Häufige Fragen','Frequently asked questions')}</h2>{faq}</section><section><h2>{tr(lang,'Weitere Trainings','Related training')}</h2><nav class="related" aria-label="{tr(lang,'Weitere Trainings','Related training')}">{related}</nav></section></div></section>{contact(lang,manager)}'''
    schema={'@type':'Course','name':c['title'][lang],'description':c['summary'][lang],'url':BASE+c['paths'][lang],'inLanguage':lang,'provider':{'@id':BASE+'/#person'}}
    render(lang,c['paths'],title,c['summary'][lang],body,[breadcrumbs(lang,c),schema])


def make_overview(lang):
    paths={l:overview(l) for l in ['de','en']}
    body=f'''<section class="course-hero wrap"><p class="eyebrow">{NAME}</p><h1>{tr(lang,'Embedded Rust Schulungen für Teams','Embedded Rust training for teams')}</h1><p class="intro">{tr(lang,'Vom Einstieg bis zu Linux und Mikrocontroller-Firmware. Dazu ein eigener Workshop für technische Entscheider.','From the fundamentals to Linux applications and microcontroller firmware. Plus a dedicated workshop for technical leaders.')}</p>{actions(lang)}<p>{link("#vergleich",tr(lang,"Zum Trainingsvergleich ↓","Compare trainings ↓"),"text-link")}</p></section>{training_comparison(lang)}<section class="wrap section overview-training"><h2>{tr(lang,'Vier Trainings, unterschiedliche Aufgaben','Four trainings, different goals')}</h2>{training_rows(lang)}</section>{contact(lang)}'''
    render(lang,paths,tr(lang,'Embedded Rust Schulung | Alle Trainings | Marc-Hendric Lühr','Embedded Rust Training | All Courses | Marc-Hendric Lühr'),tr(lang,'Rust Basics, Embedded Linux, no_std und ein Workshop für Engineering Manager. Alle Trainings mit Dauer, Preisen und Inhalten.','Rust Basics, Embedded Linux, no_std and a workshop for engineering managers. Compare training content, duration and pricing.'),body,[breadcrumbs(lang)])


def make_legal():
    for kind in ['imprint','privacy']:
        paths={'en':'/'+kind+'.html','de':'/'+('impressum' if kind=='imprint' else 'datenschutz')+'.html'}
        for lang in ['en','de']:
            title=tr(lang,'Impressum' if kind=='imprint' else 'Datenschutz','Imprint' if kind=='imprint' else 'Privacy policy')
            body=CONTENT['legal'][kind]
            if kind=='privacy':
                body=body.replace('your theme preference (light or dark mode)','your theme preference (light or dark mode) and language selection (German or English)')
                body=re.sub(r'<h3>GitHub Statistics</h3>.*?(?=<h3>Scheduling)', '<h3>Locally hosted resources</h3><p>Fonts, scripts and images are served by this website. GitHub statistics and external icon scripts are no longer embedded.</p>\n',body,flags=re.S)
                body=re.sub(r'<h3>Liability Insurance Seal.*?(?=<h3>Your Rights)', '<h3>Professional liability insurance</h3><p>This website links to the insurance information at exali AG. No insurance seal is loaded from an external server. Following the link takes you to exali’s website.</p>',body,flags=re.S)
            body=body.replace('<h3>', '<h2>').replace('</h3>', '</h2>')
            if lang=='de':
                body=LEGAL_DE[kind]
            description=tr(lang,'Impressum, Kontaktdaten und Angaben zum Betreiber von luehr.dev, Marc-Hendric Lühr.','Imprint, contact details and website operator information for Marc-Hendric Lühr at luehr.dev.') if kind=='imprint' else tr(lang,'Datenschutzhinweise zu luehr.dev: lokale Spracheinstellungen, Hosting, E-Mail-Kontakt und Terminvereinbarung.','Privacy information for luehr.dev: local language preferences, hosting, email contact and appointment scheduling.')
            render(lang,paths,title+' | '+NAME,description,f'<article class="legal wrap"><h1>{title}</h1>{body}</article>')


LEGAL_DE = {
'imprint':'''<p>Angaben gemäß §5 TMG</p><p>Marc-Hendric Lühr<br>Alte Dorfstr. 22A<br>31832 Springe<br>Deutschland</p><p>E-Mail: <a href="mailto:marc@luehr.dev">marc@luehr.dev</a></p><h2>Verantwortlich für den Inhalt gemäß §55 Abs. 2 RStV</h2><p>Marc-Hendric Lühr<br>Alte Dorfstr. 22A<br>31832 Springe</p><h2>Haftung für Inhalte</h2><p>Die Inhalte dieser Website wurden mit großer Sorgfalt erstellt. Eine Gewähr für Richtigkeit, Vollständigkeit und Aktualität kann ich jedoch nicht übernehmen.</p><h2>Haftung für Links</h2><p>Diese Website enthält Links zu externen Websites. Auf deren Inhalte habe ich keinen Einfluss und übernehme dafür keine Haftung.</p><h2>Urheberrecht</h2><p>Die Inhalte und Werke auf dieser Website unterliegen dem Urheberrecht. Vervielfältigung oder Verbreitung erfordern eine schriftliche Genehmigung.</p>''',
'privacy':'''<h2>Allgemeine Informationen</h2><p>Du kannst diese Website nutzen, ohne aktiv personenbezogene Daten anzugeben. Personenbezogene Daten werden erhoben, wenn du mich direkt per E-Mail kontaktierst.</p><h2>Lokale Speicherung und Cookies</h2><p>Diese Website verwendet keine Cookies. Deine Auswahl des Farbschemas und der Sprache wird lokal in deinem Browser gespeichert. Diese Einstellungen werden nicht an den Server übertragen. Ohne gespeicherte Auswahl wird beim allgemeinen Einstieg die Browsersprache berücksichtigt.</p><h2>Serverprotokolle</h2><p>Der Hosting-Anbieter erfasst automatisch Informationen in Serverprotokollen. Dazu können Browsertyp und -version, Betriebssystem, Referrer-URL, Zeitpunkt der Anfrage und IP-Adresse gehören.</p><p>Diese Daten dienen dem ordnungsgemäßen Betrieb und der Sicherheit der Website. Sie werden nicht mit anderen Datenquellen zusammengeführt. Protokolldaten werden nach maximal 7 Tagen automatisch gelöscht.</p><h2>Kontakt</h2><p>Wenn du mich per E-Mail kontaktierst, speichere ich deine Daten zur Bearbeitung deiner Anfrage.</p><h2>Lokal eingebundene Ressourcen</h2><p>Schriften, Skripte und Bilder werden von dieser Website ausgeliefert. GitHub-Statistiken und externe Icon-Skripte werden nicht mehr eingebunden.</p><h2>Terminvereinbarung über Zeeg</h2><p>Für Erstgespräche verlinkt diese Website auf den Terminbuchungsdienst Zeeg, Zeeg GmbH, Friedrichstr. 155, 10117 Berlin, Deutschland. Beim Besuch dieser Website werden keine Daten an Zeeg übertragen. Erst beim Folgen des Links gelangst du auf die Website von Zeeg.</p><p>Bei einer Terminbuchung werden die dort eingegebenen Daten, etwa Name, E-Mail-Adresse, Termin und optionale Nachricht, von Zeeg verarbeitet und an mich übermittelt, damit ich den Termin vorbereiten und durchführen kann. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, vorvertragliche Maßnahmen.</p><p>Weitere Informationen: <a href="https://zeeg.me/en/legal/privacy">Datenschutzerklärung von Zeeg</a>.</p><h2>Berufshaftpflichtversicherung</h2><p>Diese Website verlinkt auf Versicherungsinformationen bei exali AG. Es wird kein Versicherungssiegel von einem externen Server geladen. Erst beim Folgen des Links gelangst du auf die Website von exali.</p><h2>Deine Rechte</h2><p>Du hast das Recht, Auskunft über deine gespeicherten personenbezogenen Daten sowie deren Berichtigung oder Löschung zu verlangen.</p>'''
}


if __name__ == '__main__':
    for lang in ['de','en']:
        make_home(lang)
        make_overview(lang)
        for course in COURSES: make_course(course,lang)
        for project in PROJECTS: make_project(project,lang)
    make_legal()
    urls=[]
    for path,paths in PAGES:
        alternates=''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE+p}"/>' for l,p in paths.items())
        urls.append(f'<url><loc>{BASE+path}</loc>{alternates}</url>')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(urls)+'\n</urlset>\n')
    print(f'Rendered {len(PAGES)} pages and sitemap.xml')
