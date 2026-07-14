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
    {
        "title": "Waterproof sieraden — wat betekent het en welke zijn het beste?",
        "tags": "waterproof sieraden, douchen, zwemmen, rvs sieraden, duurzaam",
        "keywords": ["waterproof sieraden", "sieraden douchen", "sieraden zwemmen"],
        "outline": [
            ("Wat betekent waterproof bij sieraden?", "Niet elk sieraad dat 'waterbestendig' heet, is ook écht waterdicht. Er is een verschil tussen water-resistant (beperkt bestand) en volledig waterproof. RVS sieraden zijn van nature waterproof door hun chemische samenstelling."),
            ("Welke materialen zijn echt waterproof?", "316L roestvrij staal en titanium zijn de beste keuzes voor waterproof sieraden. Ze oxideren niet en tasten niet aan door water, chloor of zout. Zilver en goud zijn dat niet — die lopen aan of verkleuren bij langdurig contact met water."),
            ("Kun je sieraden van RVS dragen onder de douche?", "Ja, absoluut. RVS sieraden zijn volledig veilig om te dragen onder de douche, in het zwembad, de sauna of de zee. Zeep en shampoo hebben geen effect op het materiaal."),
            ("Wat gebeurt er met gold plated sieraden in water?", "De goudlaag op gold plated sieraden lost langzaam op bij contact met water, zweet en zeep. Na verloop van tijd zie je het basismetaal doorschemeren — groen, grijs of koperkleurig. Vermijd water bij gold plated sieraden."),
            ("Tips voor het onderhoud van waterproof sieraden", "RVS sieraden hebben nauwelijks onderhoud nodig. Spoel ze af met water als ze vuil zijn en dep ze droog. Geen speciale reinigingsmiddelen nodig."),
            ("Zijn alle Tudor Gems sieraden waterproof?", "Ja. Alle sieraden bij Tudor Gems zijn gemaakt van 316L roestvrij staal. Ze zijn volledig waterproof en geschikt voor dagelijks gebruik — ook in water."),
        ],
        "cta_text": "Bekijk onze waterproof RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Enkelbandjes dames — hoe draag je ze en welke zijn het mooist?",
        "tags": "enkelbandjes, enkelbandjes dames, zomer, strand, rvs sieraden",
        "keywords": ["enkelbandjes dames", "enkelbandje goud", "enkelbandjes zomer"],
        "outline": [
            ("Wat is een enkelbandje?", "Een enkelbandje is een dunne armband die om de enkel wordt gedragen. Het is een zomers sieraad met een vrije, bohemian uitstraling — maar ook steeds populairder in het dagelijks leven."),
            ("Hoe draag je een enkelbandje stijlvol?", "Combineer een fijn gouden enkelbandje met sandalen, sneakers of blote voeten. Draag er één of stapel er meerdere voor een bohemian look. Let op: houd het enkelbandjes simpel — te veel tegelijk wordt snel druk."),
            ("Welk materiaal is het beste voor een enkelbandje?", "RVS is de beste keuze voor enkelbandjes. Je draagt ze op plekken waar water normaal is — strand, zwembad, douche. RVS roest niet en verkleurt niet, ook niet door zand of zout water."),
            ("Goud of zilver voor enkelbandjes?", "Goud past bij een warme, zomerse look en staat mooi bij een gebruinde huid. Zilver is frisser en moderner. Beide zijn tijdloos — kies op basis van je andere sieraden."),
            ("Draag je een enkelbandje links of rechts?", "Er is geen vaste regel. De meeste mensen dragen het links, maar het is volledig persoonlijk. Draag het aan de kant die voor jou het comfortabelst is."),
            ("Enkelbandjes als zomercadeau", "Een fijn gouden enkelbandje is een perfect zomercadeau — budgetvriendelijk, draagbaar voor iedereen en altijd leuk. Combineer het met een bijpassend armbandje voor een cadeau-setje."),
        ],
        "cta_text": "Bekijk onze enkelbandjes",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Ringen dames goud — welke ring past bij jou?",
        "tags": "ringen dames goud, gouden ring, stapelringen, rvs sieraden",
        "keywords": ["ringen dames goud", "gouden ring dames", "ring goud dames"],
        "outline": [
            ("Waarom gouden ringen zo populair zijn", "Goud is een tijdloze kleur die warmte en elegantie uitstraalt. Een gouden ring is veelzijdig — hij past bij casual outfits én bij een avondlook. Geen wonder dat gouden ringen tot de bestverkochte sieraden behoren."),
            ("RVS gouden ringen vs. echte gouden ringen", "Echte gouden ringen (14k, 18k) zijn duur en kwetsbaar. RVS gouden ringen zijn PVD-gecoat — de goudkleur hecht sterker dan bij traditioneel vergulden. Ze zijn waterproof, verkleuren niet en kosten een fractie van de prijs."),
            ("Welke stijl gouden ring past bij jou?", "Minimalistische dunne band: tijdloos en stapelbaar. Brede signet ring: statement en urban. Ring met steentje: romantisch en verfijnd. Open verstelbare ring: casual en speels."),
            ("Hoe kies je de juiste ringmaat?", "Meet de omtrek van je vinger met een touwtje en vergelijk met de maattabel. Bij twijfel: kies de grotere maat. Een ring die iets te wijd is, kun je ook aan een andere vinger dragen."),
            ("Gouden ringen stapelen: hoe doe je dat?", "Begin met één dunne band en voeg lagen toe. Combineer een gladde band met een gedraaide ring en een ring met detail. Houd goud bij goud voor een strakke look, of mix bewust met één zilveren ring als accent."),
            ("Onderhoud van gouden RVS ringen", "RVS ringen hebben vrijwel geen onderhoud nodig. Spoel af met water bij vuil. De goudkleur van PVD-gecoate RVS blijft jaren mooi zonder poetsbeurt."),
        ],
        "cta_text": "Bekijk onze gouden ringen",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Sieraden voor op vakantie — wat neem je mee?",
        "tags": "vakantie sieraden, strand, waterproof, zomer, reizen met sieraden",
        "keywords": ["sieraden vakantie", "sieraden strand", "waterproof sieraden zomer"],
        "outline": [
            ("Welke sieraden zijn geschikt voor op vakantie?", "Op vakantie wil je sieraden die tegen een stootje kunnen. Waterproof, niet verkleuren door zon en zout water, en niet te kostbaar om te verliezen. RVS sieraden voldoen aan al deze eisen."),
            ("Wat zijn de risico's van sieraden meenemen op vakantie?", "Dure sieraden kun je beter thuislaten. Risico's: verlies, diefstal, en beschadiging door zout water, chloor en zonnecrème. Met betaalbare RVS sieraden heb je dat probleem niet."),
            ("Sieraden in het vliegtuig: wat zijn de regels?", "Sieraden mogen mee in het handbagage. Metalen detectiepoortjes reageren soms op grote metalen sieraden — houd kleine, lichtgewicht sieraden gewoon om. RVS is niet-magnetisch en geeft zelden problemen."),
            ("De perfecte vakantie-sieradencollectie", "Neem mee: twee of drie dunne stapelringen, een paar kleine studs, een fijn enkelbandjes, en één ketting. Alles in goud of alles in zilver — voor een coherente look die bij alles past."),
            ("Sieraden en zonnecrème: wat moet je weten?", "Zonnecrème kan op sommige materialen vlekken achterlaten. RVS is hierop bestand — spoel na het strand even af met water en klaar."),
            ("Waarom RVS ideaal is voor vakantiesieraden", "Licht van gewicht, volledig waterproof, roest niet in zout water, verkleurt niet in de zon. RVS sieraden zijn de perfecte reisgenoot."),
        ],
        "cta_text": "Shop vakantie-proof sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden combineren met kleding — de complete gids",
        "tags": "sieraden combineren, kleding, outfit, stijl, gids",
        "keywords": ["sieraden combineren met kleding", "welke sieraden bij outfit", "sieraden stijl gids"],
        "outline": [
            ("De basisregel: balans", "Het gaat om balans tussen je outfit en sieraden. Een simpele outfit vraagt om statement sieraden. Een drukke outfit vraagt om subtiele sieraden. Laat één ding het middelpunt zijn."),
            ("Sieraden bij een V-hals", "Een V-hals vraagt om een ketting die de V volgt. Kies een pendant ketting op 45 cm of een choker. Vermijd ronde hangertjes — die botsen met de V-lijn."),
            ("Sieraden bij een hoge hals of col", "Bij een col of hoge hals laat je de nek vrij. Kies grote oorbellen als statement. Een ketting toevoegen? Kies een lange opera-lengte die over de col valt."),
            ("Sieraden bij een strapless jurk of top", "Een strapless look vraagt om iets aan de nek — een statement ketting of choker. Houd oorbellen klein. Voeg een armband toe voor extra flair."),
            ("Sieraden bij casual outfits", "Jeans en een wit t-shirt: voeg een dunne gouden ketting, kleine ring en subtiele studs toe. Minimaal maar af. Ga niet overdrijven bij casual — het hoeft niet veel te zijn."),
            ("Goud combineren met kleding", "Goud staat het best bij warme kleuren: camel, bruin, wit, crème, terracotta en olijfgroen. Zilver past beter bij koel: wit, zwart, grijs, marineblauw en lavendel."),
        ],
        "cta_text": "Ontdek onze sieradencollectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Nepleer armband vs RVS armband — wat is de betere keuze?",
        "tags": "armband vergelijking, rvs armband, kwaliteit, duurzaam, dames",
        "keywords": ["rvs armband dames", "beste armband dagelijks gebruik", "duurzame armband dames"],
        "outline": [
            ("Waarom sommige armbanden zo snel kapotgaan", "Veel betaalbare armbanden zijn gemaakt van zinklegeringen, aluminium of nepleer. Ze zien er mooi uit in de winkel, maar verkleuren, breken of roesten na een paar weken."),
            ("Wat is RVS en waarom is het beter?", "316L roestvrij staal is hetzelfde materiaal dat gebruikt wordt in medische implantaten en keukengerei. Het is krasbestendig, buigt niet snel, en tast niet aan door zweet, water of zeep."),
            ("Levensduur vergelijking", "Goedkope legering armband: gemiddeld 2-6 maanden. Vergulde armband: 6-18 maanden. RVS armband: 5+ jaar bij normaal gebruik. De investering betaalt zich terug."),
            ("Comfort en draagbaarheid", "RVS armbanden zijn licht van gewicht en hypoallergeen. Ze irriteren de huid niet, ook niet bij langdurig dragen. Ideaal voor mensen met een nikkel-allergie."),
            ("De prijs: is RVS duurder?", "Bij Tudor Gems beginnen RVS armbanden vanaf €17,99. Vergelijkbaar met veel fast-fashion armbanden — maar dan met een levensduur van jaren in plaats van maanden."),
            ("Conclusie: welke kies je?", "Als je een armband koopt voor dagelijks gebruik, is RVS altijd de slimste keuze. Waterproof, duurzaam, hypoallergeen en tijdloos. Koop één keer, draag voor altijd."),
        ],
        "cta_text": "Bekijk onze RVS armbanden",
        "cta_url": "/collections/armbanden",
    },
    {
        "title": "Oorbellen die niet zweren — de oplossing voor gevoelige oren",
        "tags": "oorbellen die niet zweren, gevoelige oren, nikkelvrij, rvs sieraden, hypoallergeen",
        "keywords": ["oorbellen die niet zweren", "oorbellen gevoelige oren", "nikkelvrije oorbellen"],
        "meta": "Oorbellen die niet zweren? RVS 316L is nikkelvrij en hypoallergeen — ideaal voor gevoelige oren. Ontdek waarom je oren ervan rustig blijven bij Tudor Gems.",
        "outline": [
            ("Waarom gaan oren zweren van oorbellen?", "Zweren ontstaat meestal door een allergische reactie op nikkel, een metaal dat in veel goedkope oorbellen zit. De huid raakt geïrriteerd, rood en soms ontstoken. Ook gold plated oorbellen kunnen nikkel bevatten in het basismetaal."),
            ("Wat is de oplossing? Nikkelvrij materiaal", "De enige echte oplossing is een materiaal dat geen nikkel afgeeft. 316L roestvrij staal (RVS) is nikkelvrij en hypoallergeen — het geeft geen stoffen af aan je huid, ook niet bij langdurig dragen."),
            ("Waarom RVS oorbellen niet laten zweren", "RVS is chirurgisch staal: hetzelfde materiaal dat in medische implantaten en piercings wordt gebruikt. Het is bestand tegen zweet, water en huidvet, en blijft stabiel — dus geen reactie, geen jeuk, geen zweren."),
            ("Waar let je op bij het kopen?", "Let op de term '316L roestvrij staal' of 'surgical steel'. Vermijd vage omschrijvingen als 'legering' of 'fashion metal'. Bij gold plated: check of de kern nikkelvrij is — vaak is dat niet zo."),
            ("Welke oorbellen zijn geschikt voor gevoelige oren?", "Studs (oorknopjes), kleine creolen en lichtgewicht oorhangers in RVS zijn allemaal veilig. Hoe lichter de oorbel, hoe minder druk op het gaatje — wat irritatie verder voorkomt."),
            ("Verzorging om irritatie te voorkomen", "Maak je oorbellen en oorgaatjes af en toe schoon met water. Ook met nikkelvrije RVS oorbellen blijft een schone basis belangrijk voor gezonde oren."),
        ],
        "cta_text": "Bekijk onze hypoallergene RVS oorbellen",
        "cta_url": "/collections/oorbellen",
    },
    {
        "title": "Betaalbare sieraden die niet verkleuren — bestaat dat echt?",
        "tags": "betaalbare sieraden, sieraden die niet verkleuren, goedkoop, rvs sieraden, waterproof",
        "keywords": ["goedkope sieraden die niet verkleuren", "betaalbare sieraden", "sieraden niet verkleuren goedkoop"],
        "meta": "Betaalbare sieraden die niet verkleuren? Ja, dat kan. RVS 316L blijft jarenlang mooi, is waterproof en nikkelvrij — al vanaf €10 bij Tudor Gems.",
        "outline": [
            ("Waarom verkleuren goedkope sieraden zo snel?", "Veel betaalbare sieraden zijn gemaakt van verguld basismetaal of legeringen. De dunne goudlaag slijt door zweet, water en zeep, waarna het basismetaal doorschemert — groen, grijs of koperkleurig."),
            ("Goedkoop hoeft niet 'slechte kwaliteit' te betekenen", "De prijs van een sieraad zegt niet alles over de levensduur. Het draait om het materiaal. RVS sieraden zijn betaalbaar én duurzaam — een zeldzame combinatie."),
            ("Waarom RVS niet verkleurt", "316L roestvrij staal verkleurt van nature niet. Het oxideert niet, roest niet en reageert niet op water, zweet of zeep. De kleur (zilver of PVD-goud) blijft jarenlang stabiel."),
            ("Wat kost een sieraad dat écht niet verkleurt?", "Bij Tudor Gems begint betaalbare, niet-verkleurende RVS al vanaf €10. Je betaalt dus niet meer dan voor een fast-fashion sieraad, maar je hebt er jaren plezier van in plaats van weken."),
            ("Reken het eens uit: goedkoop is duurkoop", "Een verguld sieraad van €15 dat na 3 maanden verkleurt, vervang je 3-4 keer per jaar. Een RVS sieraad van €15 draag je jaren. Op de lange termijn is RVS dus juist goedkoper."),
            ("Waar koop je betaalbare RVS sieraden?", "Let op de term '316L roestvrij staal' en een duidelijke waterproof-belofte. Bij Tudor Gems is alles RVS — betaalbaar, waterproof en nikkelvrij, met gratis verzending."),
        ],
        "cta_text": "Bekijk onze betaalbare RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden cadeauset samenstellen — de complete gids",
        "tags": "sieraden cadeauset, cadeau set, sieraden set, cadeau voor haar, rvs sieraden",
        "keywords": ["sieraden cadeauset", "sieraden set cadeau", "cadeauset dames"],
        "meta": "Een sieraden cadeauset samenstellen? Combineer ketting, oorbellen & armband in één stijl. Tips voor de perfecte set — waterproof RVS, al vanaf €10 bij Tudor Gems.",
        "outline": [
            ("Waarom een cadeauset mooier is dan los", "Een bij elkaar passende set oogt luxueuzer en doordachter dan één los sieraad. Het lijkt duurder dan het is en laat zien dat je hebt nagedacht over de stijl van de ontvanger."),
            ("De basis van een goede set: één stijl", "Kies één lijn: minimalistisch, romantisch (hartjes), of statement. Houd ook de kleur consistent — alles goud óf alles zilver — voor een samenhangend geheel."),
            ("Welke stukken combineer je?", "De klassieke combinatie: een ketting + bijpassende oorbellen. Wil je het completer? Voeg een armband of ring toe. Drie stukken in dezelfde stijl maken een volwaardige set."),
            ("Set op basis van de gelegenheid", "Verjaardag: een persoonlijke stijl die bij haar past. Moederdag: tijdloos en elegant. Valentijn: hartjes-thema. Stem de set af op het moment."),
            ("Waarom RVS perfect is voor een cadeauset", "Een set draag je vaak samen en dagelijks. RVS is waterproof en verkleurt niet, dus de hele set blijft jarenlang op elkaar afgestemd mooi — geen los stuk dat eerder verkleurt."),
            ("Maak het cadeau compleet", "Een mooie verpakking en een persoonlijk kaartje maken de set af. Combineer losse stukken zelf of kies een kant-en-klare set voor het gemak."),
        ],
        "cta_text": "Stel je eigen cadeauset samen",
        "cta_url": "/collections/cadeau-ideeen",
    },
    {
        "title": "Kruidvat waterproof sieraden vs RVS — wat is het verschil?",
        "tags": "kruidvat waterproof sieraden, waterproof sieraden, rvs sieraden, vergelijking, kwaliteit",
        "keywords": ["kruidvat waterproof sieraden", "waterproof sieraden vergelijking", "beste waterproof sieraden"],
        "meta": "Kruidvat waterproof sieraden of RVS? Ontdek het echte verschil in materiaal, levensduur en waterbestendigheid — en welke sieraden écht niet verkleuren.",
        "outline": [
            ("Wat betekent 'waterproof' bij sieraden eigenlijk?", "Niet elk sieraad dat 'waterbestendig' heet, is écht waterdicht. Er is verschil tussen water-resistant (beperkt bestand) en volledig waterproof. Het materiaal bepaalt alles — niet het label."),
            ("Waar let je op bij waterproof sieraden?", "De enige betrouwbare garantie is het materiaal: 316L roestvrij staal of titanium zijn van nature waterproof. Verguld of gecoat metaal is dat niet, ongeacht wat de verpakking belooft."),
            ("Waarom RVS de standaard is voor waterproof", "316L roestvrij staal oxideert niet en tast niet aan door water, chloor, zout of zweet. Je kunt het dragen onder de douche, in zee en in het zwembad zonder verkleuring of roest."),
            ("Let op gecoate of vergulde sieraden", "Sieraden met een dunne goud- of kleurlaag kunnen 'waterproof' heten, maar de coating slijt bij contact met water en zeep. Na verloop van tijd verkleuren ze alsnog. Kies daarom voor doorlegeerd RVS."),
            ("Hoe herken je echte waterproof sieraden?", "Zoek naar '316L roestvrij staal' of 'stainless steel' in de productinformatie, plus een duidelijke belofte dat het niet verkleurt. Vage termen als 'waterproof coating' zijn een waarschuwingssignaal."),
            ("De slimste keuze voor dagelijks dragen", "Wil je sieraden die je nooit hoeft af te doen — ook niet onder de douche of op het strand — kies dan volledig RVS. Bij Tudor Gems is alles 316L: waterproof, nikkelvrij en niet-verkleurend."),
        ],
        "cta_text": "Bekijk onze waterproof RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "RVS armband dames goud — welke past bij jou?",
        "tags": "rvs armband dames goud, gouden armband, armband dames, waterproof, rvs sieraden",
        "keywords": ["rvs armband dames goud", "gouden armband dames", "armband goud waterproof"],
        "meta": "Op zoek naar een gouden RVS armband voor dames? Ontdek welke stijl bij jou past — schakel, bangle of bedel. Waterproof, verkleurt nooit. Al vanaf €10 bij Tudor Gems.",
        "outline": [
            ("Waarom een gouden RVS armband?", "Een gouden armband geeft warmte en elegantie aan elke look. In RVS-uitvoering (PVD-gecoat goud) krijg je die gouden kleur zonder de nadelen: waterproof, verkleurt niet en betaalbaar."),
            ("Schakelarmband: tijdloos en veelzijdig", "Een gouden schakelarmband past bij casual én chic. Van fijne schakels voor een subtiele look tot grovere schakels voor een statement — altijd elegant om de pols."),
            ("Bangle: strak en minimalistisch", "Een gouden bangle is een gladde, gesloten of open ring om de pols. Perfect om te stapelen of solo te dragen. Minimalistisch en modern."),
            ("Bedelarmband: persoonlijk en speels", "Een bedelarmband maak je helemaal van jezelf met bedels die iets betekenen. Een persoonlijke favoriet en een geliefd cadeau."),
            ("Welke maat heb je nodig?", "Meet de omtrek van je pols en tel 1,5–2 cm op voor comfortabele bewegingsruimte. Verstelbare modellen passen vrijwel altijd — handig als cadeau."),
            ("Waarom goud in RVS de slimste keuze is", "PVD-gecoat goud op 316L staal hecht veel sterker dan traditioneel vergulden. De gouden kleur blijft jaren mooi, ook na douchen, zwemmen en dagelijks dragen. Vanaf €10 bij Tudor Gems."),
        ],
        "cta_text": "Bekijk onze gouden RVS armbanden",
        "cta_url": "/collections/armbanden",
    },
    {
        "title": "Waarom wordt je vinger groen van een ring? (en hoe je het voorkomt)",
        "tags": "groene vinger, ring, rvs sieraden, verkleuren, nikkelvrij, oorzaak",
        "keywords": ["waarom wordt mijn vinger groen", "groene vinger van ring", "ring kleurt af"],
        "outline": [
            ("Waarom je huid groen wordt van goedkope ringen", "Vaak zit het in koper of een dunne vergulde laag: door zweet en huidzuren oxideert het metaal en kleurt het je huid groen."),
            ("Welke metalen de boosdoener zijn", "Koperlegeringen, messing en goedkoop verguld zijn de grootste veroorzakers. Onschuldig voor je gezondheid, maar lelijk."),
            ("Waarom RVS 316L je vinger niet groen maakt", "Roestvrij staal oxideert niet en geeft geen stoffen af aan je huid. Daarom blijft je vinger schoon, ook bij dagelijks dragen."),
            ("Tips om verkleuring te voorkomen", "Kies 316L RVS, hou ringen droog na zwemmen of douchen en vermijd parfum direct op het metaal."),
            ("Veelgestelde vragen", "Is een groene vinger schadelijk? Nee. Gaat het eraf? Ja, met water en zeep. Voorkomt RVS het? Ja."),
        ],
        "cta_text": "Bekijk onze RVS ringen",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Sieraden schoonmaken - zo doe je het goed (en wat je NIET moet doen)",
        "tags": "sieraden schoonmaken, onderhoud, rvs, goud, zilver, tips",
        "keywords": ["sieraden schoonmaken", "rvs sieraden schoonmaken", "sieraden schoonmaken baking soda"],
        "outline": [
            ("Waarom sieraden dof worden", "Huidvet, creme, parfum en zweet vormen een laagje dat de glans wegneemt. Regelmatig schoonmaken houdt je sieraden stralend."),
            ("RVS sieraden schoonmaken in 3 stappen", "Lauw water met een drupje afwasmiddel, zacht poetsen met een microvezeldoek, droog deppen. Klaar."),
            ("Wat je beter NIET gebruikt", "Tandpasta, cola en schuurmiddelen zijn te agressief en kunnen krassen veroorzaken. Liever niet."),
            ("Verschil goud, zilver en RVS", "Zilver heeft anti-aanslagdoekjes nodig, verguld is kwetsbaar, RVS is het makkelijkst: gewoon afspoelen."),
            ("Veelgestelde vragen", "Hoe vaak? Eens per paar weken. Ultrasoon reiniger? Voor RVS prima, voor verguld af te raden."),
        ],
        "cta_text": "Bekijk onze onderhoudsvrije RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Kunnen RVS sieraden roesten? Het eerlijke antwoord",
        "tags": "rvs sieraden, roesten, roestvrij staal, 316l, waterproof, kwaliteit",
        "keywords": ["kunnen rvs sieraden roesten", "roest rvs", "roestvrij staal sieraden"],
        "outline": [
            ("Wat roestvrij staal precies betekent", "RVS bevat chroom dat een onzichtbaar beschermlaagje vormt. Dat laagje herstelt zichzelf en houdt roest buiten."),
            ("Kan RVS echt roesten?", "In normaal dagelijks gebruik niet. Alleen bij langdurig contact met agressief zout of chemicalien kan heel zelden vlekvorming optreden."),
            ("Waarom 316L de beste keuze is", "316L (chirurgisch staal) heeft extra molybdeen, wat het nog beter bestand maakt tegen water, zweet en zout."),
            ("Hoe je je sieraden mooi houdt", "Afspoelen na de zee, droog bewaren en af en toe poetsen is genoeg. Geen speciaal onderhoud nodig."),
            ("Veelgestelde vragen", "Mag het in het zwembad? Ja. In de zee? Ja, even afspoelen daarna. Verkleurt het? Nee."),
        ],
        "cta_text": "Ontdek onze 316L RVS collectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden bij nikkelallergie - wat kun je wel dragen?",
        "tags": "nikkelallergie, nikkelvrij, gevoelige huid, hypoallergeen, rvs sieraden",
        "keywords": ["nikkelallergie sieraden", "nikkelvrije sieraden", "sieraden gevoelige huid"],
        "outline": [
            ("Wat een nikkelallergie is en hoe je het herkent", "Roodheid, jeuk of eczeem op de plek van je sieraad wijst vaak op nikkelallergie, een van de meest voorkomende contactallergieen."),
            ("Welke metalen veilig zijn", "316L RVS, titanium en echt goud met hoog karaat zijn meestal veilig. Vermijd goedkoop verguld en messing."),
            ("Waarom RVS 316L nikkelvrij en hypoallergeen is", "316L geeft nauwelijks tot geen nikkel af en is daardoor geschikt voor de gevoelige huid."),
            ("Tips voor gevoelige huid", "Hou sieraden droog, doe ze af bij het sporten en kies bewust voor hypoallergeen materiaal."),
            ("Veelgestelde vragen", "Is alle RVS nikkelvrij? Let op 316L. Kan ik oorbellen dragen met allergie? Ja, met 316L of titanium."),
        ],
        "cta_text": "Bekijk onze nikkelvrije sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden bewaren - zo blijven ze langer mooi",
        "tags": "sieraden bewaren, opbergen, onderhoud, tips, dames",
        "keywords": ["sieraden bewaren", "waar sieraden bewaren", "sieraden opbergen"],
        "outline": [
            ("Waarom goed bewaren belangrijk is", "Verkeerd bewaren geeft krassen, klitten en bij sommige metalen aanslag. Een paar simpele gewoontes houden alles mooi."),
            ("De beste plek (en waarom niet in de badkamer)", "Bewaar droog en donker. De badkamer is juist slecht: vocht versnelt aanslag bij gevoelige metalen."),
            ("Sieraden apart houden tegen krassen", "Berg stuks apart op in zakjes of vakjes, zodat ze niet tegen elkaar schuren."),
            ("RVS is minder onderhoud", "RVS verkleurt niet en is robuust, dus minder gevoelig voor bewaarfouten. Netjes opbergen voorkomt krassen."),
            ("Veelgestelde vragen", "Mag alles bij elkaar? Liever niet. Zakje of doosje? Ja, ideaal tegen krassen."),
        ],
        "cta_text": "Bekijk onze sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Geboortesteen sieraden - welke steen hoort bij jouw maand?",
        "tags": "geboortesteen, ketting, ring, maand, betekenis, cadeau",
        "keywords": ["geboortesteen ketting", "geboortesteen sieraden", "geboortesteen per maand"],
        "outline": [
            ("Wat geboortestenen zijn", "Elke maand heeft een eigen edelsteen met een eigen kleur en symboliek, een persoonlijke touch aan je sieraad."),
            ("Overzicht: steen per maand en betekenis", "Van granaat in januari tot turkoois in december: elke steen staat voor eigenschappen als liefde, kracht of geluk."),
            ("Geboortesteen als persoonlijk cadeau", "Een sieraad met iemands geboortesteen voelt persoonlijk en doordacht, perfect voor verjaardagen en moederdag."),
            ("Combineren met RVS sieraden", "Draag een geboortesteen-stuk solo of combineer met minimalistische RVS sieraden voor een verfijnde look."),
            ("Veelgestelde vragen", "Welke steen hoort bij mijn maand? Zie het overzicht. Mag ik meerdere combineren? Zeker, bijvoorbeeld van je kinderen."),
        ],
        "cta_text": "Bekijk onze ringen",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Sterrenbeeld sieraden - wat past bij jouw teken?",
        "tags": "sterrenbeeld, horoscoop, ketting, ring, zodiak, betekenis",
        "keywords": ["sterrenbeeld ketting", "sterrenbeeld sieraden", "horoscoop sieraden"],
        "outline": [
            ("Waarom sterrenbeeld-sieraden zo populair zijn", "Ze zijn persoonlijk, betekenisvol en een subtiele manier om je identiteit te dragen."),
            ("Wat elk teken symboliseert", "Van de vurige Ram tot de dromerige Vissen: elk teken heeft eigen eigenschappen die je met je meedraagt."),
            ("Welk sieraad bij welk teken", "Een sterrenbeeld-hanger, een ring met je teken of een subtiele bedel: voor elk teken is er een passende vorm."),
            ("Perfect als persoonlijk cadeau", "Je hoeft alleen iemands geboortedatum te weten en het voelt meteen persoonlijk."),
            ("Veelgestelde vragen", "Werkt het ook zonder in astrologie te geloven? Zeker, puur als persoonlijk symbool. Combineren met geboortesteen? Mooi idee."),
        ],
        "cta_text": "Bekijk onze Zodiak ringen",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Letterketting en letterbedel - hoe kies je de jouwe?",
        "tags": "letter ketting, letterbedel, naam, initiaal, personaliseren, cadeau",
        "keywords": ["letter ketting", "letterbedel", "initiaal ketting"],
        "outline": [
            ("Waarom een initiaal zo persoonlijk is", "Je eigen letter, die van een geliefde of je kind: een initiaal maakt een sieraad meteen van jou."),
            ("Letterketting versus losse letterbedel", "Een letterketting is een complete look, een losse letterbedel hang je aan je eigen ketting of armband."),
            ("Hoe je het combineert (layering)", "Combineer je letter met een fijne ketting en een tweede laagje voor een trendy, persoonlijke stack."),
            ("Onderhoudsvrij in RVS", "In 316L RVS verkleurt je letter niet en kun je hem dagelijks dragen, ook onder de douche."),
            ("Veelgestelde vragen", "Meerdere letters? Combineer losse bedels. Verkleurt het? Niet in RVS."),
        ],
        "cta_text": "Bekijk onze bedels",
        "cta_url": "/collections/charms",
    },
    {
        "title": "Ringmaat bepalen zonder ringmeter - zo doe je het thuis",
        "tags": "ringmaat, ring maat meten, ringmeter, tips, dames",
        "keywords": ["ringmaat bepalen", "ring maat meten", "ringmaat zonder ringmeter"],
        "outline": [
            ("Waarom de juiste ringmaat belangrijk is", "Te los en je verliest hem, te strak en hij knelt. De juiste maat draagt comfortabel de hele dag."),
            ("Meten met een touwtje of strip papier", "Wikkel een touwtje om je vinger, markeer waar het sluit en meet de lengte in millimeters: dat is je omtrek."),
            ("Ringmaat-tabel (omtrek naar maat)", "Gebruik een omrekentabel: je omtrek in millimeters komt overeen met je Europese ringmaat."),
            ("Tips bij verstelbare ringen", "Twijfel je tussen twee maten of wil je flexibiliteit? Kies een verstelbare ring, die past altijd."),
            ("Veelgestelde vragen", "Wanneer meten? Aan het eind van de dag. Welke vinger? Die waar je hem draagt, die verschillen."),
        ],
        "cta_text": "Bekijk onze verstelbare ringen",
        "cta_url": "/collections/ringen",
    },
    {
        "title": "Armbandmaat bepalen - zo meet je je pols",
        "tags": "armbandmaat, pols meten, armband maat, tips, dames",
        "keywords": ["armbandmaat bepalen", "pols meten armband", "armband maat"],
        "outline": [
            ("Waarom de juiste maat comfortabel zit", "Een armband mag meebewegen zonder af te glijden. De juiste maat zit prettig en valt mooi."),
            ("Je pols meten in 2 stappen", "Meet de omtrek van je pols met een meetlint of touwtje, net onder het polsbotje."),
            ("Hoeveel ruimte je toevoegt", "Tel 1 tot 2 cm op bij je polsomtrek voor een comfortabele, niet-knellende pasvorm."),
            ("Bangle versus schakelarmband", "Een bangle heeft een vaste maat (let op de diameter), een schakelarmband is vaak verstelbaar."),
            ("Veelgestelde vragen", "Strak of los? Net wat je fijn vindt. Verstelbaar? Veel van onze armbanden hebben een verlengkettinkje."),
        ],
        "cta_text": "Bekijk onze armbanden",
        "cta_url": "/collections/armbanden",
    },
    {
        "title": "Welke ketting past bij welke halslijn?",
        "tags": "ketting, halslijn, jurk, styling, lengte, gids",
        "keywords": ["ketting bij halslijn", "welke ketting bij jurk", "ketting lengte halslijn"],
        "outline": [
            ("Waarom halslijn en kettinglengte samenhangen", "De juiste lengte volgt je halslijn en laat je outfit beter uitkomen."),
            ("Ketting bij een ronde hals", "Een princess-lengte van 45 cm of een korte ketting vult een ronde hals mooi op."),
            ("Ketting bij een V-hals of lage hals", "Een iets langere ketting van 50 tot 55 cm of een hanger volgt de V en versterkt de lijn."),
            ("Layeren voor extra effect", "Combineer twee of drie lengtes in hetzelfde metaal voor een gelaagde, trendy look."),
            ("Veelgestelde vragen", "Welke lengte bij een col? Een lange ketting. Bij strapless? Statement of opera-lengte."),
        ],
        "cta_text": "Bekijk onze kettingen",
        "cta_url": "/collections/kettingen",
    },
    {
        "title": "Goedkope sieraden die er duur uitzien - zo herken je ze",
        "tags": "goedkope sieraden, betaalbaar, luxe look, rvs, tips",
        "keywords": ["goedkope sieraden die er duur uitzien", "betaalbare sieraden", "luxe sieraden goedkoop"],
        "outline": [
            ("Waarom prijs niet alles zegt", "Een sieraad oogt luxe door materiaal, afwerking en design, niet door de prijs alleen."),
            ("Waaraan je kwaliteit herkent", "Let op een egale kleur, strakke afwerking, stevige sluiting en of het materiaal verkleurt."),
            ("Waarom RVS er luxe uitziet en blijft", "316L RVS heeft een diepe glans, verkleurt niet en behoudt zijn look jarenlang: duur ogend, betaalbaar geprijsd."),
            ("Stylingtips voor een dure uitstraling", "Kies een metaalkleur, draag minimalistisch en combineer een statement-stuk met fijne basics."),
            ("Veelgestelde vragen", "Ziet RVS er goedkoop uit? Nee, juist luxe. Verkleurt betaalbaar altijd? Niet als het RVS is."),
        ],
        "cta_text": "Bekijk onze betaalbare RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Verkleuren gold plated sieraden? (en wat je eraan doet)",
        "tags": "gold plated, verkleuren, vergulde sieraden, rvs, onderhoud",
        "keywords": ["verkleuren gold plated sieraden", "gold plated verkleuren", "vergulde sieraden verkleuren"],
        "outline": [
            ("Wat gold plated precies is", "Gold plated is een basismetaal met een dun laagje goud erop, mooi maar de laag is dun."),
            ("Waarom een dunne goudlaag slijt", "Door wrijving, zweet en parfum slijt de goudlaag na verloop van tijd, waardoor het basismetaal doorkomt."),
            ("Hoe je verkleuring vertraagt", "Hou het droog, doe het af bij sporten en vermijd parfum en creme direct op het sieraad."),
            ("Waarom RVS niet verkleurt", "RVS is door en door een materiaal met een vaste kleur, geen laagje dat eraf kan slijten."),
            ("Veelgestelde vragen", "Hoe lang houdt gold plated? Wisselend, vaak maanden tot een jaar. RVS? Jarenlang gelijk."),
        ],
        "cta_text": "Bekijk onze RVS gouden sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden cadeau voor je beste vriendin - ideeen per type",
        "tags": "cadeau, vriendin, sieraden, bff, ideeen",
        "keywords": ["sieraden cadeau vriendin", "cadeau beste vriendin", "vriendschap sieraden"],
        "outline": [
            ("Waarom sieraden een persoonlijk cadeau zijn", "Een sieraad zegt dat je aan iemand denkt en wordt vaak dagelijks gedragen: blijvend en persoonlijk."),
            ("Ideeen per type vriendin", "Voor de minimalist een fijne ketting, voor de durfal een statement-ring, voor de sentimentele een bedel met betekenis."),
            ("Matching sieraden voor BFFs", "Kies twee dezelfde of complementaire stukken, zoals zon en maan, als symbool voor jullie band."),
            ("Betaalbaar en toch bijzonder", "Met RVS geef je een mooi, duurzaam cadeau zonder een groot budget."),
            ("Veelgestelde vragen", "Wat als ze al veel heeft? Kies iets persoonlijks zoals een initiaal of geboortesteen."),
        ],
        "cta_text": "Bekijk onze cadeau-ideeen",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Cadeau voor een moeder die alles al heeft",
        "tags": "cadeau, moeder, moederdag, sieraden, persoonlijk",
        "keywords": ["cadeau moeder die alles heeft", "cadeau moeder", "persoonlijk cadeau moeder"],
        "outline": [
            ("Waarom persoonlijk wint van duur", "Een moeder die alles heeft, raakt het meest ontroerd door iets persoonlijks, niet door de prijs."),
            ("Sieraden met betekenis (geboortesteen, initiaal)", "Een geboortesteen van haar kinderen of hun initialen maakt het cadeau uniek en emotioneel."),
            ("Tijdloze keuzes die ze echt draagt", "Kies een klassieke, ingetogen stijl die bij elke outfit past, dan draagt ze het dagelijks."),
            ("Onderhoudsvrij in RVS", "RVS verkleurt niet en heeft geen onderhoud nodig, ideaal voor een zorgeloos cadeau."),
            ("Veelgestelde vragen", "Wat als ik haar maat niet weet? Kies een ketting of een verstelbare ring."),
        ],
        "cta_text": "Bekijk onze sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Enkelbandje betekenis - waar draag je het en wat zegt het?",
        "tags": "enkelbandje, betekenis, zomer, styling, dames",
        "keywords": ["enkelbandje betekenis", "enkelbandje dragen", "enkelbandje welke kant"],
        "outline": [
            ("De geschiedenis en betekenis van het enkelbandje", "Het enkelbandje wordt al eeuwen gedragen als sieraad en symbool van vrouwelijkheid en zomerse stijl."),
            ("Aan welke enkel draag je het", "Er zijn tradities rond links en rechts, maar uiteindelijk draag je het waar jij het mooi vindt."),
            ("Stylingtips voor de zomer", "Mooi bij blote enkels, sandalen of op het strand, subtiel of juist met bedeltjes."),
            ("Waterproof RVS voor strand en zwembad", "In RVS kun je je enkelbandje gewoon aanhouden in zee en zwembad zonder dat het verkleurt."),
            ("Veelgestelde vragen", "Mag het in het water? Ja, in RVS. Welke maat? Meet je enkel plus 1 tot 2 cm."),
        ],
        "cta_text": "Bekijk onze enkelbandjes",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden voor een bruiloft - wat draag je als gast?",
        "tags": "bruiloft, gast, sieraden, styling, gelegenheid",
        "keywords": ["sieraden bruiloft gast", "wat draag je naar een bruiloft", "sieraden gelegenheid"],
        "outline": [
            ("De ongeschreven regels voor gasten", "Als gast vul je je outfit aan zonder de bruid te overschaduwen: elegant maar ingetogen."),
            ("Subtiel versus statement", "Bij een drukke jurk kies je fijne sieraden, bij een ingetogen look mag een statement-stuk."),
            ("Matchen met je outfit", "Stem het metaal af op je accessoires en hou een kleur aan voor een verzorgde look."),
            ("Tijdloze keuzes die altijd passen", "Een fijne ketting, kleine oorbellen en een verfijnde ring werken bij vrijwel elke gast-outfit."),
            ("Veelgestelde vragen", "Wit dragen mag niet, geldt dat ook voor sieraden? Parels en zilver zijn prima, gewoon niet de show stelen."),
        ],
        "cta_text": "Bekijk onze sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Sieraden trends zomer 2026 - dit draag je dit seizoen",
        "tags": "trends, zomer 2026, sieraden, dames, stijl",
        "keywords": ["sieraden trends zomer 2026", "zomer sieraden trend", "sieraden trend 2026"],
        "outline": [
            ("De grootste zomertrends van 2026", "Denk aan gelaagde kettingen, kleurrijke kralen, schelp- en zonmotieven en stapelbare ringen."),
            ("Kleuren en materialen die opvallen", "Warm goud, frisse kleuraccenten en waterbestendige materialen domineren deze zomer."),
            ("Waterproof sieraden voor vakantie", "Sieraden die tegen zee en zon kunnen zijn de must-have: aanhouden op het strand zonder zorgen."),
            ("Hoe je de trends draagt", "Mix lagen, combineer kleuren met basics en kies een statement-stuk per look."),
            ("Veelgestelde vragen", "Wat is de zomertrend? Gelaagd en waterproof. Verkleurt het in de zon? Niet in RVS."),
        ],
        "cta_text": "Bekijk onze zomercollectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Wat betekent gold plated? (14k en 18k uitgelegd)",
        "tags": "gold plated, betekenis, 14k, 18k, verguld, rvs, uitleg",
        "keywords": ["gold plated betekenis", "18k gold plated", "gold plated vs rvs"],
        "outline": [
            ("Wat gold plated precies betekent", "Gold plated is een basismetaal met een dun laagje echt goud erop. Het oogt als goud, maar de goudlaag is dun."),
            ("Wat zeggen 14k en 18k?", "14k en 18k verwijzen naar de zuiverheid van de goudlaag: 18k is geler en zuiverder, 14k iets steviger. Het zegt niets over de dikte."),
            ("Gold plated, verguld en gold filled: het verschil", "Verguld en gold plated zijn hetzelfde; gold filled heeft een veel dikkere laag. Alle drie anders dan massief goud."),
            ("Waarom RVS met goudlaag langer mooi blijft", "Onze RVS sieraden hebben een duurzame goudlaag op robuust 316L staal: geen koper dat doorkomt en geen groene huid."),
            ("Veelgestelde vragen", "Verkleurt gold plated? Op den duur ja. Is RVS beter? Voor dagelijks dragen wel: het verkleurt niet."),
        ],
        "cta_text": "Bekijk onze RVS gouden sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Waarom worden zilveren sieraden zwart? (en wat je eraan doet)",
        "tags": "zilveren sieraden, zwart, aanslag, oxidatie, schoonmaken, rvs",
        "keywords": ["zilveren sieraden zwart geworden", "sieraden zwart geworden", "zwarte aanslag sieraden"],
        "outline": [
            ("Waarom zilver zwart wordt", "Zilver reageert met zwavel in lucht, zweet en cosmetica. Dat heet oxidatie en geeft een donkere aanslag."),
            ("Is het slecht voor je sieraad?", "Nee, het is oppervlakkig en gaat eraf. Maar het oogt dof en vraagt onderhoud."),
            ("Zo poets je zwart geworden zilver", "Gebruik een zilverpoetsdoekje of lauw water met mild afwasmiddel. Vermijd schuurmiddel."),
            ("Waarom RVS niet zwart wordt", "Roestvrij staal oxideert niet zoals zilver. Het houdt zijn kleur zonder poetsen, ook bij dagelijks dragen."),
            ("Veelgestelde vragen", "Kan ik zwart zilver voorkomen? Droog bewaren en afdoen bij sporten. Heeft RVS dit ook? Nee."),
        ],
        "cta_text": "Bekijk onze onderhoudsvrije RVS sieraden",
        "cta_url": "/collections/alle-sieraden",
    },
    {
        "title": "Wat is 316L roestvrij staal? (en waarom het zo geschikt is voor sieraden)",
        "tags": "316l, roestvrij staal, rvs, chirurgisch staal, hypoallergeen, materiaal",
        "keywords": ["316l roestvrij staal sieraden", "316l sieraden", "wat is 316l staal"],
        "outline": [
            ("Wat 316L roestvrij staal is", "316L is een hoogwaardige staalsoort, ook wel chirurgisch staal genoemd, met chroom en molybdeen voor extra bescherming."),
            ("Waarom 316L beter is dan gewoon RVS", "Het extra molybdeen maakt 316L beter bestand tegen zout, zweet en water dan standaard 304-staal."),
            ("Waterproof, nikkelvrij en hypoallergeen", "316L verkleurt niet, roest niet en geeft nauwelijks nikkel af: ideaal voor de gevoelige huid en dagelijks dragen."),
            ("Waarom wij voor 316L kiezen", "Al onze sieraden zijn van 316L, zodat je ze zorgeloos kunt dragen in de douche, het zwembad en de zee."),
            ("Veelgestelde vragen", "Is 316L echt waterproof? Ja. Verkleurt het? Nee. Geschikt bij allergie? Ja, het is hypoallergeen."),
        ],
        "cta_text": "Ontdek onze 316L RVS collectie",
        "cta_url": "/collections/alle-sieraden",
    },
    {'title': 'Klavertje vier sieraden — de betekenis van geluk om je hals',
     'keywords': ['klavertje vier ketting', 'klaver sieraden betekenis', 'geluksketting'],
     'tags': 'klavertje vier, klaver, geluk, betekenis, ketting, cadeau',
     'cta_text': 'Ontdek onze gelukssieraden',
     'cta_url': '/collections/kettingen',
     'outline': [('De betekenis van het klavertje vier',
                  'Elk blaadje staat voor iets: hoop, geloof, liefde en geluk. Al eeuwen een symbool '
                  'dat je bij je draagt voor voorspoed.'),
                 ('Waarom klaver sieraden zo populair zijn',
                  'Van catwalks tot straatbeeld: het klavermotief is tijdloos, subtiel en past bij '
                  'elke stijl.'),
                 ('Klaver ketting, armband of oorbellen?',
                  'Een ketting valt het meest op, een armband is subtieler en oorbellen maken de look '
                  'af. Combineren kan ook.'),
                 ('Het perfecte gelukscadeau',
                  'Een klavertje vier zegt meer dan woorden: ideaal voor een examen, nieuwe baan, '
                  'verjaardag of gewoon omdat je iemand geluk gunt.'),
                 ('Veelgestelde vragen',
                  'Verkleurt een RVS klaver ketting? Nee. Mag je ermee douchen? Ja, gewoon '
                  'aanhouden.')]},
    {'title': 'Kettingen layeren — welke lengtes combineer je?',
     'keywords': ['kettingen layeren', 'kettingen combineren lengte', 'layering kettingen'],
     'tags': 'layering, kettingen, combineren, stylen, lengte',
     'cta_text': 'Shop kettingen om te layeren',
     'cta_url': '/collections/kettingen',
     'outline': [('Wat is layering?',
                  'Meerdere kettingen in verschillende lengtes over elkaar dragen voor een gelaagde, '
                  'moeiteloze look.'),
                 ('De gouden regel: 5 cm verschil',
                  'Kies lengtes die minimaal 5 centimeter verschillen, bijvoorbeeld 40, 45 en 50 cm, '
                  'zodat ze niet in elkaar draaien.'),
                 ('Combineer dun met statement',
                  'Een fijne schakel, een hanger en één opvallende schakelketting: drie lagen is de '
                  'sweet spot.'),
                 ('Zo voorkom je klitten',
                  'Kies kettingen met verschillende schakeltypes en sluit ze apart; RVS schakels '
                  'klitten minder snel dan fijne zilveren kettinkjes.'),
                 ('Veelgestelde vragen',
                  'Hoeveel kettingen kun je layeren? Twee tot drie is ideaal. Mag goud met zilver? Ja, '
                  'mixed metals is juist een trend.')]},
    {'title': 'Schakelketting stylen — van casual tot chic',
     'keywords': ['schakelketting stylen', 'schakelketting dames', 'chunky ketting combineren'],
     'tags': 'schakelketting, stylen, chunky, trend, ketting',
     'cta_text': 'Bekijk onze schakelkettingen',
     'cta_url': '/collections/kettingen',
     'outline': [('Waarom de schakelketting een klassieker is',
                  "Van jaren '90 icoon tot moderne must-have: de schakelketting geeft elke outfit "
                  'direct karakter.'),
                 ('Casual: op een T-shirt of blouse',
                  'Eén gouden schakelketting op een wit shirt is de makkelijkste chique look die er '
                  'bestaat.'),
                 ('Chic: layeren met fijne kettingen',
                  'Combineer een chunky schakel met een fijn kettinkje met hanger voor contrast.'),
                 ('Welke dikte past bij jou?',
                  'Fijne schakels ogen subtiel en elegant, brede schakels maken een statement. Kies '
                  'wat bij je stijl en gezichtsvorm past.'),
                 ('Veelgestelde vragen',
                  'Verkleurt een RVS schakelketting? Nee, ook niet bij dagelijks dragen. Kan hij nat '
                  'worden? Ja, waterproof.')]},
    {'title': "Statement ring dragen — zo maak je 'm het middelpunt",
     'keywords': ['statement ring goud', 'statement ring dragen', 'grote ring stylen'],
     'tags': 'statement ring, ringen, stylen, goud, trend',
     'cta_text': 'Ontdek onze statement ringen',
     'cta_url': '/collections/ringen',
     'outline': [('Wat maakt een ring een statement ring?',
                  'Groot, opvallend en met karakter: een statement ring trekt de aandacht naar je '
                  'handen.'),
                 ('Eén held, rustige rest',
                  'Draag je statement ring solo of met hooguit één fijne ring per hand, zodat hij echt '
                  'opvalt.'),
                 ('Aan welke vinger?',
                  'De wijs- of middelvinger geeft het meeste effect; de pink is de moderne, gedurfde '
                  'keuze.'),
                 ('Statement ring bij elke gelegenheid',
                  'Op kantoor subtiel met een minimalistische outfit, in het weekend maximaal met '
                  'kleur en print.'),
                 ('Veelgestelde vragen',
                  'Verkleurt een gouden RVS ring? Nee. Word je vinger groen? Niet bij 316L roestvrij '
                  'staal.')]},
    {'title': 'Earcuff dragen — zo zit hij vast (zonder gaatje)',
     'keywords': ['earcuff dragen', 'earcuff goud', 'earcuff zonder gaatje'],
     'tags': 'earcuff, oorbellen, zonder gaatje, trend, goud',
     'cta_text': 'Shop earcuffs en oorbellen',
     'cta_url': '/collections/oorbellen',
     'outline': [('Wat is een earcuff?',
                  'Een oorsieraad dat je om de rand van je oor klemt: geen gaatje nodig, wel direct '
                  'effect.'),
                 ('Zo zet je hem goed vast',
                  'Schuif de cuff over het dunste deel van je oorrand en schuif hem daarna iets naar '
                  'beneden waar het kraakbeen dikker is.'),
                 ('Doet een earcuff pijn?',
                  'Nee, als hij goed zit voel je hem nauwelijks. Knijp hem heel licht aan voor meer '
                  'grip, nooit te strak.'),
                 ('De curated ear: combineren met oorbellen',
                  'Mix een earcuff met een hoop en een stud voor het populaire gelaagde oor, ook met '
                  'maar één gaatje.'),
                 ('Veelgestelde vragen',
                  'Valt een earcuff eraf? Zelden, als hij goed geplaatst is. Kan iedereen hem dragen? '
                  'Ja, gaatje of niet.')]},
    {'title': 'Ear stack samenstellen — meerdere oorbellen combineren',
     'keywords': ['ear stack', 'meerdere oorbellen combineren', 'oorbellen stapelen'],
     'tags': 'ear stack, curated ear, oorbellen, combineren, trend',
     'cta_text': 'Bekijk onze oorbellen',
     'cta_url': '/collections/oorbellen',
     'outline': [('Wat is een ear stack?',
                  'Meerdere oorbellen per oor die samen één doordachte look vormen: van studs tot '
                  'hoops en cuffs.'),
                 ('Begin met een basis',
                  'Kies één blikvanger, bijvoorbeeld een middelgrote hoop, en bouw daaromheen met '
                  'kleinere studs.'),
                 ('Mix vormen, houd één kleur aan',
                  'Hartjes, balletjes en ringetjes mogen door elkaar; in één metaalkleur blijft het '
                  'geheel rustig.'),
                 ('Ook met één of twee gaatjes',
                  'Met earcuffs creëer je een volle stack zonder extra gaatjes te hoeven schieten.'),
                 ('Veelgestelde vragen',
                  'Hoeveel oorbellen per oor? Twee tot vier oogt het mooist. Kun je ermee slapen? '
                  'Liever niet met grote hoops.')]},
    {'title': 'Sieraden en zonnebrandcrème — kan dat samen?',
     'keywords': ['sieraden zonnebrandcreme', 'sieraden zomer verkleuren', 'sieraden op het strand'],
     'tags': 'zomer, zonnebrand, waterproof, verzorging, strand',
     'cta_text': 'Shop zomerproof sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Waarom zonnebrand en sieraden lastig samengaan',
                  'Crème bevat oliën en filters die op sieraden een dof laagje achterlaten en bij '
                  'sommige metalen verkleuring versnellen.'),
                 ('RVS heeft er geen last van',
                  '316L roestvrij staal reageert niet met zonnebrandcrème: hooguit wordt het even dof '
                  'van de vette laag.'),
                 ('Zo houd je ze stralend',
                  'Smeer eerst, laat intrekken en doe daarna je sieraden om. Doffe plekken? Even '
                  'afspoelen en droogwrijven.'),
                 ('Wat je beter thuislaat',
                  'Gold plated en goedkope legeringen verkleuren wel door crème, chloor en zout: die '
                  'laat je op strandvakantie thuis.'),
                 ('Veelgestelde vragen',
                  'Mag je met RVS sieraden de zee in? Ja. En het zwembad? Ook, chloor doet 316L '
                  'niets.')]},
    {'title': 'Sieraden dragen tijdens het sporten — verstandig of niet?',
     'keywords': ['sieraden sporten', 'sieraden zweet verkleuren', 'sieraden gym'],
     'tags': 'sport, gym, zweet, waterproof, rvs',
     'cta_text': 'Bekijk onze sportproof sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Zweet en sieraden: wat gebeurt er?',
                  'Zweet is licht zuur en zout: funest voor gold plated en goedkope metalen, maar 316L '
                  'RVS kan er prima tegen.'),
                 ('Welke sieraden kun je aanhouden?',
                  'Fijne kettingen, kleine studs en gladde ringen zitten niet in de weg en kunnen '
                  'gewoon mee de gym in.'),
                 ('Wat doe je beter af?',
                  'Grote hoops, bedelarmbanden en ringen met uitstekende details: die blijven haken '
                  'achter apparaten en kleding.'),
                 ('Na het sporten: 10 seconden onderhoud',
                  'Spoel je sieraden kort af of veeg ze droog, dan blijft ook de glans op lange '
                  'termijn perfect.'),
                 ('Veelgestelde vragen',
                  'Verkleurt RVS door zweet? Nee. Mag een ketting mee onder de douche na de training? '
                  'Ja.')]},
    {'title': 'Goud of zilver — welke kleur past bij jouw huidtint?',
     'keywords': ['goud of zilver huidtint',
                  'welke sieraden passen bij mij',
                  'warme koele ondertoon sieraden'],
     'tags': 'goud, zilver, huidtint, ondertoon, stijladvies',
     'cta_text': 'Shop goud en zilver',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('De ondertoon-check',
                  'Kijk naar de aderen op je pols: groenig betekent een warme ondertoon, blauwig een '
                  'koele, allebei is neutraal.'),
                 ('Warme ondertoon: goud',
                  'Warme huidtinten lichten op bij goudkleurige sieraden: het geeft een zachte gloed.'),
                 ('Koele ondertoon: zilver',
                  'Koele huidtinten komen het best tot hun recht bij zilverkleur: fris en helder.'),
                 ('Neutraal? Mix gerust',
                  'Met een neutrale ondertoon staat alles, en mixed metals dragen is bovendien '
                  'helemaal van nu.'),
                 ('Veelgestelde vragen',
                  'Is er een verkeerde keuze? Nee, draag wat jij mooi vindt. Verkleuren beide kleuren '
                  'RVS niet? Klopt, allebei kleurvast.')]},
    {'title': 'Goud en zilver combineren — mag dat? (mixed metals gids)',
     'keywords': ['goud en zilver combineren', 'mixed metals sieraden', 'twee kleuren sieraden dragen'],
     'tags': 'mixed metals, goud, zilver, combineren, trend',
     'cta_text': 'Ontdek onze collectie in goud en zilver',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('De oude regel is dood',
                  "Vroeger 'mocht' je metalen niet mengen, nu is mixed metals juist een teken van "
                  'stijl.'),
                 ('Kies een hoofdkleur',
                  'Laat één kleur domineren (bijvoorbeeld 70% goud) en gebruik de ander als accent, zo '
                  'oogt het bewust.'),
                 ('Bicolor sieraden als bruggetje',
                  'Een sieraad met beide kleuren erin verbindt je gouden en zilveren items '
                  'moeiteloos.'),
                 ('Herhaal de mix',
                  'Draag je een gemixte ketting? Herhaal het dan ook in je ringen of oorbellen, dan '
                  'klopt het plaatje.'),
                 ('Veelgestelde vragen',
                  'Staat mixed metals bij elke huidtint? Ja. Kunnen beide kleuren tegen water? Bij RVS '
                  'wel.')]},
    {'title': 'Wat is PVD coating? (en waarom je sieraad zo lang goud blijft)',
     'keywords': ['pvd coating sieraden', 'pvd goud', 'pvd vs gold plated'],
     'tags': 'pvd, coating, goud, kwaliteit, materiaal',
     'cta_text': 'Shop PVD-gecoate sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('PVD in gewone taal',
                  "Physical Vapor Deposition: de goudlaag wordt in een vacuüm op het staal 'gedampt' "
                  'en hecht op moleculair niveau.'),
                 ('Waarom het zoveel sterker is dan gold plated',
                  'Een PVD-laag is tot tien keer harder en slijtvaster dan traditioneel galvanisch '
                  'verguldsel.'),
                 ('Waterproof en kleurvast',
                  'Douchen, zwemmen, sporten: een PVD-coating op 316L staal laat niet los en verkleurt '
                  'niet.'),
                 ('Hoe je PVD herkent',
                  "Betaalbare sieraden die expliciet 'waterproof' en 'verkleurt niet' beloven, zijn "
                  'vrijwel altijd PVD op RVS.'),
                 ('Veelgestelde vragen',
                  'Slijt PVD ooit? Bij intensief dagelijks dragen pas na jaren. Is het nikkelvrij? Ja, '
                  'veilig voor de gevoelige huid.')]},
    {'title': 'Action en Zeeman sieraden — waarom verkleuren ze zo snel?',
     'keywords': ['action sieraden verkleuren',
                  'goedkope sieraden verkleuren',
                  'zeeman sieraden kwaliteit'],
     'tags': 'action, zeeman, goedkoop, verkleuren, vergelijking',
     'cta_text': 'Bekijk betaalbare sieraden die wél mooi blijven',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Waarom budget-sieraden snel verkleuren',
                  'Ze zijn vaak gemaakt van legeringen met koper of zink en een flinterdun kleurlaagje '
                  'dat binnen weken slijt.'),
                 ('Groene vingers en jeukende oren',
                  'Koper oxideert op je huid (groene vinger) en nikkel in goedkope legeringen '
                  'veroorzaakt irritatie.'),
                 ('Goedkoop is uiteindelijk duurkoop',
                  'Drie keer een ketting van 4 euro vervangen kost meer dan één RVS ketting die jaren '
                  'meegaat.'),
                 ('Het betaalbare alternatief',
                  '316L RVS sieraden kosten net iets meer, maar verkleuren niet, roesten niet en zijn '
                  'nikkelvrij.'),
                 ('Veelgestelde vragen',
                  'Kun je budget-sieraden waterproof maken? Nee, een laklaagje helpt hooguit even. Wat '
                  'is het verschil met RVS? Massief kleurvast materiaal in plaats van een laagje.')]},
    {'title': 'Hoe weet je of een sieraad nikkelvrij is?',
     'keywords': ['nikkelvrij sieraad herkennen',
                  'nikkelvrije sieraden',
                  'nikkel allergie sieraden check'],
     'tags': 'nikkelvrij, allergie, gevoelige huid, hypoallergeen, check',
     'cta_text': 'Shop nikkelvrije RVS sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Waarom nikkel het probleem is',
                  "Zo'n 10 tot 15 procent van de vrouwen reageert allergisch op nikkel: jeuk, rode "
                  'huid en blaasjes.'),
                 ('Check het materiaal, niet de belofte',
                  "Zoek naar 316L roestvrij staal, titanium of echt goud; 'hypoallergeen' zonder "
                  'materiaalvermelding zegt weinig.'),
                 ('De signalen van nikkel',
                  'Jeuk binnen een paar uur, een donkere afdruk op de huid of een metaalgeur op je '
                  'vingers verraden goedkope legeringen.'),
                 ('Waarom 316L veilig is',
                  'In 316L zit nikkel chemisch gebonden in het staal, waardoor het praktisch niet '
                  'vrijkomt op je huid: veilig, ook bij allergie.'),
                 ('Veelgestelde vragen',
                  'Is RVS 100% nikkelvrij? Het geeft vrijwel geen nikkel af en valt ruim binnen de '
                  'EU-norm. Kan ik er dag en nacht mee? Ja.')]},
    {'title': 'Ketting in de knoop — zo krijg je hem los zonder schade',
     'keywords': ['ketting knoop eruit halen', 'ketting klit oplossen', 'ketting in de war'],
     'tags': 'knoop, klit, onderhoud, tips, ketting',
     'cta_text': 'Bekijk onze kettingen',
     'cta_url': '/collections/kettingen',
     'outline': [('Stap 1: leg de ketting plat neer',
                  'Werk op een gladde, lichte ondergrond en open het slotje: dat geeft de knoop '
                  'ruimte.'),
                 ('Stap 2: gebruik twee naalden',
                  'Steek twee speldjes of naalden in het hart van de knoop en beweeg ze zachtjes uit '
                  'elkaar: nooit trekken.'),
                 ('Hardnekkige knoop? Babyolie of talkpoeder',
                  'Een druppeltje babyolie laat de schakels langs elkaar glijden; daarna afspoelen met '
                  'lauw water en drogen.'),
                 ('Zo voorkom je knopen voortaan',
                  'Sluit kettingen voor het opbergen, hang ze op of bewaar elke ketting apart in een '
                  'zakje.'),
                 ('Veelgestelde vragen',
                  'Kan olie kwaad bij RVS? Nee, gewoon afspoelen. Wat bij een fijn kettinkje? Extra '
                  'geduld en licht werken, nooit forceren.')]},
    {'title': 'Bedelarmband samenstellen — kies bedels met betekenis',
     'keywords': ['bedelarmband samenstellen', 'bedels betekenis', 'charm armband maken'],
     'tags': 'bedels, charms, bedelarmband, betekenis, personaliseren',
     'cta_text': 'Ontdek onze bedels en charms',
     'cta_url': '/collections/charms',
     'outline': [('Begin met de basisarmband',
                  'Kies een stevige RVS schakelarmband als basis: die kan het gewicht van bedels aan '
                  'en verkleurt niet.'),
                 ('Kies bedels die iets vertellen',
                  'Een hartje voor liefde, een klavertje voor geluk, een letter voor een dierbare: zo '
                  'wordt je armband een verhaal.'),
                 ('Balans: 3 tot 5 bedels',
                  'Verdeel bedels gelijkmatig en houd ruimte over; een half gevulde armband oogt '
                  'bewuster dan een overvolle.'),
                 ('Het ultieme personaliseerbare cadeau',
                  'Geef een armband met één betekenisvolle bedel en laat de ontvanger hem zelf verder '
                  'aanvullen.'),
                 ('Veelgestelde vragen',
                  'Kunnen bedels tegen water? RVS bedels wel. Kun je later bedels bijkopen? Ja, dat is '
                  'juist het idee.')]},
    {'title': 'Sieraden cadeau onder de €25 — de mooiste ideeën',
     'keywords': ['cadeau onder 25 euro vrouw',
                  'goedkoop sieraden cadeau',
                  'klein cadeautje voor haar'],
     'tags': 'cadeau, budget, onder 25 euro, cadeautip, betaalbaar',
     'cta_text': 'Shop cadeaus onder de €25',
     'cta_url': '/collections/cadeau-ideeen',
     'outline': [('Klein budget, groot effect',
                  'Een goed gekozen sieraad voelt persoonlijk en luxe, ook onder de 25 euro: het gaat '
                  'om de betekenis.'),
                 ('Voor de minimalist',
                  'Fijne gouden studs of een subtiele ring: tijdloos, dagelijks draagbaar en altijd '
                  'raak.'),
                 ('Voor de trendsetter',
                  'Een earcuff, klaverketting of chunky ring sluit aan op de trends van dit moment.'),
                 ('Maak het persoonlijk',
                  'Kies een symbool dat past: een hartje, geluksklaver of geboortesteenkleur maakt het '
                  "cadeau van 'leuk' naar 'voor mij'."),
                 ('Veelgestelde vragen',
                  'Blijft een betaalbaar RVS sieraad mooi? Ja, het verkleurt niet. Zit er een '
                  'cadeauverpakking bij? Check de productpagina.')]},
    {'title': 'Old money sieraden stijl — tijdloze elegantie zonder de prijs',
     'keywords': ['old money sieraden', 'old money stijl accessoires', 'tijdloze sieraden'],
     'tags': 'old money, stijl, elegant, tijdloos, trend',
     'cta_text': 'Shop tijdloze klassiekers',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Wat is de old money look?',
                  'Stille luxe: verfijnd, tijdloos en nooit schreeuwerig. Denk kleine gouden hoops, '
                  'een fijne ketting en één elegante ring.'),
                 ('Minder is meer',
                  'Maximaal drie subtiele sieraden tegelijk: de kracht zit in eenvoud en kwaliteit van '
                  'afwerking.'),
                 ('De old money essentials',
                  'Kleine hoops, een dunne schakelarmband, een zegelring en een fijne ketting: daarmee '
                  'bouw je elke look.'),
                 ('Duur ogen zonder duur te zijn',
                  'Gouden RVS sieraden hebben dezelfde warme glans als echt goud, maar dan zonder het '
                  'prijskaartje en zonder verkleuren.'),
                 ('Veelgestelde vragen',
                  'Welke kleur past bij old money? Vooral goud. Kan het naar kantoor? Juist: het ís de '
                  'kantoorstijl.')]},
    {'title': 'Sieraden in de sauna — kan dat kwaad?',
     'keywords': ['sieraden sauna', 'sieraden afdoen sauna', 'rvs sieraden hitte'],
     'tags': 'sauna, hitte, waterproof, verzorging, tips',
     'cta_text': 'Bekijk onze RVS sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Het echte risico: hitte op je huid',
                  'Metaal warmt in de sauna snel op en kan onaangenaam heet worden op de huid: dáárom '
                  'doe je sieraden af, niet vanwege schade.'),
                 ('Kan RVS tegen de sauna?',
                  'Ja, 316L roestvrij staal kan probleemloos tegen hitte, stoom en vocht: het roest of '
                  'verkleurt er niet van.'),
                 ('Wat je écht moet afdoen',
                  'Gold plated sieraden en sieraden met steentjes op lijm: hitte versnelt slijtage van '
                  'laagjes en lijm.'),
                 ('Praktische saunaroutine',
                  'Doe sieraden af in de kleedkamer en bewaar ze in een klein zakje in je locker, dan '
                  'raak je niets kwijt.'),
                 ('Veelgestelde vragen',
                  'Vergeten af te doen? Geen paniek, spoel ze na met lauw water. Geldt dit ook voor '
                  'het stoombad? Zelfde verhaal.')]},
    {'title': 'Wat zeg je met een sieraad? De betekenis achter het cadeau',
     'keywords': ['sieraad cadeau betekenis', 'ketting geven betekenis', 'wat betekent sieraden geven'],
     'tags': 'betekenis, cadeau, symboliek, liefde, vriendschap',
     'cta_text': 'Vind een cadeau met betekenis',
     'cta_url': '/collections/cadeau-ideeen',
     'outline': [('Waarom een sieraad meer zegt dan woorden',
                  'Een sieraad wordt elke dag gedragen en gezien: je geeft letterlijk iets blijvends '
                  'mee.'),
                 ('De symboliek per sieraad',
                  'Een ketting draag je bij je hart (liefde), een armband staat voor verbondenheid en '
                  'een ring voor belofte.'),
                 ('Symbolen en hun boodschap',
                  'Hartje = liefde, klavertje = geluk, zonnetje = positiviteit, letter = persoonlijke '
                  'band.'),
                 ('Voor elke relatie het juiste cadeau',
                  'Voor je vriendin, moeder, zus of beste vriendin: kies het symbool dat jullie band '
                  'vangt.'),
                 ('Veelgestelde vragen',
                  'Is een sieraad te persoonlijk als eerste cadeau? Een subtiel sieraad niet. Wat als '
                  'het niet past? Kettingen en armbanden zijn maatloos veilig.')]},
    {'title': 'Festival sieraden — wat draag je (en wat laat je thuis)?',
     'keywords': ['festival sieraden', 'sieraden festival outfit', 'waterproof sieraden festival'],
     'tags': 'festival, zomer, waterproof, outfit, tips',
     'cta_text': 'Shop festivalproof sieraden',
     'cta_url': '/collections/alle-sieraden',
     'outline': [('Festivalproof = waterproof',
                  'Zon, zweet, regen en glitter: kies sieraden die daar tegen kunnen, zoals 316L RVS '
                  'dat niet verkleurt.'),
                 ('Meer is meer (voor één keer)',
                  'Op een festival mag het: stapel armbanden, layer kettingen en maak je ear stack '
                  'compleet.'),
                 ('Wat je thuislaat',
                  'Dure of dierbare sieraden en alles met kleine steentjes: verlies op een '
                  'festivalterrein is definitief.'),
                 ('Praktische tips',
                  "Draag ringen iets strakker (vingers slinken bij warmte 's avonds), en check slotjes "
                  'voordat je gaat crowdsurfen.'),
                 ('Veelgestelde vragen',
                  'Regen en modder? RVS overleeft alles, thuis even afspoelen. Glitter eraf krijgen? '
                  'Lauw water en een zachte doek.')]},
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
    article = {
        "title": topic["title"],
        "author": AUTHOR,
        "tags": topic["tags"],
        "body_html": body_html,
        "published": True,
    }
    # SEO meta description (metafield global.description_tag) indien aanwezig
    if topic.get("meta"):
        article["metafields"] = [{
            "namespace": "global",
            "key": "description_tag",
            "type": "single_line_text_field",
            "value": topic["meta"][:320],
        }]
    payload = {"article": article}
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
