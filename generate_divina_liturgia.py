import re
import html
import os

with open('Divina Liturgia.md', 'r', encoding='utf-8') as f:
    raw_md = f.read()

pages = re.split(r'--- PÁGINA (\d+) ---', raw_md)
page_data = {}
for i in range(1, len(pages), 2):
    p_num = pages[i]
    content = pages[i+1].strip()
    page_data[p_num] = content

def clean_cell(c):
    c = c.strip()
    c = re.sub(r'<br\s*/?>\s*$', '', c).strip()
    return c

actor_re = re.compile(
    r'^\*\*(?:[ΙΔΛIDLSC][:.]|'
    r'Ο ιερέυς(?:\s*\(Ι\))?:?|Ο διάκονος(?:\s*\(Δ\))?:?|Ο λαός(?:\s*\(Λ\))?:?|'
    r'O ieréfs(?:\s*\(I\))?:?|O diákonos(?:\s*\(D\))?:?|O laós(?:\s*\(L\))?:?|'
    r'O Sacerdote(?:\s*\(S\))?:?|O Diácono(?:\s*\(D\))?(?:\s*\(sentados\))?:?|O Coro(?:\s*\(C\))?:?|'
    r'Ο [αβ] χορός:?|O [12]º Coro:?|Leitor:?|D\./S\.|S\.|C\.:?|DIÁCONO:?|SACERDOTE:?|CORO:?|CORO\.)\*\*$'
)

banner_titles = [
    'Η ΘΕΙΑ ΛΕΙΤΟΥΡΓΙΑ', 'H THÌA LITURGHÍA', 'A DIVINA LITURGIA',
    'ΕΙΡΗΝΙΚΑ', 'IRINIKÁ', 'LITANIA DA PAZ',
    'PRIMEIRA ANTÍFONA', 'PEQUENA LADAINHA',
    'TERCEIRA ANTÍFONA', 'TROPÁRIO DA RESSURREIÇÃO', 'APOLITIKION OU TROPARION',
    'PROCISSÃO DO SANTO EVANGELHO',
    'ΕΙΣΟΔΟΣ ΤΟΥ ΕΥΑΓΓΕΛΙΟΥ ΚΑΙ ΙΕΡΑ ΑΝΑΓΝΩΣΜΑΤΑ', 'ISODOS TU EVANGUELIU KE IERA ANAGHNOSMATA', 'PROCISSÃO DO EVANGELHO E LEITURAS SAGRADAS',
    'Τρισάγιος', 'Trisághios',
    'LITANIA PELA IGREJA', 'ΕΚΤΕΝΗΣ ΔΕΗΣΙΣ', 'EKTENIS DEISIS',
    'ΕΚΤΕΝΗΣ ΚΑΙ ΜΕΓΑΛΗ ΕΙΣΟΔΟΣ', 'EKTENIS KE MEGALI ISODOS', 'SUPLICA E GRANDE ENTRADA', 'SÚPLICA E GRANDE ENTRADA',
    'PROCISSÃO DAS OFERENDAS', 'Μεγαλη Είσοδος:', 'Megháli Isodos:', 'Grande Entrada',
    'ΕΚΤΕΝΗΣ ΤΗΣ ΠΡΟΣΚΟΜΙΔΗΣ ΚΑΙ ΤO ΣΥΜΒΟΛΟ ΤΗΣ ΠΙΣΤΕΩΣ', 'EKTENIS TIS PROSKOMIDIS KE TO SİMVOLO TIS PÍSTEOS', 
    'SUPLICA DO OFERTORIO E PROFISSÃO DE FE (sentados)', 'SÚPLICA DO OFERTÓRIO E PROFISSÃO DE FÉ (sentados)',
    'Πιστεύου', 'CREDO NICENO-CONSTANTINOPOLITANO', 'Profissão de Fe (Credo)', 'Profissão de Fé (Credo)',
    'Η ΑΓΙΑ ΑΝΑΦΟΡΑ', 'HAGHIA ANAFORA', 'SACRIFICIO EUCARISTICO', 'SACRIFÍCIO EUCARÍSTICO',
    'MEMORIAL', 'HINO SANTA MÃE DE DEUS',
    'ΔΙΠΤΥΧΑ ΚΑΙ ΔΕΗΣΕΙΣ', 'DIPTINA KE DEISIS', 'INTENCÕES E INTERCESSÕES', 'INTENÇÕES E INTERCESSÕES',
    'ORAÇÃO DOMINICAL',
    'ΘΕΙΑ ΚΟΙΝΩΝΙΑ', 'THIA KINONIA', 'SANTA COMUNHÃO',
    'COMUNHÃO', 'ORAÇÃO PREPARATORIA', 'ORAÇÃO PREPARATÓRIA', 'COMUNHÃO DOS FIEIS', 'COMUNHÃO DOS FIÉIS',
    'LITANIA DE AÇÃO DE GRAÇAS APOS A COMUNHÃO', 'LITANIA DE AÇÃO DE GRAÇAS APÓS A COMUNHÃO',
    'RITO FINAL', 'ΑΠΟΛΥΣΗ', 'APOLISI',
    'BENÇÃO FINAL', 'BÊNÇÃO FINAL',
    'DESPEDIDA', 'Αντισωρός', 'Antidoros', 'Pão Bento',
    'Apolisis (Encerramento da Missa)'
]

def is_banner_row(cells):
    non_empty = [c for c in cells if c]
    if not non_empty:
        return False
    if all(actor_re.match(c) for c in non_empty):
        return False
    for c in non_empty:
        if c.startswith('**') and len(c) <= 75:
            c_clean = re.sub(r'^\*\*|\*\*$', '', c).strip()
            c_clean = re.sub(r'\(varia de acordo com calendário litúrgico\)', '', c_clean).strip()
            for b in banner_titles:
                if b.upper() in c_clean.upper():
                    return True
    return False

def is_actor_row(cells):
    non_empty = [c for c in cells if c]
    if not non_empty:
        return False
    return all(actor_re.match(c) for c in non_empty)

def format_cell_content(cell_text, col_idx):
    if not cell_text:
        return ''
    
    # Process markdown bold: **text**
    def replace_bold(match):
        content = match.group(1)
        is_actor = bool(re.match(r'^(?:[ΙΔΛIDLSC]|Ο ιερέυς|Ο διάκονος|Ο λαός|O ieréfs|O diákonos|O laós|O Sacerdote|O Diácono|O Coro|Leitor|D\./S\.|S\.|C\.|DIÁCONO|SACERDOTE|CORO)\b', content))
        if is_actor:
            return f'<strong class="actor-tag">{content}</strong>'
        else:
            return f'<strong class="liturgy-strong">{content}</strong>'
    
    formatted = re.sub(r'\*\*(.+?)\*\*', replace_bold, cell_text)
    
    # Format rubrics in parentheses
    def replace_rubric(match):
        content = match.group(0)
        return f'<span class="rubric">{content}</span>'
    
    formatted = re.sub(r'\((?:sentados|em pé|de pé|ὀρθοί|orthi|Εκφώνως|Ekfōnos|Ekfonos|Ekfoni|Em voz alta|τρις|tris|3x|γ|três vezes|δεινος|tu dínos|varia de acordo com calendário litúrgico|Repete o apolitikion de domingo|Leitura da Epístola \+ do Apóstolo São\.\.\.\.\.|Encerramento da Missa|tis iméras|tu Naú|i de mi, aplós|1 de mi, aplós|του δείνος|τη ση χάριτι|ει δε μη απλώς)\)', replace_rubric, formatted)
    
    return formatted

def parse_page_table_rows(page_content):
    if '| Grego Original |' not in page_content:
        return []
    parts = page_content.split('| Grego Original | Transliteração | Português |\n| --- | --- | --- |')
    if len(parts) < 2:
        return []
    tbl_text = parts[1]
    lines = tbl_text.split('\n')
    i = 0
    rows = []
    while i < len(lines):
        line = lines[i]
        if '|' in line and line.strip() != '|':
            accum = line
            while accum.count('|') < 4 and i + 1 < len(lines):
                i += 1
                accum += ' ' + lines[i].strip()
            if not ('| --- |' in accum) and not ('| Grego Original |' in accum) and accum.count('|') >= 4:
                cells = [clean_cell(c) for c in accum.split('|')[1:4]]
                rows.append(cells)
        i += 1
    return rows

def render_table(rows):
    html_lines = []
    html_lines.append('<div class="table-wrapper">')
    html_lines.append('  <table class="liturgy-table">')
    html_lines.append('    <colgroup>')
    html_lines.append('      <col class="col-greek">')
    html_lines.append('      <col class="col-translit">')
    html_lines.append('      <col class="col-portuguese">')
    html_lines.append('    </colgroup>')
    html_lines.append('    <thead>')
    html_lines.append('      <tr>')
    html_lines.append('        <th class="col-greek" lang="el">Grego Original</th>')
    html_lines.append('        <th class="col-translit">Transliteração Fonética</th>')
    html_lines.append('        <th class="col-portuguese">Tradução em Português</th>')
    html_lines.append('      </tr>')
    html_lines.append('    </thead>')
    html_lines.append('    <tbody>')
    
    for cells in rows:
        c1, c2, c3 = cells
        if is_banner_row(cells):
            html_lines.append('      <tr class="section-banner-row">')
            html_lines.append(f'        <td class="col-greek" lang="el">{format_cell_content(c1, 0)}</td>')
            html_lines.append(f'        <td class="col-translit">{format_cell_content(c2, 1)}</td>')
            html_lines.append(f'        <td class="col-portuguese">{format_cell_content(c3, 2)}</td>')
            html_lines.append('      </tr>')
        elif is_actor_row(cells):
            html_lines.append('      <tr class="actor-row">')
            html_lines.append(f'        <td class="col-greek" lang="el">{format_cell_content(c1, 0)}</td>')
            html_lines.append(f'        <td class="col-translit">{format_cell_content(c2, 1)}</td>')
            html_lines.append(f'        <td class="col-portuguese">{format_cell_content(c3, 2)}</td>')
            html_lines.append('      </tr>')
        else:
            html_lines.append('      <tr class="liturgy-row">')
            html_lines.append(f'        <td class="col-greek" lang="el">{format_cell_content(c1, 0)}</td>')
            html_lines.append(f'        <td class="col-translit">{format_cell_content(c2, 1)}</td>')
            html_lines.append(f'        <td class="col-portuguese">{format_cell_content(c3, 2)}</td>')
            html_lines.append('      </tr>')
            
    html_lines.append('    </tbody>')
    html_lines.append('  </table>')
    html_lines.append('</div>')
    return '\n'.join(html_lines)

byzantine_divider_svg = '''<div class="byzantine-divider" aria-hidden="true">
  <svg width="340" height="26" viewBox="0 0 340 26" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 13h135M195 13h135" stroke="#A68A56" stroke-width="1.2" stroke-linecap="round"/>
    <circle cx="20" cy="13" r="2.5" fill="#7A0C0C"/>
    <circle cx="135" cy="13" r="2" fill="#A68A56"/>
    <circle cx="205" cy="13" r="2" fill="#A68A56"/>
    <circle cx="320" cy="13" r="2.5" fill="#7A0C0C"/>
    <!-- Central Byzantine Cross -->
    <path d="M170 2v22M158 9h24M162 19h16" stroke="#7A0C0C" stroke-width="2.2" stroke-linecap="round"/>
    <circle cx="170" cy="2" r="2" fill="#A68A56"/>
    <circle cx="170" cy="24" r="2" fill="#A68A56"/>
    <circle cx="158" cy="9" r="1.8" fill="#A68A56"/>
    <circle cx="182" cy="9" r="1.8" fill="#A68A56"/>
  </svg>
</div>'''

# Collect rows for tables
tbl1_rows = parse_page_table_rows(page_data['3'])
tbl2_rows = parse_page_table_rows(page_data['4'])
tbl3_rows = (parse_page_table_rows(page_data['6']) + 
             parse_page_table_rows(page_data['7']) + 
             parse_page_table_rows(page_data['8']) + 
             parse_page_table_rows(page_data['9']))
tbl4_rows = (parse_page_table_rows(page_data['10']) + 
             parse_page_table_rows(page_data['11']) + 
             parse_page_table_rows(page_data['12']) + 
             parse_page_table_rows(page_data['13']) + 
             parse_page_table_rows(page_data['17']) + 
             parse_page_table_rows(page_data['19']) + 
             parse_page_table_rows(page_data['21']) + 
             parse_page_table_rows(page_data['23']))
tbl5_rows = (parse_page_table_rows(page_data['27']) + 
             parse_page_table_rows(page_data['29']) + 
             parse_page_table_rows(page_data['30']) + 
             parse_page_table_rows(page_data['31']) + 
             parse_page_table_rows(page_data['32']) + 
             parse_page_table_rows(page_data['33']) + 
             parse_page_table_rows(page_data['35']) + 
             parse_page_table_rows(page_data['39']))
tbl6_rows = (parse_page_table_rows(page_data['41']) + 
             parse_page_table_rows(page_data['42']) + 
             parse_page_table_rows(page_data['43']))

html_doc = f'''<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A Divina Liturgia de São João Crisóstomo</title>
  
  <!-- Fontes Tipográficas: Cardo (Títulos), Cormorant Garamond / Cormorant (Texto Latino), EB Garamond / GFS Didot (Texto Grego) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cardo:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Cormorant:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=GFS+Didot&display=swap" rel="stylesheet">

  <style>
    /* ==========================================================================
       PALETA LITÚRGICA BIZANTINA E VARIÁVEIS TIPOGRÁFICAS
       ========================================================================== */
    :root {{
      --bg-page: #FFFDF9;
      --text-main: #1A1816;
      --text-translit: #3A3530;
      --rubric-crimson: #7A0C0C;
      --rubric-deep: #8B1E1E;
      --gold-accent: #A68A56;
      --gold-bright: #D4AF37;
      --gold-subtle: rgba(166, 138, 86, 0.12);
      --banner-bg: #F7F3EB;
      --border-outer: #7A0C0C;
      --border-inner: #A68A56;
    }}

    /* ==========================================================================
       ARQUITETURA DE PAGINAÇÃO E CSS PAGED MEDIA (@page)
       ========================================================================== */
    @page {{
      size: A4 portrait;
      margin: 20mm 15mm 20mm 15mm;
      @top-center {{
        font-family: 'Cardo', serif;
        font-size: 8pt;
        letter-spacing: 0.15em;
        color: #7A0C0C;
        content: "Η ΘΕΙΑ ΛΕΙΤΟΥΡΓΙΑ ΤΟΥ ΑΓΙΟΥ ΙΩΑΝΝΟΥ ΤΟΥ ΧΡΥΣΟΣΤΟΜΟΥ";
      }}
      @bottom-center {{
        font-family: 'EB Garamond', serif;
        font-size: 9pt;
        color: #7A0C0C;
        content: counter(page);
      }}
    }}

    @page :first {{
      @top-center {{ content: normal; }}
      @bottom-center {{ content: normal; }}
    }}

    /* ==========================================================================
       RESETS E CONFIGURAÇÕES GERAIS DE VISUALIZAÇÃO E IMPRESSÃO
       ========================================================================== */
    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background-color: #EFECE6;
      font-family: 'Cormorant Garamond', 'Cormorant', Georgia, serif;
      font-size: 11.5pt;
      color: var(--text-main);
      font-size: 11pt;
      line-height: 1.5;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    /* Contentor com cercadura clássica maximalista */
    .page-frame {{
      max-width: 960px;
      margin: 25px auto;
      background-color: var(--bg-page);
      padding: 35px 42px;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.10), 0 1px 4px rgba(0, 0, 0, 0.06);
      border: 3px double var(--border-outer);
      outline: 1px solid var(--border-inner);
      outline-offset: -7px;
      position: relative;
    }}

    @media print {{
      body {{
        background-color: var(--bg-page);
        margin: 0;
        padding: 0;
      }}
      .page-frame {{
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
      }}
    }}

    /* ==========================================================================
       ELEMENTOS DECORATIVOS E SEPARADORES ORNAMENTAIS
       ========================================================================== */
    .byzantine-divider {{
      text-align: center;
      margin: 22px 0;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .byzantine-divider svg {{
      display: inline-block;
      max-width: 100%;
      height: auto;
    }}

    /* ==========================================================================
       CAPITULARES (DROP CAPS) E PARÁGRAFOS CONTÍNUOS
       ========================================================================== */
    .drop-cap::first-letter {{
      font-family: 'Cardo', serif;
      font-weight: 700;
      color: var(--rubric-crimson);
      float: left;
      font-size: 3.5em;
      line-height: 0.8;
      margin-right: 0.12em;
      margin-top: 0.05em;
      initial-letter: 3;
      text-shadow: 1px 1px 0px rgba(166, 138, 86, 0.35);
    }}

    .full-width-section {{
      margin: 20px 0;
      break-inside: auto;
    }}

    .full-width-section p {{
      text-align: justify;
      text-indent: 1.5em;
      margin: 6px 0;
      line-height: 1.55;
      hyphens: auto;
      -webkit-hyphens: auto;
    }}

    /* ==========================================================================
       FRONTISPÍCIO E CAPA LITÚRGICA
       ========================================================================== */
    .cover-section {{
      text-align: center;
      margin-bottom: 30px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .cover-cross {{
      font-size: 26pt;
      color: var(--rubric-crimson);
      margin-bottom: 8px;
    }}

    .main-title-greek {{
      font-family: 'Cardo', 'EB Garamond', serif;
      font-size: 17pt;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--rubric-crimson);
      margin: 4px 0 8px 0;
      line-height: 1.3;
      break-after: avoid;
    }}

    .main-title-pt {{
      font-family: 'Cardo', serif;
      font-size: 15pt;
      font-weight: 700;
      letter-spacing: 0.12em;
      color: var(--text-main);
      margin: 0 0 10px 0;
      line-height: 1.3;
      break-after: avoid;
    }}

    .liturgy-meta {{
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      font-style: italic;
      font-size: 12pt;
      color: var(--gold-accent);
      letter-spacing: 0.05em;
      margin: 6px 0 16px 0;
    }}

    .parish-card {{
      display: inline-block;
      border: 1px solid var(--gold-accent);
      background-color: var(--gold-subtle);
      padding: 12px 24px;
      margin: 12px auto;
      border-radius: 2px;
      max-width: 650px;
    }}

    .parish-title {{
      font-family: 'Cardo', serif;
      font-size: 10.5pt;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--rubric-crimson);
      margin-bottom: 4px;
    }}

    .parish-address, .parish-social {{
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      font-size: 11pt;
      color: var(--text-main);
      line-height: 1.4;
    }}

    .church-notice {{
      font-family: 'Cardo', serif;
      font-size: 8.5pt;
      letter-spacing: 0.12em;
      font-weight: 600;
      color: var(--rubric-crimson);
      margin-top: 12px;
      text-transform: uppercase;
    }}

    /* ==========================================================================
       TÍTULOS E SUBTÍTULOS DAS SECÇÕES
       ========================================================================== */
    .section-title {{
      font-family: 'Cardo', serif;
      font-size: 13.5pt;
      font-weight: 700;
      letter-spacing: 0.12em;
      color: var(--rubric-crimson);
      text-align: center;
      margin: 22px 0 12px 0;
      text-transform: uppercase;
      break-after: avoid;
      page-break-after: avoid;
    }}

    .section-subtitle {{
      font-family: 'Cardo', serif;
      font-size: 11.5pt;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--rubric-crimson);
      text-align: center;
      margin: 16px 0 8px 0;
      break-after: avoid;
      page-break-after: avoid;
    }}

    .rubric {{
      font-style: italic;
      color: var(--rubric-crimson);
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
    }}

    .rubric-block {{
      text-indent: 0 !important;
      text-align: justify;
      margin: 10px 0;
      padding-left: 12px;
      border-left: 2px solid var(--rubric-crimson);
    }}

    .rubric-feast {{
      font-family: 'Cardo', serif;
      font-size: 9pt;
      font-weight: 700;
      letter-spacing: 0.06em;
      color: var(--rubric-crimson);
    }}

    /* ==========================================================================
       GRANDE DOXOLOGIA E ORAÇÕES EM VERSÍCULOS
       ========================================================================== */
    .doxology-container {{
      margin: 14px 0;
    }}

    .doxology-verse {{
      margin: 7px 0;
      line-height: 1.5;
      text-align: justify;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .verse-num {{
      font-family: 'Cardo', serif;
      font-weight: 700;
      font-size: 9.5pt;
      color: var(--rubric-crimson);
      margin-right: 6px;
    }}

    /* ==========================================================================
       ORAÇÕES SECRETAS DO SACERDOTE (EM VOZ BAIXA)
       ========================================================================== */
    .secret-prayer-box {{
      background-color: #FAF7F0;
      border-left: 3px solid var(--rubric-crimson);
      border-right: 1px solid var(--gold-accent);
      border-top: 1px solid var(--gold-accent);
      border-bottom: 1px solid var(--gold-accent);
      padding: 14px 18px;
      margin: 16px 0;
      border-radius: 2px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .secret-prayer-title {{
      font-family: 'Cardo', serif;
      font-size: 9.5pt;
      font-weight: 700;
      color: var(--rubric-crimson);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      text-align: center;
      margin-bottom: 8px;
    }}

    .secret-prayer-text {{
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      font-size: 11.5pt;
      line-height: 1.5;
      color: var(--text-main);
      text-align: justify;
      hyphens: auto;
      -webkit-hyphens: auto;
    }}

    .antiphon-variations {{
      margin: 12px 0;
      line-height: 1.5;
    }}

    .antiphon-variations p {{
      text-indent: 0 !important;
      margin: 5px 0;
      text-align: justify;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .solemn-words {{
      font-family: 'Cardo', serif;
      font-weight: 700;
      font-size: 11pt;
      letter-spacing: 0.08em;
      color: var(--rubric-crimson);
      text-align: center;
      margin: 12px 0;
      text-indent: 0 !important;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .editorial-note {{
      font-style: italic;
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      color: var(--rubric-crimson);
      text-align: center;
      font-size: 10.5pt;
      margin: 12px 0;
      padding: 6px 12px;
      background-color: var(--gold-subtle);
      border: 1px dashed var(--gold-accent);
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    /* ==========================================================================
       TABELA LITÚRGICA A TRÊS COLUNAS (PARALELISMO RIGOROSO)
       ========================================================================== */
    .table-wrapper {{
      width: 100%;
      margin: 16px 0;
      break-inside: auto;
    }}

    .liturgy-table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      page-break-inside: auto;
    }}

    .liturgy-table col.col-greek {{ width: 33%; }}
    .liturgy-table col.col-translit {{ width: 33%; }}
    .liturgy-table col.col-portuguese {{ width: 34%; }}

    .liturgy-table thead {{
      display: table-header-group;
    }}

    .liturgy-table thead th {{
      font-family: 'Cardo', serif;
      font-size: 9pt;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--rubric-crimson);
      background-color: #F8F4EB;
      border-top: 1.5px solid var(--gold-accent);
      border-bottom: 1.5px solid var(--gold-accent);
      padding: 7px 8px;
      text-align: left;
    }}

    .liturgy-table tbody tr {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .liturgy-table tbody td {{
      padding: 4px 8px;
      vertical-align: top;
      word-wrap: break-word;
      overflow-wrap: break-word;
    }}

    /* Coluna 1: Grego Original */
    .liturgy-table td.col-greek {{
      font-family: 'EB Garamond', 'GFS Didot', serif;
      font-size: 10.5pt;
      line-height: 1.45;
      color: var(--text-main);
      text-align: left;
    }}

    /* Coluna 2: Transliteração Fonética */
    .liturgy-table td.col-translit {{
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      font-style: italic;
      font-size: 10.5pt;
      line-height: 1.45;
      color: var(--text-translit);
      text-align: left;
    }}

    /* Coluna 3: Tradução em Português */
    .liturgy-table td.col-portuguese {{
      font-family: 'Cormorant Garamond', 'Cormorant', serif;
      font-style: normal;
      font-size: 11pt;
      line-height: 1.45;
      color: var(--text-main);
      text-align: left;
    }}

    /* Linhas divisórias subtis entre versículos */
    .liturgy-table tr.liturgy-row td {{
      border-bottom: 1px solid rgba(166, 138, 86, 0.18);
    }}

    /* Linhas de anúncio do papel litúrgico (Sacerdote, Diácono, Coro) */
    .liturgy-table tr.actor-row {{
      break-after: avoid;
      page-break-after: avoid;
    }}

    .liturgy-table tr.actor-row td {{
      padding-top: 8px;
      padding-bottom: 1px;
      border-bottom: none;
    }}

    /* Papéis Litúrgicos: caixa alta (small-caps), negrito, vermelho litúrgico */
    .actor-tag {{
      font-family: 'Cardo', serif;
      font-variant: small-caps;
      font-weight: 700;
      color: var(--rubric-crimson);
      letter-spacing: 0.05em;
      font-size: 1.05em;
      display: inline-block;
    }}

    .liturgy-strong {{
      font-family: 'Cardo', serif;
      font-weight: 700;
      color: var(--rubric-crimson);
      letter-spacing: 0.04em;
    }}

    /* Banners e Títulos de Secção dentro da Tabela */
    .liturgy-table tr.section-banner-row td {{
      background: linear-gradient(90deg, rgba(166,138,86,0.12) 0%, rgba(122,12,12,0.10) 50%, rgba(166,138,86,0.12) 100%);
      border-top: 1.5px solid var(--gold-accent);
      border-bottom: 1.5px solid var(--gold-accent);
      padding: 9px 8px;
      text-align: center;
      font-family: 'Cardo', serif;
      font-weight: 700;
      font-size: 10.5pt;
      letter-spacing: 0.08em;
      color: var(--rubric-crimson);
      break-after: avoid;
      page-break-after: avoid;
    }}

    /* Evitar quebras orfãs em títulos */
    h1, h2, h3, h4, .section-title, .section-subtitle {{
      break-after: avoid;
      page-break-after: avoid;
    }}
  </style>
</head>
<body>

<div class="page-frame">

  <!-- ==========================================================================
       CAPA LITÚRGICA E IDENTIFICAÇÃO DA PARÓQUIA (PÁGINA 1)
       ========================================================================== -->
  <header class="cover-section">
    <div class="cover-cross" aria-hidden="true">☩</div>
    <h1 class="main-title-greek" lang="el">Η ΘΕΙΑ ΛΕΙΤΟΥΡΓΙΑ<br><span style="font-size: 0.85em;">ΤΟΥ ΑΓΙΟΥ ΙΩΑΝΝΟΥ ΤΟΥ ΧΡΥΣΟΣΤΟΜΟΥ</span></h1>
    <h2 class="main-title-pt">A DIVINA LITURGIA DE SÃO JOÃO CRISÓSTOMO</h2>
    <div class="liturgy-meta">Texto litúrgico para o fiel &bull; Setembro, 2026</div>

    <div class="parish-card">
      <div class="parish-title">PARÓQUIA DA SANTA DORMIÇÃO DA MÃE DE DEUS</div>
      <div class="parish-address">Rua Albuquerque Maranhão, 211 - Cambuci - São Paulo - SP</div>
      <div class="parish-social">Instagram: @paroquiaortodoxa.cambuci</div>
    </div>

    <div class="church-notice">☩ APÓS A DIVINA LITURGIA, FAVOR DEIXAR ESTE LIVRO NO BANCO ☩</div>
  </header>

  {byzantine_divider_svg}

  <!-- ==========================================================================
       PRÓLOGO (PÁGINA 1)
       ========================================================================== -->
  <section class="full-width-section prologue-section">
    <h3 class="section-title">PRÓLOGO</h3>
    <p class="drop-cap">A Santa Liturgia é o centro dos Santos Mistérios da Igreja fundada por Deus.</p>
    <p>A Santa Missa é o Mistério que nosso Senhor Jesus Cristo ofereceu a Seus discípulos na véspera de Sua morte na Cruz, quando lhes disse: "Desejei ardentemente comer convosco esta Páscoa, antes que padeça" (Lucas 22:15). Em seguida, após orar, agradecer e abençoá-los, deu-lhes o Pão e o Vinho como Seu próprio Corpo e Sangue, e continuou: "Fazei isto em minha memória".</p>
    <p>Este grande mistério do sacrifício incruento que celebra a Igreja, cumprindo o mandato do Senhor, para que todos nós, Seus fiéis membros, recordemos Sua paixão salvadora da Cruz vivificante, Sua morte durante três dias, Sua gloriosa Ressurreição, Sua ascensão aos Céus, Seu assento à direita de Deus Pai e Seu glorioso e terrível juízo final.</p>
    <p>O sincero arrependimento nos conduz à Santa Confissão de nossos pecados e, purificadas nossas almas, cheguemos com temor de Deus, com fé e amor à Santa Eucaristia, unindo-nos com Ele.</p>
    <p>Assistindo à Santa Liturgia, logramos concentração, devoção e o devido respeito e ordem.</p>
    <p>Com estas virtudes nos fazemos dignos de herdar o Reino dos Céus, que Deus, desde a criação do mundo, preparou para os que convivem de acordo com o Evangelho de nosso Senhor Jesus Cristo. Amém.</p>
  </section>

  {byzantine_divider_svg}

  <!-- ==========================================================================
       OFÍCIO MATUTINO E GRANDE DOXOLOGIA (PÁGINA 2)
       ========================================================================== -->
  <section class="full-width-section orthros-section">
    <h3 class="section-title">OFÍCIO MATUTINO</h3>
    <p class="rubric rubric-block">Terminada a Prótese (preparação do pão e do vinho que, pela força inacessível do Espírito Santo, serão transformados no Corpo e Sangue de Cristo), o coro recita o ofício matutino (Orthros) e começa imediatamente o hino da Grande Doxologia.</p>
    
    <h3 class="section-title">GRANDE DOXOLOGIA</h3>
    <div class="doxology-container">
      <div class="doxology-verse"><span class="verse-num">1.</span> Glória a Ti que nos fizeste ver a verdadeira Luz.</div>
      <div class="doxology-verse"><span class="verse-num">2.</span> Glória a Deus no mais alto dos Céus e Paz na terra aos homens a quem Ele ama.</div>
      <div class="doxology-verse"><span class="verse-num">3.</span> Nós Te louvamos, nós Te bendizemos, nós Te adoramos, nós Te glorificamos, nós Te damos graças pela Tua imensa Glória.</div>
      <div class="doxology-verse"><span class="verse-num">4.</span> Senhor Deus, Rei dos Céus, Pai Todo-Poderoso, Senhor Filho Único Jesus Cristo e o Espírito Santo.</div>
      <div class="doxology-verse"><span class="verse-num">5.</span> Senhor Deus, Cordeiro de Deus, Filho de Deus Pai. Tu que tiras o pecado do mundo, tem piedade de nós, Tu que tiras o pecado do mundo.</div>
      <div class="doxology-verse"><span class="verse-num">6.</span> Acolhe a nossa súplica, Tu que estás sentado à direita do Pai, tende piedade de nós.</div>
      <div class="doxology-verse"><span class="verse-num">7.</span> Amém.</div>
      <div class="doxology-verse"><span class="verse-num">8.</span> Só Tu és o Santo, só Tu és o Senhor, Jesus Cristo, para a Glória de Deus Pai.</div>
      <div class="doxology-verse"><span class="verse-num">9.</span> Cada dia Te bendirei e cantarei eternamente o Teu nome glorioso.</div>
      <div class="doxology-verse"><span class="verse-num">10.</span> Tu és bendito, Senhor, Deus dos nossos Pais, digno de louvor e glória eternamente. Amém.</div>
      <div class="doxology-verse"><span class="verse-num">11.</span> Senhor, que a Tua misericórdia esteja sobre nós, segundo a esperança que desde sempre depositamos em Ti.</div>
      <div class="doxology-verse"><span class="verse-num">12.</span> Tu és bendito, Senhor; ensina-nos os Teus mandamentos (3x).</div>
      <div class="doxology-verse"><span class="verse-num">13.</span> Senhor nosso Deus, que és o nosso refúgio, ensina-nos a fazer a Tua vontade; pois em Ti está a fonte da vida e é na Tua luz que vemos a luz. Concede a Tua misericórdia àqueles que Te conhecem.</div>
      <div class="doxology-verse"><span class="verse-num">14.</span> Senhor, Tu que és o nosso refúgio de geração em geração, cura as nossas almas e tem piedade de nós que pecamos contra Ti.</div>
      <div class="doxology-verse"><span class="verse-num">15.</span> Concede a Tua misericórdia àqueles que Te conhecem. Santo Deus, Santo Forte, Santo Imortal, tende piedade de nós (3x). Glória ao Pai, ao Filho e ao Espírito Santo, agora e sempre e pelos séculos dos séculos. Amém. Santo Deus, Santo Forte, Santo Imortal, tende piedade de nós.</div>
    </div>
  </section>

  {byzantine_divider_svg}

  <!-- ==========================================================================
       TABELA 1: ENÁRXIS E LITANIA DA PAZ (PÁGINA 3)
       ========================================================================== -->
  {render_table(tbl1_rows)}

  <!-- ==========================================================================
       15. SÚPLICAS (SENTADOS) E ORAÇÃO DA PRIMEIRA ANTÍFONA (PÁGINA 4)
       ========================================================================== -->
  <section class="full-width-section">
    <h4 class="section-subtitle">15. SÚPLICAS (SENTADOS)</h4>
    <p class="rubric">Enquanto o Diácono recita a Grande Ladainha, o Sacerdote reza em voz baixa a oração da Primeira Antífona:</p>
    <div class="secret-prayer-box">
      <div class="secret-prayer-title">☩ Oração da Primeira Antífona (em voz baixa) ☩</div>
      <div class="secret-prayer-text drop-cap">NOSSO DEUS, CUJO PODER É INEXPRIMÍVEL E A GLÓRIA INCOMPREENSÍVEL, CUJA BONDADE É INDIZÍVEL E O AMOR PELOS HOMENS INEFÁVEL, VOLVEI O VOSSO OLHAR SOBRE NÓS E SOBRE ESTA SANTA IGREJA, E CONCEDE A NÓS E ÀQUELES QUE REZAM CONOSCO OS DONS INFINITOS DA TUA MISERICÓRDIA.</div>
    </div>
  </section>

  <!-- ==========================================================================
       TABELA 2: LITANIA CONTINUADA, PRIMEIRA ANTÍFONA E PEQUENA LADAINHA (PÁGINA 4)
       ========================================================================== -->
  {render_table(tbl2_rows)}

  <!-- ==========================================================================
       ORAÇÃO DA SEGUNDA ANTÍFONA E 18. SEGUNDA ANTÍFONA COM HINOS FESTIVOS (PÁGINA 5)
       ========================================================================== -->
  <section class="full-width-section">
    <p class="rubric">O sacerdote, entretanto, diz em voz baixa a oração da Segunda Antífona:</p>
    <div class="secret-prayer-box">
      <div class="secret-prayer-title">☩ Oração da Segunda Antífona (em voz baixa) ☩</div>
      <div class="secret-prayer-text drop-cap">SENHOR, DEUS NOSSO, SALVA O TEU POVO, ABENÇOA A TUA HERANÇA, GUARDA A TUA IGREJA, SANTIFICA AOS QUE AMAM O ESPLENDOR DE TUA CASA. GLORIFICA-OS, EM TROCA, COM O TEU DIVINO PODER, E NÃO NOS ABANDONES, A NÓS QUE CONFIAMOS EM TI.</div>
    </div>

    <h4 class="section-subtitle">18. SEGUNDA ANTÍFONA</h4>
    <div class="antiphon-variations">
      <p><strong class="actor-tag">CORO:</strong> Aos Domingos e no dia de Páscoa: Salva-nos, ó Filho de Deus, que ressurgiste dos mortos, a nós que a ti salmodiamos, aleluia! (3x).</p>
      <p>Durante a semana e nas festas principais: Salva-nos, ó Filho de Deus, admirável em teus santos, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">NATAL:</strong>... que nasceste da Virgem, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">CIRCUNCISÃO:</strong>...que foste circuncidado na carne, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">EPIFANIA:</strong>...que foste batizado por João no Jordão, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">HYPAPANTE:</strong>...que foste carregado nos braços do justo Simeão, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">ANUNCIAÇÃO:</strong>...que te encarnaste por nós, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">RAMOS:</strong>...que montaste num jumentinho, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">ASCENSÃO:</strong>...que subiste dentre nós com glória para os céus, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">PENTECOSTES:</strong> Salva-nos, ó Consolador bondoso, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">TRANSFIGURAÇÃO:</strong>... que te transfiguraste sobre o monte Tabor, a nós que a ti salmodiamos, aleluia!</p>
      <p><strong class="rubric-feast">EXALTAÇÃO DA SANTA CRUZ:</strong>...que foste crucificado na carne, a nós que a ti salmodiamos, aleluia!</p>
    </div>
  </section>

  <!-- ==========================================================================
       TABELA 3: PEQUENA LADAINHA, TERCEIRA ANTÍFONA, ENTRADA DO EVANGELHO,
       TRISÁGIO, LEITURAS SAGRADAS E SANTO EVANGELHO (PÁGINAS 6 A 9)
       ========================================================================== -->
  {render_table(tbl3_rows)}

  <!-- ==========================================================================
       NOTA EDITORIAL E TABELA 4: LITANIA PELA IGREJA, GRANDE ENTRADA,
       OFERTÓRIO, CREDO, SANTA ANÁFORA E INSTITUIÇÃO (PÁGINAS 10 A 23)
       ========================================================================== -->

  {render_table(tbl4_rows)}

  <!-- ==========================================================================
       ANAMNESE, CONSAGRAÇÃO E EPICLESIS SOLENE (PÁGINAS 24 E 25)
       ========================================================================== -->
  <section class="full-width-section epiclesis-section">
    {byzantine_divider_svg}
    <p class="rubric"><strong>SACERDOTE: continua a oração em voz baixa.</strong></p>
    <p class="drop-cap">Lembrando-nos, pois, deste mandamento salutar e de todas as coisas que foram feitas por causa de nós: da Cruz, do Sepulcro, da Ressurreição ao terceiro dia, da Ascensão aos céus, do assento à direita do Pai e também do glorioso e segundo advento... <span class="rubric">(neste momento o diácono ou o sacerdote, pondo a mão direita sobre a esquerda, levanta um pouco, com a direita o disco e com a esquerda o cálice, e faz com eles o sinal da cruz, dizendo):</span></p>
    <p class="solemn-words">Os Teus dons a Ti oferecemos, em tudo e por tudo.</p>
    <p><strong class="actor-tag">CORO:</strong> NÓS TE LOUVAMOS, NÓS TE BENDIZEMOS, NÓS TE AGRADECEMOS, SENHOR, E TE INVOCAMOS, DEUS NOSSO.</p>
    <p class="rubric">Depondo os santos dons novamente na santa mesa, fazem três metânias. O sacerdote recita em voz baixa:</p>
    <p class="secret-prayer-text">Nós Vos oferecemos ainda esta adoração vocal e incruenta, nós Vos invocamos, nós Vos rogamos e Vos suplicamos. Enviai, pois, o Vosso Espírito Santo sobre nós e sobre estes dons aqui dispostos.</p>
    <p class="rubric">De braços erguidos, o sacerdote reza o Tropário da Hora Terça:</p>
    <p><strong class="actor-tag">S.</strong> Senhor, que à hora terceira enviaste aos Apóstolos o Vosso Santo Espírito, pela Vossa misericórdia não O afastes de nós, e renova-nos a nós que humildemente Vos apresentamos as nossas súplicas.</p>
    <p><strong class="actor-tag">D./S.</strong> Cria em mim, ó Deus, um coração puro, e renova em mim um espírito reto.</p>
    <p><strong class="actor-tag">S.</strong> Senhor, que à hora terceira...</p>
    <p><strong class="actor-tag">D./S.</strong> Não me afastes de Vossa face e não retires de mim o Vosso Santo Espírito.</p>
    <p><strong class="actor-tag">S.</strong> Senhor, que à hora terceira...</p>
    <p><strong class="actor-tag">DIÁCONO:</strong> <span class="rubric">inclinando a cabeça, aponta com o seu orárion o santo pão e diz em voz baixa:</span> Abençoa, senhor, o santo pão!</p>
    <p><strong class="actor-tag">SACERDOTE:</strong> <span class="rubric">inclinando-se, abençoa três vezes com o sinal da cruz o santo pão, e diz em voz baixa, continuando a oração:</span><br>E fazei deste pão o Precioso Corpo de Vosso Cristo.</p>
    <p><strong class="actor-tag">DIÁCONO:</strong> Amém. <span class="rubric">E apontando o orárion para o santo cálice, diz ao sacerdote:</span> Abençoa, senhor, o Santo Cálice.</p>
    <p><strong class="actor-tag">SACERDOTE:</strong> <span class="rubric">abençoando o cálice diz:</span><br>E quanto ao que se contém neste cálice, o Precioso Sangue de Vosso Cristo.</p>
    <p><strong class="actor-tag">DIÁCONO:</strong> <span class="rubric">apontando mais uma vez o orárion para ambas as espécies, diz:</span> Abençoa, senhor, ambos os dons.</p>
    <p><strong class="actor-tag">SACERDOTE:</strong> <span class="rubric">abençoa ambos os dons, dizendo:</span><br>Transformando-os por Vosso Espírito Santo.</p>
    <p><strong class="actor-tag">DIÁCONO:</strong> Amém, amém, amém. <span class="rubric">Diácono e Sacerdote fazem uma profunda inclinação de adoração. O Diácono ou o Sacerdote toma o pequeno véu e o agita sobre os santos mistérios.</span></p>
    <p><strong class="actor-tag">SACERDOTE:</strong> <span class="rubric">em voz baixa recita a seguinte oração:</span><br>Para que eles sirvam aos comungantes para o despertar da alma e a remissão dos pecados, para a comunhão com o Vosso Espírito Santo, para terem a plenitude do Reino celeste, para terem um motivo de confiança perante Vós e não de juízo ou condenação.<br>Oferecemos-Vos esta oblação racional também por aqueles que descansam na fé: pelos antepassados, pais, patriarcas, profetas, apóstolos, pregadores, evangelizadores, mártires, confessores, ascetas e por toda a alma justa que morreu na fé;</p>
    {byzantine_divider_svg}
  </section>

  <!-- ==========================================================================
       TABELA 5: AXION ESTIN, DÍPTICOS, ORAÇÃO DOMINICAL (PAI NOSSO)
       E SANTA COMUNHÃO DOS FIÉIS (PÁGINAS 27 A 39)
       ========================================================================== -->
  {render_table(tbl5_rows)}

  <!-- ==========================================================================
       ORAÇÕES FINAIS E AÇÃO DE GRAÇAS APÓS A COMUNHÃO (PÁGINA 40)
       ========================================================================== -->
  <section class="full-width-section post-communion-section">
    {byzantine_divider_svg}
    <h3 class="section-title">ORAÇÕES FINAIS</h3>
    <h4 class="section-subtitle">45. AÇÃO DE GRAÇAS APÓS A COMUNHÃO</h4>
    <p><strong class="actor-tag">C.:</strong> AGRADECEMOS-TE, Ó SENHOR BENFEITOR DE NOSSAS ALMAS, PORQUE NO PRESENTE DIA TE DIGNASTE FAZER-NOS PARTICIPANTES DE TEUS MISTÉRIOS CELESTES E IMORTAIS. ENDIREITA O NOSSO CAMINHO, CONFIRMA-NOS A TODOS EM TEU TEMOR, GUARDA A NOSSA VIDA, ASSEGURA OS NOSSOS PASSOS, PELAS ORAÇÕES E SÚPLICAS DA GLORIOSA MÃE DE DEUS E SEMPRE VIRGEM MARIA E DE TODOS OS SANTOS.</p>
    <p><span class="rubric">No Natal canta-se:</span> O TEU NATAL, Ó CRISTO NOSSO DEUS, FEZ RAIAR NO MUNDO A LUZ DO CONHECIMENTO; POR ELE, OS ADORADORES DAS ESTRELAS APRENDERAM DE UMA ESTRELA A ADORAR-TE A TI, SOL DA JUSTIÇA, E A CONHECER-TE A TI, ORIENTE DO ALTO. SENHOR, GLÓRIA A TI!</p>
    <p><span class="rubric">Na Páscoa canta-se:</span> CRISTO RESSUSCITOU DOS MORTOS, PISANDO A MORTE COM A MORTE E DANDO A VIDA AOS SEPULTADOS.</p>
    <p><strong class="actor-tag">SACERDOTE:</strong> <span class="rubric">Dobra o antimênsio. Levanta o Santo Evangelho, faz com ele o sinal da cruz, coloca-o sobre o antimênsio já dobrado e exclama:</span><br>PORQUE TU ÉS A NOSSA SANTIFICAÇÃO E A TI RENDEMOS GLÓRIA, AO PAI, AO FILHO E AO ESPÍRITO SANTO, AGORA E SEMPRE E PELOS SÉCULOS DOS SÉCULOS.</p>
    <p><strong class="actor-tag">CORO:</strong> AMÉM.</p>
    {byzantine_divider_svg}
  </section>

  <!-- ==========================================================================
       TABELA 6: RITO FINAL, APÓLYSIS, BÊNÇÃO FINAL, DESPEDIDA E ANTIDORON (PÁGINAS 41 A 43)
       ========================================================================== -->
  {render_table(tbl6_rows)}

  <footer style="text-align: center; margin-top: 30px; font-family: 'Cardo', serif; font-size: 9pt; color: var(--gold-accent); letter-spacing: 0.15em;">
    ☩ ΔΟΞΑ ΤΩ ΘΕΩ ΠΑΝΤΩΝ ΕΝΕΚΕΝ ☩
  </footer>

</div>

</body>
</html>
'''

with open('divina_liturgia.html', 'w', encoding='utf-8') as f:
    f.write(html_doc)

print(f"divina_liturgia.html updated successfully! File size: {os.path.getsize('divina_liturgia.html')} bytes")
