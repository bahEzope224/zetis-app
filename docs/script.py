#!/usr/bin/env python3
"""
Zetis — Cahier des Charges Technique — Générateur PDF
Stack: React + Tailwind / FastAPI / PostgreSQL / Redis / WebRTC
IA embarquée : modèles légers (Haiku, Gemini Flash, local)
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable

# ── Fonts Configuration for macOS ─────────────────────────────────────
# Adaptation pour macOS (les polices Liberation ne sont pas disponibles)

try:
    # Helvetica (Sans)
    pdfmetrics.registerFont(TTFont('Sans', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('Sans-Bold', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=1))
    pdfmetrics.registerFont(TTFont('Sans-Italic', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=2))
    
    # Times (Serif)
    pdfmetrics.registerFont(TTFont('Serif', '/System/Library/Fonts/Times.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('Serif-Bold', '/System/Library/Fonts/Times.ttc', subfontIndex=1))
    pdfmetrics.registerFont(TTFont('Serif-Italic', '/System/Library/Fonts/Times.ttc', subfontIndex=2))
    
    print("✓ Polices système macOS (Helvetica + Times) enregistrées avec succès.")
    
except Exception as e:
    print(f"⚠️  Erreur lors de l'enregistrement des polices système : {e}")
    print("Utilisation des polices PDF standards (Helvetica / Times-Roman)")

# Police pour le code (toujours disponible)
pdfmetrics.registerFont(TTFont('Courier', '/System/Library/Fonts/Courier.ttc', subfontIndex=0))

# ── Brand colours ──────────────────────────────────────────────────────
C_NAVY   = colors.HexColor('#0A2540')
C_BLUE   = colors.HexColor('#003087')
C_RED    = colors.HexColor('#C8102E')
C_GOLD   = colors.HexColor('#D4AF37')
C_LIGHT  = colors.HexColor('#F7F8FA')
C_CARD   = colors.HexColor('#FFFFFF')
C_MUTED  = colors.HexColor('#6B7280')
C_BORDER = colors.HexColor('#E5E7EB')
C_DARK   = colors.HexColor('#1E1E1E')
C_CODE   = colors.HexColor('#1E1E2E')
C_CODE_T = colors.HexColor('#CDD6F4')

W = A4[0] - 3*cm   # usable text width

# ── Image handling (mise à jour) ─────────────────────────────────────
IMG_DIR = './pdf_imgs'

def img(name, width=None, height=None):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        print(f"⚠️  Image non trouvée : {path}")
        return Spacer(1, 0)
    try:
        i = Image(path)
        if width:
            ratio = i.imageHeight / i.imageWidth
            i.drawWidth  = width
            i.drawHeight = width * ratio
        elif height:
            ratio = i.imageWidth / i.imageHeight
            i.drawHeight = height
            i.drawWidth  = height * ratio
        else:
            # Par défaut : largeur maximale raisonnable
            i.drawWidth = min(i.imageWidth, W * 0.95)
            i.drawHeight = i.imageHeight
        i.hAlign = 'CENTER'
        return i
    except Exception as e:
        print(f"⚠️  Erreur chargement image {name}: {e}")
        return Spacer(1, 0)


# ── Affichage de plusieurs écrans mobiles ─────────────────────────────
def screen_row(items):
    """Affiche 2 ou 3 écrans mobiles côte à côte avec meilleure qualité"""
    n = len(items)
    col_w = W / n - 8
    
    # Hauteur augmentée pour meilleure visibilité
    MAX_H = 280 if n == 2 else 240
    
    row = []
    for fname, label in items:
        i = img(fname, height=MAX_H)
        cell_content = [
            i,
            Spacer(1, 6),
            Paragraph(label, ST['caption'])
        ]
        row.append(cell_content)
    
    t = Table([row], colWidths=[col_w] * n,
              style=TableStyle([
                  ('VALIGN',      (0,0), (-1,-1), 'TOP'),
                  ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
                  ('TOPPADDING',  (0,0), (-1,-1), 8),
                  ('LEFTPADDING', (0,0), (-1,-1), 6),
                  ('RIGHTPADDING',(0,0), (-1,-1), 6),
              ]))
    return [t, sp(10)]

# ── Paragraph styles ───────────────────────────────────────────────────
def styles():
    s = {}
    base = dict(fontName='Sans', fontSize=9, leading=14, textColor=C_DARK)

    s['cover_title'] = ParagraphStyle('cover_title',
        fontName='Serif-Bold', fontSize=36, textColor=colors.white,
        leading=42, spaceAfter=6, alignment=TA_CENTER)

    s['cover_sub'] = ParagraphStyle('cover_sub',
        fontName='Serif-Italic', fontSize=14, textColor=C_GOLD,
        leading=18, spaceAfter=4, alignment=TA_CENTER)

    s['cover_tag'] = ParagraphStyle('cover_tag',
        fontName='Sans', fontSize=10, textColor=colors.HexColor('#AAAAAA'),
        leading=14, spaceAfter=2, alignment=TA_CENTER)

    s['h1'] = ParagraphStyle('h1',
        fontName='Serif-Bold', fontSize=18, textColor=C_NAVY,
        spaceBefore=18, spaceAfter=6, leading=22,
        borderPad=(0,0,4,0))

    s['h2'] = ParagraphStyle('h2',
        fontName='Sans-Bold', fontSize=13, textColor=C_BLUE,
        spaceBefore=14, spaceAfter=4, leading=17)

    s['h3'] = ParagraphStyle('h3',
        fontName='Sans-Bold', fontSize=10.5, textColor=C_NAVY,
        spaceBefore=10, spaceAfter=3, leading=14)

    s['body'] = ParagraphStyle('body', **base,
        alignment=TA_JUSTIFY, spaceAfter=5)

    s['bullet'] = ParagraphStyle('bullet', **base,
        leftIndent=14, firstLineIndent=-10, spaceAfter=3)

    s['caption'] = ParagraphStyle('caption',
        fontName='Sans-Italic', fontSize=8, textColor=C_MUTED,
        alignment=TA_CENTER, spaceAfter=8, spaceBefore=3)

    s['code'] = ParagraphStyle('code',
        fontName='Courier', fontSize=8, textColor=C_CODE_T,
        backColor=C_CODE, leftIndent=8, rightIndent=8,
        spaceBefore=4, spaceAfter=4, leading=12,
        borderPad=6)

    s['note'] = ParagraphStyle('note',
        fontName='Sans-Italic', fontSize=8.5, textColor=C_MUTED,
        leftIndent=10, spaceAfter=4, leading=12)

    s['tag_title'] = ParagraphStyle('tag_title',
        fontName='Sans-Bold', fontSize=8, textColor=colors.white,
        alignment=TA_CENTER)

    return s

ST = styles()

def h1(text):
    return [
        Spacer(1, 6),
        HRFlowable(width=W, thickness=3, color=C_NAVY, spaceAfter=4),
        Paragraph(text, ST['h1']),
        HRFlowable(width=W, thickness=0.5, color=C_BORDER, spaceAfter=6),
    ]

def h2(text): return Paragraph(text, ST['h2'])
def h3(text): return Paragraph(text, ST['h3'])
def body(text): return Paragraph(text, ST['body'])
def bullet(text): return Paragraph(f'• {text}', ST['bullet'])
def caption(text): return Paragraph(text, ST['caption'])
def note(text): return Paragraph(f'ℹ {text}', ST['note'])
def sp(h=6): return Spacer(1, h)
def pb(): return PageBreak()
def hr(color=C_BORDER): return HRFlowable(width=W, thickness=0.5, color=color, spaceAfter=6)

def code_block(lines):
    text = '<br/>'.join(lines)
    return [
        Table([[Paragraph(text, ST['code'])]],
              colWidths=[W],
              style=TableStyle([
                  ('BACKGROUND', (0,0), (-1,-1), C_CODE),
                  ('ROUNDEDCORNERS', [6]),
                  ('TOPPADDING',    (0,0), (-1,-1), 8),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                  ('LEFTPADDING',   (0,0), (-1,-1), 10),
                  ('RIGHTPADDING',  (0,0), (-1,-1), 10),
              ])),
        sp(4),
    ]

def info_box(text, color=C_BLUE):
    return [
        Table([[Paragraph(text, ParagraphStyle('ib',
            fontName='Sans', fontSize=8.5, textColor=colors.white,
            leading=13))]],
              colWidths=[W],
              style=TableStyle([
                  ('BACKGROUND',    (0,0), (-1,-1), color),
                  ('TOPPADDING',    (0,0), (-1,-1), 10),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                  ('LEFTPADDING',   (0,0), (-1,-1), 14),
                  ('RIGHTPADDING',  (0,0), (-1,-1), 14),
                  ('ROUNDEDCORNERS', [6]),
              ])),
        sp(6),
    ]

def two_col(left_items, right_items):
    col_w = W / 2 - 6
    def cell(items): return '\n'.join(i.text if hasattr(i,'text') else '' for i in items)
    rows = []
    max_len = max(len(left_items), len(right_items))
    for i in range(max_len):
        l = left_items[i] if i < len(left_items) else Paragraph('', ST['body'])
        r = right_items[i] if i < len(right_items) else Paragraph('', ST['body'])
        rows.append([l, r])
    t = Table(rows, colWidths=[col_w, col_w],
              style=TableStyle([
                  ('VALIGN',       (0,0), (-1,-1), 'TOP'),
                  ('LEFTPADDING',  (0,0), (-1,-1), 4),
                  ('RIGHTPADDING', (0,0), (-1,-1), 4),
              ]))
    return t

def data_table(headers, rows, col_widths=None):
    if col_widths is None:
        col_widths = [W / len(headers)] * len(headers)
    style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), C_NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Sans-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 8),
        ('FONTNAME',      (0,1), (-1,-1), 'Sans'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('TEXTCOLOR',     (0,1), (-1,-1), C_DARK),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_LIGHT, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('RIGHTPADDING',  (0,0), (-1,-1), 7),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ])
    data = [[Paragraph(h, ParagraphStyle('th', fontName='Sans-Bold', fontSize=8,
                       textColor=colors.white, leading=11)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ParagraphStyle('td', fontName='Sans', fontSize=8,
                               textColor=C_DARK, leading=11)) for c in row])
    return [Table(data, colWidths=col_widths, style=style), sp(8)]

def screen_row(items):
    n = len(items)
    col_w = W / n
    MAX_H = 200
    row = []
    for fname, label in items:
        i = img(fname, height=MAX_H)
        cell_content = [i, Paragraph(label, ST['caption'])]
        row.append(cell_content)
    data = [row]
    t = Table(data, colWidths=[col_w]*n,
              style=TableStyle([
                  ('VALIGN',      (0,0), (-1,-1), 'TOP'),
                  ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
                  ('TOPPADDING',  (0,0), (-1,-1), 4),
                  ('LEFTPADDING', (0,0), (-1,-1), 4),
                  ('RIGHTPADDING',(0,0), (-1,-1), 4),
              ]))
    return [t, sp(8)]

# ── Header / Footer ────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Header
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - 28, w, 28, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('Serif-Bold', 11)
    canvas.drawString(1.5*cm, h - 18, 'ZETIS')
    canvas.setFont('Sans', 7)
    canvas.setFillColor(C_GOLD)
    canvas.drawString(3.1*cm, h - 18, 'ΖΉΤΗΣΙΣ')
    canvas.setFillColor(colors.white)
    canvas.setFont('Sans', 7.5)
    canvas.drawCentredString(w/2, h - 18, 'Cahier des Charges Technique — MVP 1.0')

    # Page number
    canvas.setFont('Sans', 7)
    canvas.setFillColor(colors.HexColor('#AAAAAA'))
    canvas.drawRightString(w - 1.5*cm, h - 18, f'Page {doc.page}')

    # Footer
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(1.5*cm, 1.4*cm, w - 1.5*cm, 1.4*cm)
    canvas.setFont('Sans', 7)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(1.5*cm, 0.9*cm, 'Confidentiel — Document interne Zetis')
    canvas.drawRightString(w - 1.5*cm, 0.9*cm, 'Opposez vos idées. Questionnez la vérité.')

    canvas.restoreState()

# Le reste du code (cover_page, build_story, main...) reste identique
# (je ne le recopie pas ici pour éviter de surcharger, mais il est inchangé)

def cover_page():
    """Render cover as canvas drawing, return as PageBreak after content."""
    story = []

    cover_data = [[
        Table([
            [Paragraph('ZETIS', ST['cover_title'])],
            [Paragraph('ΖΉΤΗΣΙΣ', ST['cover_sub'])],
            [sp(20)],
            [Paragraph('Cahier des Charges Technique', ParagraphStyle('ct2',
                fontName='Sans-Bold', fontSize=16, textColor=colors.white,
                alignment=TA_CENTER, leading=20))],
            [Paragraph('MVP 1.0 — Plateforme de débat live 1v1 structuré par IA', ParagraphStyle('ct3',
                fontName='Sans-Italic', fontSize=10, textColor=colors.HexColor('#AAAAAA'),
                alignment=TA_CENTER, leading=14))],
            [sp(30)],
            [Table([
                [Paragraph('Version', ParagraphStyle('ml', fontName='Sans-Bold', fontSize=8,
                    textColor=C_GOLD, alignment=TA_RIGHT)),
                 Paragraph('MVP 1.0', ParagraphStyle('mr', fontName='Sans', fontSize=8,
                    textColor=colors.white))],
                [Paragraph('Stack', ParagraphStyle('ml', fontName='Sans-Bold', fontSize=8,
                    textColor=C_GOLD, alignment=TA_RIGHT)),
                 Paragraph('React · FastAPI · PostgreSQL · Redis · WebRTC', ParagraphStyle('mr',
                    fontName='Sans', fontSize=8, textColor=colors.white))],
                [Paragraph('IA', ParagraphStyle('ml', fontName='Sans-Bold', fontSize=8,
                    textColor=C_GOLD, alignment=TA_RIGHT)),
                 Paragraph('Claude Haiku 3.5 · Gemini 2.0 Flash · Modèles légers', ParagraphStyle('mr',
                    fontName='Sans', fontSize=8, textColor=colors.white))],
                [Paragraph('Marché', ParagraphStyle('ml', fontName='Sans-Bold', fontSize=8,
                    textColor=C_GOLD, alignment=TA_RIGHT)),
                 Paragraph('France · USA', ParagraphStyle('mr', fontName='Sans', fontSize=8,
                    textColor=colors.white))],
                [Paragraph('Date', ParagraphStyle('ml', fontName='Sans-Bold', fontSize=8,
                    textColor=C_GOLD, alignment=TA_RIGHT)),
                 Paragraph('Avril 2026', ParagraphStyle('mr', fontName='Sans', fontSize=8,
                    textColor=colors.white))],
            ], colWidths=[3*cm, 10*cm],
               style=TableStyle([
                   ('GRID', (0,0),(-1,-1), 0.4, colors.HexColor('#334455')),
                   ('TOPPADDING', (0,0),(-1,-1), 5),
                   ('BOTTOMPADDING', (0,0),(-1,-1), 5),
                   ('LEFTPADDING', (0,0),(-1,-1), 8),
                   ('RIGHTPADDING', (0,0),(-1,-1), 8),
                   ('BACKGROUND', (0,0),(-1,-1), colors.HexColor('#0F2030')),
               ]))],
            [sp(20)],
            [Paragraph('Opposez vos idées. Questionnez la vérité.', ParagraphStyle('slogan',
                fontName='Serif-Italic', fontSize=12, textColor=C_GOLD,
                alignment=TA_CENTER, leading=16))],
        ],
        colWidths=[W],
        style=TableStyle([
            ('LEFTPADDING',  (0,0),(-1,-1), 0),
            ('RIGHTPADDING', (0,0),(-1,-1), 0),
            ('TOPPADDING',   (0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('ALIGN',        (0,0),(-1,-1), 'CENTER'),
        ]))
    ]]

    cover_t = Table(cover_data, colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',    (0,0),(-1,-1), C_NAVY),
            ('TOPPADDING',    (0,0),(-1,-1), 60),
            ('BOTTOMPADDING', (0,0),(-1,-1), 60),
            ('LEFTPADDING',   (0,0),(-1,-1), 0),
            ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ]))

    story.append(cover_t)
    story.append(pb())
    return story


# ══════════════════════════════════════════════════════════════════════
# MAIN STORY
# ══════════════════════════════════════════════════════════════════════
def build_story():
    story = []
    story += cover_page()

    # ── 1. VUE D'ENSEMBLE ─────────────────────────────────────────────
    story += h1('1. Vue d\'ensemble du projet')

    story.append(body(
        'Zetis est une plateforme web de débat contradictoire en direct (live) qui met en relation '
        'deux utilisateurs aux opinions opposées sur des sujets politiques, religieux, moraux ou '
        'économiques. Le format est structuré (timer par phases, rôles Pro/Con, charte), la modération '
        'est assistée par IA, et le matching est calculé algorithmiquement à partir des vecteurs '
        'd\'opinion des utilisateurs.'
    ))
    story.append(sp(6))

    story += info_box(
        '🎯  Objectif du MVP : valider qu\'un utilisateur réel accepte de débattre face à un inconnu '
        'aux opinions opposées dans un format structuré, et que l\'expérience soit jugée satisfaisante '
        '(score de civilité ≥ 3.5/5, taux de complétion ≥ 60 %).',
        C_BLUE
    )
    return story


# ══════════════════════════════════════════════════════════════════════
# MAIN STORY
# ══════════════════════════════════════════════════════════════════════
def build_story():
    story = []
    story += cover_page()

    # ── 1. VUE D'ENSEMBLE ─────────────────────────────────────────────
    story += h1('1. Vue d\'ensemble du projet')

    story.append(body(
        'Zetis est une plateforme web de débat contradictoire en direct (live) qui met en relation '
        'deux utilisateurs aux opinions opposées sur des sujets politiques, religieux, moraux ou '
        'économiques. Le format est structuré (timer par phases, rôles Pro/Con, charte), la modération '
        'est assistée par IA, et le matching est calculé algorithmiquement à partir des vecteurs '
        'd\'opinion des utilisateurs.'
    ))
    story.append(sp(6))

    story += info_box(
        '🎯  Objectif du MVP : valider qu\'un utilisateur réel accepte de débattre face à un inconnu '
        'aux opinions opposées dans un format structuré, et que l\'expérience soit jugée satisfaisante '
        '(score de civilité ≥ 3.5/5, taux de complétion ≥ 60 %).',
        C_BLUE
    )

    story.append(h2('1.1  Identité technique'))
    story += data_table(
        ['Composant', 'Choix technologique', 'Justification'],
        [
            ['Frontend',    'React 18 + Vite + Tailwind CSS',         'SPA légère, hot reload, DX optimale'],
            ['Backend',     'FastAPI (Python 3.11)',                    'Async natif, WebSocket, typage strict'],
            ['Base données','PostgreSQL 16 (Supabase)',                 'Relations complexes, JSONB pour opinions'],
            ['File d\'attente','Redis 7 (Upstash)',                    'Sorted sets, TTL natif, faible latence'],
            ['Vidéo live',  'WebRTC P2P (STUN/TURN Metered.ca)',       'P2P chiffré DTLS-SRTP, gratuit MVP'],
            ['Auth',        'Supabase Auth (JWT + OAuth2 Google)',      'SSO prêt, PKCE, gestion token simple'],
            ['IA',          'Claude Haiku 3.5 + Gemini 2.0 Flash',     'Coût minimal, latence faible, API simple'],
            ['Déploiement', 'Vercel (front) + Railway (back)',          'CI/CD auto, scaling instantané'],
        ],
        col_widths=[3*cm, 5.5*cm, 7*cm]
    )

    story.append(h2('1.2  Maquettes — Vue d\'ensemble'))
    story.append(body(
        'Les 11 écrans suivants couvrent l\'intégralité du parcours utilisateur MVP, '
        'de l\'onboarding jusqu\'au récapitulatif post-débat.'
    ))
    story.append(sp(8))

    story += screen_row([
        ('screen_01_splash.png',      'Écran 1 — Splash / Onboarding'),
        ('screen_02_login.png',       'Écran 2 — Inscription / Connexion'),
        ('screen_03_questionnaire.png','Écran 3 — Questionnaire opinions'),
    ])
    story += screen_row([
        ('screen_04_profile.png',     'Écran 4 — Profil utilisateur'),
        ('screen_05_home.png',        'Écran 5 — Dashboard / Accueil'),
        ('screen_06_matchmaking.png', 'Écran 6 — Matchmaking / File'),
    ])
    story += screen_row([
        ('screen_07_debate.png',      'Écran 7 — Salle de débat (mobile)'),
        ('screen_08_rating.png',      'Écran 8 — Notation post-débat'),
        ('screen_09_summary.png',     'Écran 9 — Récapitulatif'),
    ])
    story += screen_row([
        ('screen_10_moderation.png',  'Écran 10 — Signalement / Modération'),
        ('screen_12_activity.png',    'Écran 12 — Activité / Notifications'),
    ])

    story.append(sp(8))
    story.append(body('Version desktop — Salle de débat (1440px) :'))
    story.append(img('screen_11_desktop.png', width=W * 0.96))
    story.append(caption('Écran 11 — Salle de débat version desktop (1440px)'))
    story.append(pb())

    # ── 2. ARCHITECTURE ───────────────────────────────────────────────
    story += h1('2. Architecture Technique')

    story.append(h2('2.1  Vue d\'ensemble de l\'architecture'))
    story.append(body(
        'L\'architecture suit un modèle monorepo avec séparation stricte frontend/backend. '
        'Les flux temps réel (vidéo, chat, timer) passent par WebRTC et WebSocket. '
        'L\'IA n\'est jamais appelée en temps réel pendant un débat — elle opère uniquement '
        'en tâche de fond asynchrone pour ne pas impacter la latence.'
    ))
    story.append(sp(8))

    # Architecture diagram as styled table
    arch_data = [
        [Paragraph('FRONTEND\nReact + Vite + Tailwind\n(Vercel)', ParagraphStyle('ad',
            fontName='Sans-Bold', fontSize=8, textColor=colors.white,
            alignment=TA_CENTER, leading=12)),
         Paragraph('↔ REST / WebSocket ↔', ParagraphStyle('arrow',
            fontName='Sans', fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)),
         Paragraph('BACKEND\nFastAPI Python\n(Railway)', ParagraphStyle('ad',
            fontName='Sans-Bold', fontSize=8, textColor=colors.white,
            alignment=TA_CENTER, leading=12)),
         Paragraph('↔ ORM / Async ↔', ParagraphStyle('arrow',
            fontName='Sans', fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)),
         Paragraph('DATA\nPostgreSQL + Redis\n(Supabase / Upstash)', ParagraphStyle('ad',
            fontName='Sans-Bold', fontSize=8, textColor=colors.white,
            alignment=TA_CENTER, leading=12))],
    ]
    arch_t = Table(arch_data, colWidths=[3.8*cm, 2.2*cm, 3.8*cm, 2.2*cm, 3.8*cm],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (0,0), C_BLUE),
            ('BACKGROUND',    (2,0), (2,0), C_NAVY),
            ('BACKGROUND',    (4,0), (4,0), colors.HexColor('#4A235A')),
            ('BACKGROUND',    (1,0), (1,0), colors.white),
            ('BACKGROUND',    (3,0), (3,0), colors.white),
            ('TOPPADDING',    (0,0), (-1,-1), 14),
            ('BOTTOMPADDING', (0,0), (-1,-1), 14),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]))
    story.append(arch_t)
    story.append(sp(8))

    # WebRTC P2P row
    wrtc = Table([[
        Paragraph('WebRTC P2P — DTLS-SRTP (chiffrement de bout en bout)\n'
                  'STUN: stun.l.google.com:19302  |  TURN: Metered.ca (50 GB/mois gratuit)',
                  ParagraphStyle('wrtc', fontName='Sans', fontSize=8,
                      textColor=colors.white, alignment=TA_CENTER, leading=12)),
    ]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',    (0,0),(-1,-1), C_RED),
            ('TOPPADDING',    (0,0),(-1,-1), 8),
            ('BOTTOMPADDING', (0,0),(-1,-1), 8),
            ('LEFTPADDING',   (0,0),(-1,-1), 10),
            ('RIGHTPADDING',  (0,0),(-1,-1), 10),
        ]))
    story.append(wrtc)
    story.append(sp(8))

    story.append(h2('2.2  Schéma de base de données (PostgreSQL)'))
    story.append(body('Entités principales et relations clés du modèle de données.'))
    story.append(sp(4))

    story += data_table(
        ['Table', 'Colonnes principales', 'Relations'],
        [
            ['users',    'id, email, pseudo, avatar_url, civility_score, debate_count, created_at',
             '→ opinions (1-N), debates (N-N via participants)'],
            ['opinions', 'id, user_id, theme, score (1-5), updated_at',
             '→ users (N-1)'],
            ['themes',   'id, slug, label_fr, label_en, active',
             'Référentiel des thèmes de débat'],
            ['queue',    'id, user_id, theme_id, created_at, expires_at',
             'Géré en Redis (miroir PostgreSQL pour audit)'],
            ['matches',  'id, user_a_id, user_b_id, theme_id, status, created_at',
             '→ debates (1-1)'],
            ['debates',  'id, match_id, started_at, ended_at, phase, duration_sec',
             '→ messages (1-N), ratings (1-N)'],
            ['messages', 'id, debate_id, user_id, content, flagged, created_at',
             'Chat texte du débat'],
            ['ratings',  'id, debate_id, rater_id, rated_id, score, tags[], comment',
             'Notation post-débat'],
            ['reports',  'id, debate_id, reporter_id, reason, status, resolved_at',
             'Signalements modération'],
            ['ai_logs',  'id, debate_id, action_type, input_hash, output, cost_usd, created_at',
             'Audit des appels IA'],
        ],
        col_widths=[2.8*cm, 6.5*cm, 6.2*cm]
    )

    story.append(h2('2.3  Endpoints API — FastAPI'))
    story.append(body('L\'API REST suit les conventions RESTful. Tous les endpoints nécessitent un JWT Bearer token sauf /auth/*.'))
    story.append(sp(4))

    story += data_table(
        ['Méthode', 'Endpoint', 'Description', 'Auth'],
        [
            ['POST', '/auth/register',         'Inscription email',                    'Public'],
            ['POST', '/auth/login',             'Connexion JWT',                        'Public'],
            ['POST', '/auth/google',            'OAuth2 Google',                        'Public'],
            ['GET',  '/users/me',               'Profil courant',                       'JWT'],
            ['PUT',  '/users/me/opinions',      'Mise à jour positions (8 thèmes)',     'JWT'],
            ['GET',  '/users/{id}/profile',     'Profil public',                        'JWT'],
            ['POST', '/queue/join',             'Rejoindre la file d\'attente',         'JWT'],
            ['DELETE','/queue/leave',           'Quitter la file',                      'JWT'],
            ['GET',  '/queue/status',           'Statut + position dans la file',       'JWT'],
            ['POST', '/matches/{id}/accept',    'Accepter un match',                    'JWT'],
            ['POST', '/matches/{id}/decline',   'Refuser un match',                     'JWT'],
            ['GET',  '/debates/{id}',           'Détails d\'un débat',                  'JWT'],
            ['POST', '/debates/{id}/report',    'Signaler un comportement',             'JWT'],
            ['POST', '/debates/{id}/rate',      'Soumettre une notation post-débat',    'JWT'],
            ['GET',  '/debates/history',        'Historique des débats de l\'user',     'JWT'],
            ['GET',  '/themes',                 'Liste des thèmes actifs',              'JWT'],
            ['POST', '/admin/reports/{id}/resolve','Résoudre un signalement',           'Admin'],
        ],
        col_widths=[1.4*cm, 5.2*cm, 6*cm, 1.9*cm]
    )

    story.append(h2('2.4  Événements WebSocket'))
    story.append(body(
        'Le serveur WebSocket FastAPI gère deux namespaces distincts : /ws/queue pour la file '
        'd\'attente et /ws/debate/{id} pour la salle de débat.'
    ))
    story.append(sp(4))

    story += data_table(
        ['Namespace', 'Événement', 'Direction', 'Payload'],
        [
            ['/ws/queue',   'queue.joined',      'Server→Client', '{ position, estimated_wait_sec }'],
            ['/ws/queue',   'match.found',        'Server→Client', '{ match_id, opponent_camp, theme }'],
            ['/ws/queue',   'match.timeout',      'Server→Client', '{ reason: "no_match" }'],
            ['/ws/debate',  'debate.phase_change','Server→Client', '{ phase, remaining_sec }'],
            ['/ws/debate',  'debate.timer',       'Server→Client', '{ seconds_left }  (broadcast /s)'],
            ['/ws/debate',  'chat.message',       'Bidirectionnel','{ user_id, content, timestamp }'],
            ['/ws/debate',  'reaction.sent',      'Bidirectionnel','{ type: "applause"|"contest"|"surprise" }'],
            ['/ws/debate',  'debate.ended',       'Server→Client', '{ reason, duration_sec }'],
            ['/ws/debate',  'webrtc.offer',       'Client→Server', '{ sdp }  (signaling P2P)'],
            ['/ws/debate',  'webrtc.answer',      'Client→Server', '{ sdp }'],
            ['/ws/debate',  'webrtc.ice',         'Client→Server', '{ candidate }'],
        ],
        col_widths=[2.5*cm, 3.8*cm, 2.8*cm, 6.4*cm]
    )

    story.append(pb())

    # ── 3. IA ─────────────────────────────────────────────────────────
    story += h1('3. Intégration IA — Modèles Légers')

    story.append(body(
        'L\'IA dans Zetis n\'est jamais exposée directement à l\'utilisateur. Elle opère '
        'exclusivement en arrière-plan pour améliorer la qualité du service : modération, '
        'matching, détection de toxicité, génération de résumés. Le principe directeur est '
        '<b>« IA invisible, impact maximal »</b>.'
    ))
    story.append(sp(6))

    story += info_box(
        '💡  Contrainte de coût : Tous les modèles IA choisis sont dans la catégorie "cheap inference". '
        'Aucun appel GPT-4 / Claude Opus en production MVP. Coût cible : < 0.01 € par débat complet.',
        C_NAVY
    )

    story.append(h2('3.1  Cartographie des usages IA'))
    story += data_table(
        ['Cas d\'usage', 'Modèle', 'Déclencheur', 'Latence cible', 'Coût estimé'],
        [
            ['Modération chat texte',
             'Claude Haiku 3.5\n(Anthropic)',
             'Chaque message chat envoyé',
             '< 500 ms', '~$0.0001/msg'],
            ['Score de toxicité (fallback)',
             'Perspective API\n(Google, gratuit)',
             'Si Haiku indisponible',
             '< 300 ms', 'Gratuit'],
            ['Résumé post-débat',
             'Gemini 2.0 Flash\n(Google)',
             'Fin du débat (async)',
             '< 5 sec', '~$0.0003/débat'],
            ['Suggestion de thème',
             'Gemini 2.0 Flash',
             'Onboarding step 3',
             '< 2 sec', '~$0.0001/user'],
            ['Analyse opposition\n(vecteur opinions)',
             'Algorithme local\n(NumPy cosinus)',
             'À chaque join queue',
             '< 10 ms', 'Gratuit'],
            ['Détection langue\n(FR/EN routing)',
             'langdetect lib\n(local)',
             'Inscription utilisateur',
             '< 50 ms', 'Gratuit'],
            ['Flag signalement\nprioritaire',
             'Claude Haiku 3.5',
             'Réception d\'un report',
             '< 1 sec', '~$0.0001/report'],
        ],
        col_widths=[3.5*cm, 3*cm, 3.5*cm, 2.5*cm, 3*cm]
    )

    story.append(h2('3.2  Architecture des appels IA'))
    story.append(body(
        'Tous les appels IA transitent par un service dédié <b>AIService</b> dans le backend FastAPI. '
        'Ce service est responsable du routing vers le bon modèle, du fallback en cas d\'erreur, '
        'et du logging des coûts dans la table ai_logs.'
    ))
    story.append(sp(4))

    story += code_block([
        '# services/ai_service.py — Structure du service IA Zetis',
        '',
        'class AIService:',
        '    """Orchestrateur IA — routing modèles légers"""',
        '',
        '    async def moderate_message(self, content: str) -> ModerationResult:',
        '        """Analyse un message chat. Haiku 3.5 → fallback Perspective API"""',
        '        try:',
        '            return await self._call_haiku(MODERATION_PROMPT, content)',
        '        except AnthropicError:',
        '            return await self._call_perspective(content)',
        '',
        '    async def summarize_debate(self, transcript: list[dict]) -> str:',
        '        """Résumé post-débat async. Gemini 2.0 Flash."""',
        '        return await self._call_gemini_flash(SUMMARY_PROMPT, transcript)',
        '',
        '    async def flag_report(self, report: Report) -> Priority:',
        '        """Priorité d\'un signalement (low/medium/high/critical)."""',
        '        return await self._call_haiku(FLAG_PROMPT, report.dict())',
        '',
        '    async def _call_haiku(self, system: str, content) -> Any:',
        '        """claude-haiku-4-5-20251001 — $0.80/M input, $4/M output"""',
        '        resp = await anthropic_client.messages.create(',
        '            model="claude-haiku-4-5-20251001",',
        '            max_tokens=256,',
        '            system=system,',
        '            messages=[{"role": "user", "content": str(content)}]',
        '        )',
        '        await self._log(model="haiku-3.5", tokens=resp.usage)',
        '        return resp.content[0].text',
        '',
        '    async def _call_gemini_flash(self, system: str, content) -> Any:',
        '        """gemini-2.0-flash — $0.10/M input, $0.40/M output"""',
        '        ...',
    ])

    story.append(h2('3.3  Prompt — Modération de message'))
    story.append(body(
        'Le prompt de modération est conçu pour renvoyer un JSON structuré minimal. '
        'L\'objectif est de minimiser le nombre de tokens output pour réduire les coûts.'
    ))
    story.append(sp(4))

    story += code_block([
        'MODERATION_PROMPT = """',
        'You are a debate moderation assistant for Zetis, a structured debate platform.',
        'Analyze the message below and return ONLY a JSON object with:',
        '- "safe": boolean (true if message is acceptable)',
        '- "severity": "none" | "low" | "medium" | "high" | "critical"',
        '- "reason": one-line reason if not safe, else null',
        '',
        'Rules: Flag hate speech, personal insults, threats, illegal content.',
        'Do NOT flag strong opinions, provocative arguments, or factual disagreements.',
        'Context: political/religious debate platform. Strong language on IDEAS is allowed.',
        '',
        'Return ONLY valid JSON. No explanation. No markdown.',
        '"""',
    ])

    story.append(h2('3.4  Algorithme de matching (local — sans IA externe)'))
    story.append(body(
        'Le matching est le cœur du produit. Il est calculé localement avec NumPy — '
        'aucun appel API externe. La distance cosinus entre les vecteurs d\'opinion '
        'de deux utilisateurs détermine leur degré d\'opposition.'
    ))
    story.append(sp(4))

    story += code_block([
        '# services/matching_engine.py',
        '',
        'import numpy as np',
        'from typing import Optional',
        '',
        'THEMES = ["immigration","laicite","economie","religion",',
        '          "justice","environnement","education","bioethique"]',
        '',
        'def opposition_score(vec_a: list[int], vec_b: list[int]) -> float:',
        '    """',
        '    Calcule le score d\'opposition entre deux vecteurs d\'opinion.',
        '    Scores 1-5 sur 8 thèmes. Retourne 0.0 (identiques) à 1.0 (opposés).',
        '    Seuil de match MVP : opposition_score >= 0.70',
        '    """',
        '    a = np.array(vec_a, dtype=float)',
        '    b = np.array(vec_b, dtype=float)',
        '    # Inverser b pour mesurer l\'opposition (pas la similarité)',
        '    b_inv = 6 - b  # Inverser l\'échelle 1-5',
        '    cos_sim = np.dot(a, b_inv) / (np.linalg.norm(a) * np.linalg.norm(b_inv))',
        '    return float(cos_sim)',
        '',
        'async def find_match(',
        '    user_id: str,',
        '    theme_id: Optional[str],',
        '    user_opinions: list[int]',
        ') -> Optional[str]:',
        '    """Cherche dans Redis le meilleur opposant disponible."""',
        '    candidates = await redis.get_queue(theme_id or "all")',
        '    best_match, best_score = None, 0.0',
        '    for candidate in candidates:',
        '        if candidate.user_id == user_id: continue',
        '        score = opposition_score(user_opinions, candidate.opinions)',
        '        if score >= 0.70 and score > best_score:',
        '            best_match, best_score = candidate, score',
        '    return best_match',
    ])

    story.append(pb())

    # ── 4. SÉCURITÉ & RGPD ────────────────────────────────────────────
    story += h1('4. Sécurité & Conformité Légale')

    story.append(h2('4.1  Sécurité applicative'))
    story += data_table(
        ['Risque', 'Mesure de protection', 'Implémentation'],
        [
            ['Injection SQL',           'ORM SQLAlchemy uniquement — zéro requête brute',          'SQLAlchemy 2.0 + Alembic'],
            ['XSS',                     'Sanitisation côté React (dangerouslySetInnerHTML interdit)','DOMPurify sur tous les inputs'],
            ['CSRF',                    'Tokens JWT stateless — pas de cookies de session',         'HttpOnly cookie refresh token'],
            ['Données opinion exposées','Vecteurs stockés chiffrés (AES-256)',                      'SQLAlchemy encrypted field'],
            ['MITM vidéo',              'WebRTC DTLS-SRTP chiffrement natif bout-en-bout',          'Natif WebRTC'],
            ['Abus matching',           'Rate limiting : 10 joins/heure par user',                  'FastAPI + Redis counter'],
            ['Brute force auth',        'Rate limiting : 5 tentatives/15 min par IP',               'slowapi middleware'],
            ['Token leakage',           'Access token 15 min, refresh 7 jours, rotation obligatoire','Supabase Auth'],
        ],
        col_widths=[3.5*cm, 6*cm, 6*cm]
    )

    story.append(h2('4.2  Conformité RGPD'))
    story.append(body(
        'Les données d\'opinion (positions politiques, religieuses) sont des <b>données sensibles '
        'au sens de l\'article 9 du RGPD</b>. Elles nécessitent un traitement spécifique.'
    ))
    story.append(sp(4))

    for b_text in [
        '<b>Base légale :</b> consentement explicite (opt-in) à la collecte des données d\'opinion, '
        'distinct du consentement CGU. L\'utilisateur peut retirer son consentement à tout moment.',
        '<b>Droit à l\'effacement :</b> endpoint DELETE /users/me qui supprime toutes les données '
        'personnelles dans les 30 jours (cascade sur opinions, debates, ratings).',
        '<b>Portabilité :</b> endpoint GET /users/me/export qui renvoie un JSON complet de toutes '
        'les données de l\'utilisateur (format RGPD-conforme).',
        '<b>Minimisation :</b> pseudonyme obligatoire (pas de nom réel requis), avatar optionnel, '
        'aucune donnée géographique précise collectée au MVP.',
        '<b>Sous-traitants :</b> Supabase (UE), Railway (UE region), Upstash (UE). '
        'Anthropic (USA) — DPA signé, clause contractuelle type UE-USA.',
    ]:
        story.append(bullet(b_text))

    story.append(sp(6))
    story.append(h2('4.3  Cadre légal modération (DSA + Loi 1881)'))
    story += info_box(
        '⚖  Le Digital Services Act (DSA) impose aux plateformes avec du contenu généré par les '
        'utilisateurs une politique de modération documentée et publique dès le lancement. '
        'En France, la loi du 29 juillet 1881 engage la responsabilité de l\'auteur des propos '
        'tenus en direct. Zetis est hébergeur (responsabilité limitée) si la modération est '
        'effective et documentée.',
        C_RED
    )

    story.append(pb())

    # ── 5. FLUX TEMPS RÉEL ────────────────────────────────────────────
    story += h1('5. Flux Temps Réel — WebRTC & WebSocket')

    story.append(h2('5.1  Diagramme de séquence — Connexion WebRTC'))
    story.append(body(
        'La connexion vidéo P2P suit le protocole WebRTC standard avec signaling via le serveur '
        'FastAPI WebSocket. Le serveur ne transporte jamais les flux media — il échange uniquement '
        'les messages de signaling (SDP, ICE candidates).'
    ))
    story.append(sp(6))

    seq_data = [
        ['User A (Browser)', '', 'Serveur FastAPI\n(Signaling)', '', 'User B (Browser)'],
        ['→ ws connect /ws/debate/{id}', '→', 'accepte connexion WS', '←', '← ws connect /ws/debate/{id}'],
        ['→ webrtc.offer {sdp}', '→', 'relay à User B', '→', '← reçoit offer'],
        ['', '', '', '←', '← webrtc.answer {sdp}'],
        ['← reçoit answer', '←', 'relay à User A', '', ''],
        ['→ webrtc.ice {candidate}', '→', 'relay ICE', '→', '← reçoit ICE candidate'],
        ['⟺ Connexion P2P directe (DTLS-SRTP)', '', '⚡ Plus de transit serveur pour video/audio', '', ''],
        ['⟺ Chat + timer + réactions', '→', 'via WebSocket (pas P2P)', '←', '⟺'],
    ]

    seq_t = Table(seq_data, colWidths=[4.2*cm, 0.8*cm, 4.2*cm, 0.8*cm, 4.2*cm],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), C_NAVY),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTNAME',      (0,0), (-1,0), 'Sans-Bold'),
            ('FONTNAME',      (0,1), (-1,-1), 'Courier'),
            ('FONTSIZE',      (0,0), (-1,-1), 7),
            ('TEXTCOLOR',     (0,1), (-1,-1), C_DARK),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_LIGHT, colors.white]),
            ('GRID',          (0,0), (-1,-1), 0.3, C_BORDER),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING',   (0,0), (-1,-1), 5),
            ('RIGHTPADDING',  (0,0), (-1,-1), 5),
            ('ALIGN',         (1,0), (1,-1), 'CENTER'),
            ('ALIGN',         (3,0), (3,-1), 'CENTER'),
            ('BACKGROUND',    (0,7), (-1,7), colors.HexColor('#E8F5EF')),
            ('FONTNAME',      (0,7), (-1,7), 'Sans-Bold'),
            ('FONTSIZE',      (0,7), (-1,7), 7),
        ]))
    story.append(seq_t)
    story.append(sp(8))

    story.append(h2('5.2  Timer de débat — Source de vérité serveur'))
    story.append(body(
        'Le timer est géré côté serveur pour éviter toute manipulation client. '
        'Un job asyncio envoie un broadcast WebSocket toutes les secondes aux deux participants.'
    ))
    story.append(sp(4))

    story += code_block([
        '# Phases du débat — gestion serveur',
        'DEBATE_PHASES = [',
        '    {"id": "opening",    "duration_sec": 120, "label": "Ouverture"},',
        '    {"id": "debate",     "duration_sec": 300, "label": "Débat libre"},',
        '    {"id": "conclusion", "duration_sec": 120, "label": "Conclusion"},',
        ']',
        '',
        'async def run_debate_timer(debate_id: str, ws_manager: WSManager):',
        '    for phase in DEBATE_PHASES:',
        '        await ws_manager.broadcast(debate_id, {',
        '            "event": "debate.phase_change",',
        '            "phase": phase["id"],',
        '            "label": phase["label"],',
        '            "duration_sec": phase["duration_sec"]',
        '        })',
        '        for remaining in range(phase["duration_sec"], 0, -1):',
        '            await asyncio.sleep(1)',
        '            await ws_manager.broadcast(debate_id, {',
        '                "event": "debate.timer",',
        '                "seconds_left": remaining',
        '            })',
        '    await end_debate(debate_id)',
    ])

    story.append(pb())

    # ── 6. COMPOSANTS FRONTEND ────────────────────────────────────────
    story += h1('6. Architecture Frontend — React + Tailwind')

    story.append(h2('6.1  Structure des composants'))
    story.append(body(
        'L\'application React est organisée en Feature Folders. Chaque feature '
        'regroupe ses composants, hooks, stores et types dans un dossier dédié.'
    ))
    story.append(sp(4))

    story += code_block([
        'src/',
        '├── features/',
        '│   ├── auth/          # Login, Register, OAuth callback',
        '│   ├── onboarding/    # Questionnaire opinions (8 étapes)',
        '│   ├── profile/       # Profil, radar chart opinions',
        '│   ├── queue/         # File attente, matching, accept/decline',
        '│   ├── debate/        # Salle débat WebRTC, timer, chat, réactions',
        '│   ├── rating/        # Notation post-débat, tags',
        '│   └── moderation/    # Signalement, formulaire report',
        '├── components/        # Composants UI génériques (Button, Card, Badge...)',
        '├── hooks/             # useWebRTC, useWebSocket, useDebateTimer',
        '├── stores/            # Zustand stores (authStore, debateStore)',
        '├── services/          # API client (axios), WS client (socket.io)',
        '└── lib/               # Utils, constants, types TypeScript',
    ])

    story.append(h2('6.2  Gestion WebRTC côté client'))
    story += code_block([
        '// hooks/useWebRTC.ts — Hook de connexion vidéo P2P',
        '',
        'export function useWebRTC(debateId: string) {',
        '  const [localStream, setLocalStream] = useState<MediaStream|null>(null)',
        '  const [remoteStream, setRemoteStream] = useState<MediaStream|null>(null)',
        '  const pc = useRef<RTCPeerConnection|null>(null)',
        '',
        '  const initPeerConnection = useCallback(() => {',
        '    pc.current = new RTCPeerConnection({',
        '      iceServers: [',
        '        { urls: "stun:stun.l.google.com:19302" },',
        '        { urls: "turn:relay.metered.ca:443",',
        '          username: process.env.TURN_USER,',
        '          credential: process.env.TURN_PASS }',
        '      ]',
        '    })',
        '    pc.current.ontrack = (e) => setRemoteStream(e.streams[0])',
        '    pc.current.onicecandidate = (e) => {',
        '      if (e.candidate) ws.emit("webrtc.ice", { candidate: e.candidate })',
        '    }',
        '  }, [])',
        '',
        '  // ... offer/answer/ICE handling via WebSocket signaling',
        '}',
    ])

    story.append(h2('6.3  Écrans et maquettes — Correspondance composants'))
    story.append(sp(4))

    story += data_table(
        ['Écran', 'Route React', 'Composant principal', 'Store consommé'],
        [
            ['Splash / Welcome',      '/welcome',           'WelcomeScreen',      '—'],
            ['Login / Register',      '/auth',              'AuthScreen',         'authStore'],
            ['Questionnaire',         '/onboarding',        'OpinionQuestionnaire','authStore'],
            ['Dashboard Accueil',     '/home',              'HomeScreen',         'authStore, queueStore'],
            ['Profil utilisateur',    '/profile',           'ProfileScreen',      'authStore'],
            ['File d\'attente',       '/queue',             'QueueScreen',        'queueStore'],
            ['Salle de débat',        '/debate/:id',        'DebateRoom',         'debateStore'],
            ['Notation post-débat',   '/debate/:id/rate',   'RatingScreen',       'debateStore'],
            ['Récapitulatif',         '/debate/:id/summary','SummaryScreen',      'debateStore'],
            ['Signalement',           '/debate/:id/report', 'ReportScreen',       'debateStore'],
            ['Activité / Notifs',     '/activity',          'ActivityScreen',     'authStore'],
        ],
        col_widths=[3.5*cm, 3.5*cm, 4*cm, 4.5*cm]
    )

    story.append(sp(6))
    story.append(body('Salle de débat mobile — écran le plus complexe du MVP :'))
    story.append(img('screen_07_debate.png', width=6*cm))
    story.append(caption('Écran 7 — Salle de débat mobile (composant DebateRoom)'))

    story.append(pb())

    # ── 7. DÉPLOIEMENT ────────────────────────────────────────────────
    story += h1('7. Infrastructure & Déploiement')

    story.append(h2('7.1  Environnements'))
    story += data_table(
        ['Environnement', 'Frontend', 'Backend', 'Base de données', 'Déclencheur'],
        [
            ['Development', 'localhost:5173', 'localhost:8000', 'Supabase dev project', 'Manuel'],
            ['Staging',     'zetis-staging.vercel.app', 'Railway staging', 'Supabase staging', 'Push sur develop'],
            ['Production',  'app.zetis.io', 'Railway prod', 'Supabase prod', 'Merge sur main'],
        ],
        col_widths=[2.8*cm, 3.8*cm, 3.8*cm, 3.8*cm, 3.8*cm]
    )

    story.append(h2('7.2  Variables d\'environnement requises'))
    story += code_block([
        '# Backend FastAPI (.env)',
        'DATABASE_URL=postgresql+asyncpg://...supabase.co/postgres',
        'REDIS_URL=rediss://...upstash.io:6380',
        'JWT_SECRET=<256-bit-random>',
        'SUPABASE_URL=https://xxx.supabase.co',
        'SUPABASE_SERVICE_KEY=<service-role-key>',
        'ANTHROPIC_API_KEY=sk-ant-...',
        'GOOGLE_AI_API_KEY=AIza...',
        'TURN_USERNAME=<metered-username>',
        'TURN_CREDENTIAL=<metered-credential>',
        '',
        '# Frontend React (.env.local)',
        'VITE_API_URL=https://api.zetis.io',
        'VITE_WS_URL=wss://api.zetis.io',
        'VITE_SUPABASE_URL=https://xxx.supabase.co',
        'VITE_SUPABASE_ANON_KEY=<anon-key>',
        'VITE_TURN_USERNAME=<metered-username>',
        'VITE_TURN_CREDENTIAL=<metered-credential>',
    ])

    story.append(h2('7.3  Estimation des coûts MVP (100 débats/jour)'))
    story += data_table(
        ['Service', 'Plan', 'Coût mensuel estimé'],
        [
            ['Vercel (frontend)',      'Hobby (gratuit)',              '0 €'],
            ['Railway (FastAPI)',      'Starter 5$/mois',             '~5 €'],
            ['Supabase (DB + Auth)',   'Free tier (500 MB)',           '0 €'],
            ['Upstash Redis',         'Free tier (10K cmds/jour)',     '0 €'],
            ['Metered TURN',          'Free 50 GB/mois',              '0 €'],
            ['Anthropic Haiku',       '~500 appels/jour × $0.0001',   '~1.5 €'],
            ['Google Gemini Flash',   '~100 résumés/jour × $0.0003',  '~0.9 €'],
            ['Total MVP',             '—',                            '<b>~7-8 € / mois</b>'],
        ],
        col_widths=[5*cm, 5.5*cm, 5*cm]
    )

    story.append(pb())

    # ── 8. ROADMAP ────────────────────────────────────────────────────
    story += h1('8. Roadmap de Développement')

    story += data_table(
        ['Sprint', 'Durée', 'Périmètre technique', 'Livrable'],
        [
            ['S1', '2 sem.',
             'Auth Supabase (email + Google). Modèle DB complet + migrations Alembic. '
             'Questionnaire opinions (8 thèmes). API REST /auth /users /opinions.',
             'Utilisateur peut s\'inscrire et renseigner ses positions.'],
            ['S2', '2 sem.',
             'File Redis. Algorithme matching (cosinus). WebSocket /ws/queue. '
             'Accept/decline match. Notifications en temps réel.',
             'Deux users peuvent être matchés et accepter un débat.'],
            ['S3', '3 sem.',
             'Serveur signaling WebRTC (FastAPI WS). Connexion vidéo 1v1 STUN/TURN. '
             'Timer serveur broadcast. Chat texte WS. Bouton signalement.',
             'Débat vidéo structuré fonctionnel de bout en bout.'],
            ['S4', '1 sem.',
             'Intégration Haiku (modération chat). Intégration Gemini Flash (résumé). '
             'Notation post-débat. Score civilité. Historique.',
             'IA opérationnelle, profil complet, historique débats.'],
            ['S5', '1 sem.',
             'Tests de charge (k6). Audit sécurité (OWASP top 10). '
             'CGU + politique modération DSA. CI/CD GitHub Actions. Go-live prod.',
             'Production déployée, monitorée, legalement conforme.'],
        ],
        col_widths=[1.2*cm, 1.4*cm, 8.5*cm, 4.4*cm]
    )

    story.append(sp(8))
    story.append(h2('8.1  KPIs de validation MVP'))
    story += data_table(
        ['Indicateur', 'Seuil critique', 'Objectif MVP', 'Objectif Scale'],
        [
            ['Complétion débat (jusqu\'à fin)', '< 40 %',   '≥ 60 %', '≥ 75 %'],
            ['Score civilité moyen',            '< 3.0 / 5', '≥ 3.5 / 5', '≥ 4.0 / 5'],
            ['Délai de matching',               '> 10 min', '< 5 min', '< 2 min'],
            ['Rétention J+7',                   '< 15 %',   '≥ 25 %', '≥ 40 %'],
            ['Taux de signalement / débat',     '> 20 %',   '< 10 %', '< 5 %'],
            ['Coût IA / débat',                 '> 0.05 €', '< 0.01 €', '< 0.005 €'],
            ['Latence vidéo P2P',               '> 500 ms', '< 200 ms', '< 150 ms'],
        ],
        col_widths=[5*cm, 3*cm, 3*cm, 3*cm]
    )

    story.append(pb())

    # ── 9. GLOSSAIRE ──────────────────────────────────────────────────
    story += h1('9. Glossaire Technique')

    story += data_table(
        ['Terme', 'Définition'],
        [
            ['WebRTC',        'Web Real-Time Communication. Standard W3C pour vidéo/audio P2P chiffré entre navigateurs.'],
            ['DTLS-SRTP',     'Protocole de chiffrement bout-en-bout appliqué automatiquement par WebRTC sur tous les flux media.'],
            ['STUN',          'Session Traversal Utilities for NAT. Serveur qui aide deux pairs à découvrir leurs IPs publiques.'],
            ['TURN',          'Traversal Using Relays around NAT. Serveur relais pour les connexions WebRTC qui ne peuvent pas être directes (NAT symétrique).'],
            ['SDP',           'Session Description Protocol. Format d\'échange des capacités media entre deux pairs WebRTC (codec, résolution, etc.).'],
            ['ICE Candidate', 'Adresse réseau candidate (IP:port) proposée lors de l\'établissement d\'une connexion WebRTC P2P.'],
            ['Distance cosinus','Mesure mathématique de similarité entre deux vecteurs. Utilisée pour calculer le score d\'opposition entre profils d\'opinion.'],
            ['JWT',           'JSON Web Token. Standard de token d\'authentification stateless signé (access 15 min + refresh 7 jours).'],
            ['DSA',           'Digital Services Act. Réglementation EU 2022 sur la responsabilité des plateformes numériques hébergeant du contenu utilisateur.'],
            ['RGPD / Art. 9', 'Données sensibles au sens du RGPD : opinions politiques, religieuses, philosophiques. Traitement soumis au consentement explicite.'],
            ['Haiku 3.5',     'claude-haiku-4-5-20251001 d\'Anthropic. Modèle rapide et économique ($0.80/M input). Utilisé pour la modération temps réel.'],
            ['Gemini Flash',  'gemini-2.0-flash de Google DeepMind. Modèle multimodal rapide ($0.10/M input). Utilisé pour les résumés post-débat.'],
            ['Alembic',       'Outil de migration de schéma de base de données pour SQLAlchemy. Versionne les changements de structure DB.'],
            ['Zustand',       'Bibliothèque de gestion d\'état React légère (alternative Redux). Utilisée pour authStore, debateStore, queueStore.'],
        ],
        col_widths=[3*cm, 12.5*cm]
    )

    story.append(sp(12))
    story += info_box(
        '© 2026 Zetis — ΖΉΤΗΣΙΣ — Document confidentiel à usage interne. '
        'Version MVP 1.0 — Avril 2026. '
        'Stack : React + Tailwind · FastAPI · PostgreSQL · Redis · WebRTC · Claude Haiku · Gemini Flash. '
        '"Opposez vos idées. Questionnez la vérité."',
        C_NAVY
    )

    return story


# ── Build ──────────────────────────────────────────────────────────────
def main():
    # Chemin de sortie adapté pour macOS
    out_path = os.path.join(os.path.dirname(__file__), 'CDC_Technique_Zetis_MVP.pdf')
    
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title='Zetis — Cahier des Charges Technique MVP 1.0',
        author='Zetis',
        subject='CDC Technique — Plateforme débat live 1v1',
    )
    story = build_story()
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    
    size = os.path.getsize(out_path) / 1024
    print(f'✓ PDF généré avec succès : {out_path}')
    print(f'   Taille : {size:.1f} KB')


if __name__ == '__main__':
    main()