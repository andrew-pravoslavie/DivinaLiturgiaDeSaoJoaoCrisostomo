
---

```markdown
# BRIEFING DE ENGENHARIA TIPOGRÁFICA E FRONT-END
**Tarefa:** Converter o ficheiro `Divina Liturgia.md` num ficheiro autónomo `divina_liturgia.html` (com CSS embutido na tag `<style>`), projetado para exportação em PDF de altíssima fidelidade estética, no estilo litúrgico bizantino/clássico, maximalista e formal.

---

### 1. REQUISITOS DE DESIGN E TIPOGRAFIA

1. **Paleta de Cores Litúrgica:**
   - **Fundo de Página:** `#FFFDF9` (marfim muito subtil, ideal para leitura e impressão).
   - **Tinta Principal (Corpo do texto):** `#1A1816` (preto carvão quente de alta densidade).
   - **Rubro Litúrgico (Rubricas, títulos secundários, papéis litúrgicos, cruzes decorativas):** `#8B1E1E` ou `#7A0C0C` (carmesim profundo/sangue de boi).
   - **Fios e Ornamentos:** `#A68A56` (ouro velho/bronze) e `#7A0C0C`.

2. **Fontes Tipográficas (via Google Fonts no `<head>`):**
   - **Títulos e Aberturas:** `'Cinzel Decorative'`, `'Cinzel'`, serif ou `'GFS Didot'`.
   - **Corpo do Texto (Latino, Grego e Transliteração):** `'EB Garamond'`, com pesos 400, 500, 600, 700 e os respetivos itálicos. O EB Garamond suporta nativamente todo o alfabeto grego politónico e diacríticos latinos.
   - **Fonte Secundária/Alternativa:** `'Cardo'` ou serif clássica.

3. **Maximalismo Ornamental:**
   - **Moldura Externa de Página:** Criar uma cercadura clássica com linha dupla (uma espessa e outra fina) nas margens da página via CSS `@page` ou via contentor `.page-frame`.
   - **Separadores e Glifos:** Usar separadores com ornamentos litúrgicos em SVG vetorial embutido ou glifos Unicode clássicos (ex.: `☩`, `✠`, `❦`, `✦`, `⚜`) entre secções e orações.
   - **Capitulares (Drop Caps):** Nas orações corridas em voz baixa e prólogos, utilizar capitulares decorativas (`::first-letter` com fonte ornamentada, cor vermelha litúrgica, 3 linhas de altura com `initial-letter: 3` e fallback com `float: left`).

---

### 2. ARQUITETURA DE PAGINAÇÃO E CSS PAGED MEDIA (`@page`)

Configure o CSS para impressão rigorosa:
```css
@page {
  size: A4 portrait; /* ou Letter, conforme a necessidade */
  margin: 20mm 15mm 20mm 15mm;
  @top-center {
    font-family: 'Cinzel', serif;
    font-size: 8pt;
    letter-spacing: 0.15em;
    color: #7A0C0C;
    content: "Η ΘΕΙΑ ΛΕΙΤΟΥΡΓΙΑ ΤΟΥ ΑΓΙΟΥ ΙΩΑΝΝΟΥ ΤΟΥ ΧΡΥΣΟΣΤΟΜΟΥ";
  }
  @bottom-center {
    font-family: 'EB Garamond', serif;
    font-size: 9pt;
    content: counter(page);
  }
}

@page :first {
  @top-center { content: normal; }
  @bottom-center { content: normal; }
}

```

* **Evitar Quebras Traumáticas:**
* Aplique `break-inside: avoid;` e `page-break-inside: avoid;` em cada bloco de versículo, oração ou linha litúrgica da tabela.
* Títulos (`h1`, `h2`, `h3`) devem ter `break-after: avoid;`.



---

### 3. ESTRUTURAÇÃO DO CONTEÚDO LITÚRGICO

1. **Secções a Três Colunas (Diálogos e Orações Paralelas):**
* Não use tabelas genéricas não estilizadas. Utilize uma grelha rígida ou tabela tipográfica com cabeçalho fixo:
* Coluna 1: **Grego Original** (alinhado à esquerda, corpo 10.5pt, itálico leve ou regular).
* Coluna 2: **Transliteração Fonética** (corpo 9.5pt, itálico, tom ligeiramente rebaixado ou fonte ligeiramente condensada).
* Coluna 3: **Tradução em Português** (corpo 10.5pt, regular).


* As rubricas dos papéis litúrgicos (**Ι / S**, **Δ / D**, **Λ / C**) devem surgir em **caixa alta (small-caps), negrito e em vermelho litúrgico (`#7A0C0C`)**.


2. **Secções Corridas de Página Inteira:**
* Prólogo, Grande Doxologia, Orações secretas do Sacerdote, Credo e Oração Diante do Ícone:
* Diagramar em bloco único justificado, com recuo de parágrafo clássico (`text-indent: 1.5em`), hífenização ativada (`hyphens: auto;`) e rubricas de instruções com estilo `font-style: italic; color: #7A0C0C;`.


3. **Fidelidade Textual Absoluta:**
* Transcreva ipsis verbis todo o conteúdo contido em `Divina Liturgia.md`.
* Mantenha rigorosamente todos os acentos, espíritos do grego, diacríticos da transliteração fonética (como "ö", "ê", dígrafos) e as repetições rituais.
* Não resuma, não modernize palavras e não remova nenhuma rubrica litúrgica.



---

### 4. PLANO DE EXECUÇÃO EM FASES

* **Fase 1: Preparação do Esqueleto**
* Declarar documento HTML5 (`lang="pt"` com trechos em `lang="el"`).
* Incluir as fontes do Google Fonts (`Cinzel`, `Cinzel Decorative`, `EB Garamond`, `Cardo`).
* Estabelecer a folha de estilos base de reset e configurações de impressão (`@media print` e regras de ecrã para pré-visualização fidedigna).


* **Fase 2: Componentes Litúrgicos**
* Desenvolver a classe `.liturgy-grid` / `.liturgy-table` para o paralelismo a três colunas, garantindo que as linhas grego-transliteração-português permaneçam rigorosamente alinhadas horizontalmente linha a linha.
* Desenvolver os estilos para `.rubric` (vermelho), `.actor-tag` (papel litúrgico), `.drop-cap` e `.divider-ornament`.


* **Fase 3: Transcrição e Injeção do Conteúdo**
* Inserir integralmente o texto do ficheiro `Divina Liturgia.md`, mapeando cada trecho para o seu respetivo contentor sem saltar nenhuma oração ou página.


* **Fase 4: Validação Final**
* Verificar se todas as orações secretas, hinos e aclamações estão no documento.
* Garantir que o ficheiro final é 100% autónomo (HTML com CSS interno) e pode ser aberto diretamente em qualquer navegador para "Guardar como PDF" com máxima qualidade gráfica.



```

***

### Como executar após o Opus Agent gerar o ficheiro:
1. Abra o ficheiro `divina_liturgia.html` gerado no **Google Chrome** ou **Chromium**.
2. Pressione `Ctrl + P` (ou `Cmd + P`).
3. Em **Destino**, escolha **Guardar como PDF**.
4. Em **Mais definições**:
   - Tamanho do papel: **A4** (ou o configurado no CSS).
   - Margens: **Nenhuma** (para que as margens do CSS `@page` governem o layout).
   - Ative a opção **Gráficos de segundo plano** (*Background graphics*).

```
