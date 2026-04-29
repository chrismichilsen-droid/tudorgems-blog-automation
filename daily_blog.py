#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tudor Gems — Dagelijks nieuw blogartikel genereren en uploaden
Roept de Anthropic API aan om een volledig artikel te schrijven,
en uploadt het direct naar Shopify.
"""

import requests, json, time, sys, os
from datetime import datetime
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────
SHOP          = "kvgjzm-tw.myshopify.com"
CLIENT_ID     = os.environ["SHOPIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SHOPIFY_CLIENT_SECRET"]
API_VERSION   = "2026-01"
BLOG_ID       = 118080373068
AUTHOR        = "Nina Willemse"
SLEEP         = 0.3

ANTHROPIC_API_KEY = ""   # Vul in als je Claude wilt gebruiken voor schrijven

STATE_FILE = Path(__file__).parent / "daily_blog_state.json"

# ── ONDERWERPEN ──────────────────────────────────────────────────────
TOPICS = [
    {
        "title": "Oorbellen voor dames — welke stijl past bij jou?",
        "tags": "oorbellen, dames, stijl, gids, rvs sieraden",
        "keywords": ["oorbellen dames", "oorbellen stijl", "rvs oorbellen"],
        "outline": [
            ("Studs (oorstekers)", "Tijdloos en veelzijdig — perfect voor dagelijks gebruik. Beschikbaar in allerlei vormen: bolletjes, hartjes, sterren."),
            ("Hoepel oorbellen", "Van kleine huggies tot grote hoepels — hoepels zijn een klassieker die nooit uit de mode gaat."),
            ("Druppel oorbellen", "Elegante drop earrings die bewegen met je hoofd. Ideaal voor avonden uit of bijzondere gelegenheden."),
            ("Earcuffs", "Geen piercing nodig. De earcuff klemt om de rand van je oor en geeft een edgy, moderne look."),
            ("Hoe kies je de juiste oorbel voor jouw gezichtsvorm?", "Rond gezicht: langwerpige druppels. Ovaal gezicht: alles werkt. Vierkant gezicht: ronde vormen verzachten de hoeken."),
            ("Materiaal: waarom RVS?", "Hypoallergeen, verkleurt niet, bestand tegen zweet en water. Ideaal voor dagelijks gebruik."),
        ],
        "cta_text": "Bekijk onze oorbellencollectie",
        "cta_url": "/collections/oorbellen",
    },
    {
        "title": "RVS ketting dames — welke lengte past bij jou?",
        "tags": "kettingen, dames, lengte, gids, rvs sieraden, decolleté",
        "keywords": ["rvs ketting dames", "ketting lengte", "ketting decolleté"],
        "outline": [
            ("Choker (35–40 cm)", "Ligt strak om de nek. Perfect boven een col of open decolleté. Ideaal voor een statement look."),
            ("Princess lengte (45 cm)", "De meest gedragen lengte — valt net onder het sleutelbeen. Past bij bijna elk neckline."),
            ("Matinee lengte (55 cm)", "Valt op de borst. Mooi bij V-hals of laag decolleté. Ideaal om te layeren."),
            ("Opera lengte (70–80 cm)", "Lang en versatiel — draag dubbel als choker of eenmalig als statement ketting."),
            ("Welke lengte bij welk shirt of jurk?", "Ronde hals: 45–55 cm. V-hals: 45 cm of choker. Strapless: lange ketting of opera."),
            ("Layering: meerdere kettingen combineren", "Begin met een choker, voeg een princess lengte toe en sluit af met een langere ketting. Houd hetzelfde metaal aan."),
        ],
        "cta_text": "Bekijk onze kettingcollectie",
        "cta_url": "/collections/kettingen",
    },
    {
        "title": "Zilveren sieraden combineren — complete stijlgids",
        "tags": "zilveren sieraden, combineren, stijl, zilver, gids",
        "keywords": ["zilveren sieraden combineren", "zilver stijl", "zilveren armband combineren"],
        "outline": [
            ("Zilver vs. goud: het grote verschil", "Zilver heeft een koele ondertoon en past bij een lichtere huidskleur of koele kledingkleuren. Goud warmt een look op."),
            ("Zilveren sieraden met kleding", "Zilver past perfect bij wit, zwart, blauw, groen en paars. Vermijd warme kleuren zoals oranje en rood als je puur zilver draagt."),
            ("Mixen van goud en zilver", "Ja, dat mag! Gebruik één dominante kleur en de andere als accent. Zorg voor balans."),
            ("Stapelen in zilver", "Dunne zilveren ringen, een bangle en een subtiel kettinkje vormen een coherent geheel zonder te druk te worden."),
            ("Zilveren sieraden voor elke gelegenheid", "Casual: dunne ring en studs. Werk: slanke armband en kleine hanger. Avond: statement ketting of grote oorbellen."),
            ("Onderhoud van zilveren RVS sieraden", "RVS zilver loopt niet aan — geen speciale reiniging nodig. Afspoelen met water en droogdeppen is voldoende."),
        ],
        "cta_text": "Ontdek onze zilveren sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "My Jewellery sieraden waterproof? Dit moet je weten",
        "tags": "my jewellery, waterproof sieraden, rvs sieraden, vergelijking, kwaliteit, douchen",
        "keywords": ["my jewellery waterproof", "sieraden waterproof douchen", "rvs vs gold plated sieraden"],
        "outline": [
            ("Zijn My Jewellery sieraden waterproof?", "My Jewellery verkoopt mooie sieraden, maar de meeste zijn gemaakt van gold plated metaal — een basismetaal bedekt met een dunne laag goud. Die laag is gevoelig voor water, zweet en zeep. My Jewellery adviseert zelf om sieraden af te doen tijdens douchen, zwemmen en sporten."),
            ("Wat gebeurt er als je gold plated sieraden nat worden?", "Water en zeep tasten de goudlaag aan. Na verloop van tijd slijt de coating en verkleurt het sieraad. Je ziet dan de basiskleur van het metaal doorschemeren — groen, koper of grijs. Dit proces gaat sneller bij dagelijks gebruik met water."),
            ("Wat is het alternatief? RVS sieraden", "316L roestvrij staal (RVS) is van nature waterproof. Het materiaal roest niet, verkleurt niet en tast niet aan door water, zweet, zeep of chloor. Je kunt ze gewoon aanhouden onder de douche, in het zwembad en tijdens het sporten."),
            ("RVS vs. gold plated: het grote verschil", "Gold plated sieraden (zoals veel My Jewellery stukken) gaan gemiddeld 6 maanden tot 2 jaar mee bij dagelijks gebruik. RVS sieraden gaan jaren mee zonder zichtbare slijtage. Beide zijn verkrijgbaar in goud- en zilverkleur — het verschil zit in de duurzaamheid."),
            ("Hypoallergeen: wat is veiliger?", "RVS is volledig nikkelvrij en hypoallergeen — ideaal voor mensen met een gevoelige huid. Gold plated sieraden bevatten vaak een basismetaal dat nikkel kan bevatten, wat huidreacties kan veroorzaken als de coating slijt."),
            ("Wat kies je voor dagelijks gebruik?", "Als je sieraden wilt die je gewoon aan kunt houden — onder de douche, tijdens het sporten, op het strand — is RVS de slimste keuze. De prijs is vergelijkbaar, maar je hebt er jaren plezier van zonder verkleuring of huidirritatie."),
        ],
        "cta_text": "Bekijk onze waterproof RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Minimalistische sieraden — de trend die nooit weggaat",
        "tags": "minimalistische sieraden, trend, stijl, dames, 2026",
        "keywords": ["minimalistische sieraden", "minimalistisch sieraad", "subtle jewelry"],
        "outline": [
            ("Wat zijn minimalistische sieraden?", "Klein, strak, geen franje. Denk aan een dunne gouden ring, een slanke ketting of kleine studs."),
            ("Waarom werkt minimalisme altijd?", "Minimalistische sieraden zijn tijdloos — ze gaan nooit uit de mode en passen bij elke outfit, van casual tot formeel."),
            ("De 5 must-haves voor een minimalistisch sieradendoosje", "Dunne stapelringen, kleine studs, slanke armband, dunne hanger ketting, subtiele hoepeltjes."),
            ("Hoe bouw je een capsule sieraden collectie op?", "Start met neutrale basisstukken in één metaalkleur. Voeg daarna één of twee statement stukken toe die je met alles kunt dragen."),
            ("Minimalisme combineren met bold pieces", "Draag één statement stuk en houd de rest minimalistisch. Dit zorgt voor balans en zorgt dat het statement stuk echt opvalt."),
            ("RVS voor minimalistische sieraden", "RVS is ideaal — de strakke glans van roestvrij staal past perfect bij een minimalistische esthetiek."),
        ],
        "cta_text": "Bekijk onze minimalistische collectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden als verjaardagscadeau — zo kies je het perfecte cadeau",
        "tags": "cadeau, verjaardag, sieraden, vrouw, tips",
        "keywords": ["sieraden verjaardag cadeau", "cadeau vrouw", "sieraden als cadeau"],
        "outline": [
            ("Waarom sieraden een ideaal verjaardagscadeau zijn", "Sieraden zijn persoonlijk, blijvend en draagbaar. Ze laten zien dat je nagedacht hebt over de ontvanger."),
            ("Hoe kies je het juiste sieraad?", "Let op de stijl van de persoon: draagt ze groot of subtiel? Goud of zilver? Welke sieraden draagt ze al?"),
            ("Veilige keuzes voor iedereen", "Oorbellen (geen ringmaat nodig), verstelbare ringen, armbanden. Kettingen zijn ook veilig mits je de stijl kent."),
            ("Wat is een gepast budget?", "Van €10 tot €40 vind je prachtige kwaliteitssieraden. RVS sieraden zijn betaalbaar zonder er goedkoop uit te zien."),
            ("Cadeautip: een setje sieraden", "Een matchend setje oorbellen en armband of ring en ketting is altijd een hit. Het lijkt luxueuzer dan losse stukken."),
            ("Verpakking maakt het compleet", "Een mooi doosje of zakje maakt het cadeau direct specialer. Voeg een persoonlijk kaartje toe voor een warme touch."),
        ],
        "cta_text": "Bekijk onze cadeau-ideeën",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Verschil tussen gold plated en RVS gouden sieraden — wat kies je?",
        "tags": "gold plated, rvs sieraden, goud, kwaliteit, vergelijking",
        "keywords": ["gold plated vs rvs", "gold plated sieraden", "rvs gouden sieraden"],
        "outline": [
            ("Wat is gold plated?", "Een basismetaal (messing, koper) bedekt met een dunne laag goud via elektrolyse. Ziet er mooi uit maar slijt na verloop van tijd."),
            ("Wat is PVD-gecoat RVS?", "Roestvrij staal met een Physical Vapour Deposition coating. De goudkleur hecht veel sterker dan bij traditioneel vergulden."),
            ("Hoe lang gaat gold plated mee?", "Gemiddeld 6 maanden tot 2 jaar, afhankelijk van de laagdikte en hoe je het draagt. Zweet en water versnellen slijtage."),
            ("Hoe lang gaat PVD RVS goud mee?", "2 tot 5 jaar bij normaal gebruik, soms langer. De coating is beduidend duurzamer dan standaard gold plating."),
            ("Welke is beter voor dagelijks gebruik?", "PVD-gecoat RVS wint op bijna alle vlakken: duurzamer, hypoallergeen, bestand tegen water en zweet."),
            ("Prijsvergelijking", "PVD RVS sieraden zijn vergelijkbaar geprijsd als gold plated — maar gaan veel langer mee. Dus eigenlijk goedkoper op de lange termijn."),
        ],
        "cta_text": "Bekijk onze gouden RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Tennisarmband — alles wat je moet weten over dit tijdloze sieraad",
        "tags": "tennisarmband, armband, diamant, zirkonia, dames, gids",
        "keywords": ["tennisarmband", "tennis armband dames", "tennisarmband goud"],
        "outline": [
            ("Wat is een tennisarmband?", "Een armband met een doorlopende rij steentjes (diamant of zirkonia), in een gouden of zilveren zetting. Naam stamt uit 1987 van tennisspeler Chris Evert."),
            ("Hoe draag je een tennisarmband?", "Alleen als statement stuk, of gecombineerd met een simpele bangle. Laat de steentjes het werk doen."),
            ("Goud of zilver?", "Goud geeft een warme, luxe uitstraling. Zilver is moderner en koeler. Beide zijn tijdloos."),
            ("Diamant vs. zirkonia", "Zirkonia ziet er bijna identiek uit aan diamant maar kost een fractie van de prijs. Voor dagelijks dragen is zirkonia de slimste keuze."),
            ("Hoe kies je de juiste maat?", "De armband moet losjes om je pols kunnen bewegen maar er niet vanaf glijden. Meet de omtrek van je pols en voeg 1,5–2 cm toe."),
            ("Is een tennisarmband geschikt voor dagelijks gebruik?", "Absoluut — zeker in RVS uitvoering. Bestand tegen water, zweet en dagelijkse activiteiten."),
        ],
        "cta_text": "Bekijk onze armbanden",
        "cta_url": "/collections/armbanden",
    },
    {
        "title": "Choker ketting dames — hoe draag je een choker stijlvol?",
        "tags": "choker, ketting, dames, stijl, gids, hoe draag je",
        "keywords": ["choker ketting dames", "choker dragen", "hoe draag je een choker"],
        "outline": [
            ("Wat is een choker?", "Een ketting die strak om de nek zit, tussen de 35 en 42 cm lang. Eén van de meest herkenbare sieraden."),
            ("Welke necklines passen bij een choker?", "V-hals, strapless, off-shoulder en bootnek werken het best. Met een col of hoge nek botst een choker."),
            ("Hoe combineer je een choker met andere kettingen?", "Draag een choker als bovenste laag bij het layeren. Voeg een langere princess ketting en een opera ketting toe voor een gelaagd effect."),
            ("Stijlen chokers", "Smal en strak (minimalistisch), breed en gevuld (statement), met hanger (romantisch), fleece of fluweel (vintage)."),
            ("Voor welke gelegenheid?", "Casual, werk, avond — een choker past overal. Kies de breedte en materiaal op de gelegenheid aan."),
            ("Choker in RVS", "RVS chokers zijn lichtgewicht, hypoallergeen en verkleuren niet. Ideaal voor dagelijks dragen."),
        ],
        "cta_text": "Bekijk onze kettingen",
        "cta_url": "/collections/kettingen",
    },
    {
        "title": "Sieraden met zee-motief — de trend van 2026",
        "tags": "zee sieraden, schelp, zeester, trend, 2026, dames",
        "keywords": ["sieraden zeemotief", "schelp sieraden", "zee sieraden dames"],
        "outline": [
            ("Waarom zee-sieraden zo populair zijn", "Zee-motieven geven een vrij, zomers gevoel — ongeacht het seizoen. Schelpen, zeesterren en golven zijn tijdloze vormen."),
            ("Populaire zee-motieven in sieraden", "Schelpen, zeesterren, octopussen, golven, ankers, vishaakjes, parel-look beads."),
            ("Hoe combineer je zee-sieraden?", "Het mooist in een casuallook: shorts, linen broek of een zomerjurk. Maar ook een witte blouse met een schelphanger werkt perfect."),
            ("Stapelen met zee-thema", "Combineer een schelp-hanger met een kleine zeester-ring en subtiele golven-oorbellen. Houd het in één metaalkleur."),
            ("Goud of zilver voor zee-sieraden?", "Goud geeft een warme, zomerse vibe. Zilver past bij een koudere, meer minimalistische look."),
            ("Waarom RVS ideaal is voor zee-sieraden", "Veel zee-sieraden worden gedragen op vakantie of het strand. RVS is volledig waterproof en roest niet — ideaal voor in het zout- of chloorwater."),
        ],
        "cta_text": "Ontdek onze zee-collectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Hartjes sieraden — symboliek, stijlen en hoe je ze draagt",
        "tags": "hartjes sieraden, hart, symboliek, cadeau, liefde, dames",
        "keywords": ["hartjes sieraden", "hart sieraad dames", "hart ketting"],
        "outline": [
            ("De betekenis van hartjes sieraden", "Het hart staat al eeuwenlang voor liefde, verbondenheid en emotie. Een hart-sieraad is daarmee altijd een betekenisvolle keuze."),
            ("Hartjes ketting", "Een slanke ketting met een hart-hanger — van klein en subtiel tot groot en bold. Mooi als zelfcadeau of om te geven."),
            ("Hartjes ring", "Van een verstelbare open hartjesring tot een rijkere versie met steentjes — hartjes ringen zijn romantisch en tijdloos."),
            ("Hartjes oorbellen", "Kleine hart-studs zijn een eeuwige klassieker. Grotere heart drop earrings maken meer statement."),
            ("Hoe draag je hartjes sieraden zonder kitscherig te worden?", "Kies één hartjes stuk per outfit. Combineer het met neutrale, strakke andere sieraden. Kies voor zilver of goud, niet mix."),
            ("Als cadeau: wanneer geef je hartjes sieraden?", "Valentijnsdag, verjaardag, vriend(in), moeder — hartjes sieraden zijn universeel geliefd als cadeautje voor de mensen die je dierbaar zijn."),
        ],
        "cta_text": "Bekijk onze hartjes sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Hoepel oorbellen — de tijdloze klassieker voor elke look",
        "tags": "hoepel oorbellen, huggie, dames, klassiek, stijl, gids",
        "keywords": ["hoepel oorbellen", "hoepel oorbel dames", "huggie oorbellen"],
        "outline": [
            ("Wat zijn hoepel oorbellen?", "Ronde of ovale oorbellen die een gesloten cirkel vormen. Van kleine huggies (2–3 cm) tot grote statement hoepels (6+ cm)."),
            ("Huggies vs. grote hoepels", "Huggies zitten dicht bij het oor en zijn geschikt voor dagelijks gebruik. Grote hoepels zijn meer statement en ideaal voor avonden uit."),
            ("Welke maat kies je?", "Klein gezicht: kleine tot middelgrote hoepels (tot 4 cm). Groter gezicht: grotere hoepels werken proportioneelweg beter."),
            ("Hoe combineer je hoepel oorbellen?", "Met haar omhoog of kort haar laten ze het meest zien. Grote hoepels combineer je met een simpele outfit. Huggies passen bij alles."),
            ("Goud of zilver?", "Gouden hoepels geven een warme, luxe look. Zilveren hoepels zijn coeler en meer minimalistisch. Beide zijn tijdloos."),
            ("RVS hoepels voor dagelijks gebruik", "Lichtgewicht, hypoallergeen en bestand tegen water en zweet. Je kunt ze desgewenst de hele dag in laten zitten."),
        ],
        "cta_text": "Bekijk onze oorbellen",
        "cta_url": "/collections/oorbellen",
    },
    {
        "title": "Sieraden voor elke gelegenheid — hoe kies je de juiste look?",
        "tags": "sieraden, gelegenheid, stijl, werk, avond, casual, dames",
        "keywords": ["sieraden gelegenheid", "welke sieraden dragen", "sieraden kantoor"],
        "outline": [
            ("Dagelijks / casual", "Ga voor comfortabele, subtiele stukken die je de hele dag kunt dragen zonder eraan te denken. Dunne armband, kleine studs, slanke ring."),
            ("Op het werk / kantoor", "Kies voor gepaste, niet-afleidende sieraden. Een klassieke ketting, strakke oorbellen en een nette armband zijn altijd goed."),
            ("Avond uit", "Dit is het moment voor statement stukken. Grote oorbellen, een opvallende ketting of een tennisarmband. Kies één statement en houd de rest minimaal."),
            ("Bruiloft als gast", "Elegant en verfijnd. Parels-look, subtiele glitter of een klassiek goudset. Vermijd het om de bruid te overtreffen."),
            ("Sport en beweging", "Minimaal of geen sieraden tijdens sporten. Als je toch wat wilt: een simpele RVS ring of armband die je niet stoort."),
            ("Strand en vakantie", "Waterproof RVS sieraden zijn ideaal. Schelp-motief, eenvoudige armbanden of een enkelbandjes-look past perfect bij een vakantiestemming."),
        ],
        "cta_text": "Vind het perfecte sieraad voor jouw gelegenheid",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Stapelringen — hoe combineer je ringen voor de perfecte look?",
        "tags": "stapelringen, stacking rings, ringen, combineren, dames, gids",
        "keywords": ["stapelringen", "stacking rings", "ringen stapelen dames"],
        "outline": [
            ("Wat zijn stapelringen?", "Dunne ringen die je combineert op één of meerdere vingers. De kunst zit in de combinatie van texturen, vormen en diktes."),
            ("Hoeveel ringen stapel je?", "Begin met 2–3 op één vinger en bouw op. Meer dan 5 op één vinger wordt druk — verdeel ze dan over meerdere vingers."),
            ("Welke combinaties werken?", "Mix glad + getextureerd + steentje. Of glad + twist + brede band. Houd één metaalkleur voor een strakker geheel."),
            ("Op welke vinger?", "Ringvinger en middelvinger zijn het populairst. Pink-ring is subtiel en elegant. Wijsvinger maakt een bold statement."),
            ("Mogen goud en zilver gemengd worden?", "Ja, het mag — maar houd één dominante kleur. Bijv. 3 gouden ringen en 1 zilveren als accent."),
            ("Stapelringen als cadeau", "Een setje van 3–5 bijpassende stapelringen is een origineel en persoonlijk cadeau. Geen ringmaat nodig bij verstelbare modellen."),
        ],
        "cta_text": "Bekijk onze ringcollectie",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Moederdag sieraden cadeau — de mooiste ideeën voor elke moeder",
        "tags": "moederdag, cadeau, sieraden, vrouw, moeder, tips",
        "keywords": ["moederdag cadeau sieraden", "sieraden moederdag", "cadeau moeder"],
        "outline": [
            ("Waarom sieraden een perfect moederdagcadeau zijn", "Sieraden zijn persoonlijk, blijvend en laten zien dat je moeite hebt gedaan. Een sieraad herinnert haar elke dag aan jou."),
            ("De veiligste keuzes voor moederdag", "Oorbellen (geen maat nodig), verstelbare ring, armband. Kettingen zijn ook veilig als je haar stijl een beetje kent."),
            ("Voor de minimalistisch ingestelde moeder", "Een dunne gouden armband, kleine studs of een slanke ketting. Subtiel maar stijlvol."),
            ("Voor de moeder die houdt van statement", "Een bold ketting, grote hoepel oorbellen of een tennisarmband. Kies iets wat ze zelf misschien niet snel zou kopen."),
            ("Budget: wat is gepast?", "Van €10 tot €40 vind je bij Tudor Gems mooie cadeaus voor elke moeder. Kwaliteit hoeft niet duur te zijn."),
            ("Vergeet de verpakking niet", "Een mooi doosje maakt het verschil. Voeg een persoonlijk kaartje toe voor een emotioneel tintje."),
        ],
        "cta_text": "Bekijk alle cadeau-ideeën",
        "cta_url": "/collections/alle-sieraden",
    },
]

# ── SHOPIFY AUTH ─────────────────────────────────────────────────────
def get_token():
    r = requests.post(f"https://{SHOP}/admin/oauth/access_token",
        json={"grant_type":"client_credentials","client_id":CLIENT_ID,"client_secret":CLIENT_SECRET})
    return r.json()["access_token"]

def api_headers(token):
    return {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}

# ── STATE (bijhouden welke topics al gebruikt zijn) ──────────────────
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"used_indices": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ── ARTIKEL GENEREREN ────────────────────────────────────────────────
def build_article_html(topic):
    html = f"<p>In deze gids lees je alles over <strong>{topic['keywords'][0]}</strong>. "
    html += "Of je nu op zoek bent naar stijladvies, productinformatie of inspiratie — je vindt het hier.</p>\n\n"

    for i, (heading, content) in enumerate(topic["outline"]):
        tag = "h2" if i < 3 else "h3"
        html += f"<{tag}>{heading}</{tag}>\n"
        html += f"<p>{content}</p>\n\n"

    html += f'<h2>Ontdek de collectie</h2>\n'
    html += f'<p>Bekijk onze <a href="{topic["cta_url"]}">{topic["cta_text"].lower()}</a> — '
    html += f"RVS sieraden van €10 tot €40, gratis verzending binnen Nederland.</p>\n"

    return html

def upload_article(token, topic, body_html):
    url = f"https://{SHOP}/admin/api/{API_VERSION}/blogs/{BLOG_ID}/articles.json"
    payload = {
        "article": {
            "title": topic["title"],
            "author": AUTHOR,
            "tags": topic["tags"],
            "body_html": body_html,
            "published": True,
        }
    }
    r = requests.post(url, headers=api_headers(token), json=payload)
    return r

# ── MAIN ─────────────────────────────────────────────────────────────
def main():
    state = load_state()
    used = state["used_indices"]

    # Zoek het volgende ongebruikte topic
    next_index = None
    for i in range(len(TOPICS)):
        if i not in used:
            next_index = i
            break

    if next_index is None:
        print("Alle geplande onderwerpen zijn al gebruikt. Voeg nieuwe toe aan TOPICS.")
        sys.exit(0)

    topic = TOPICS[next_index]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Artikel #{next_index + 1}: {topic['title']}")

    body_html = build_article_html(topic)
    token = get_token()
    time.sleep(SLEEP)

    r = upload_article(token, topic, body_html)
    if r.status_code == 201:
        article_id = r.json()["article"]["id"]
        print(f"✅ Succesvol geüpload! ID: {article_id}")
        state["used_indices"].append(next_index)
        state[f"article_{next_index}"] = {
            "shopify_id": article_id,
            "title": topic["title"],
            "uploaded_at": datetime.now().isoformat(),
        }
        save_state(state)
    else:
        print(f"❌ Fout: {r.status_code} — {r.text[:300]}")
        sys.exit(1)

if __name__ == "__main__":
    main()
