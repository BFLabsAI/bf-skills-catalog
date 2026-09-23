# Design System — Inteligência Comercial

Sistema de peças de marca da **Inteligência Comercial / Ramon Pessoa /
R7 Treinamentos**. 28 templates em canvas fixo, sete categorias, operados por
agentes CLI (Claude Code, Codex, opencode) ou à mão no navegador.

Preto quente, branco e um vermelho. Archivo condensada sobre Poppins.
Cada arquivo é um canvas único que exporta em PNG ou PDF.

---

## Instalação

```bash
git clone git@github.com:<org>/ic-design-system.git
cd ic-design-system
npm install          # instala Playwright + Chromium
```

Sem dependência de rede em runtime: as fontes estão em `assets/fonts/`.

---

## Uso

```bash
npm run export                              # exporta as 28 peças → out/
npm run export -- ad-4x5-follow-up          # uma peça
npm run export -- --scale 1 quote-1x1-caixa-e-rei
npm run export:pdf -- onepager-a4-proposta  # documento em PDF
npm run serve                               # vitrine em http://localhost:4180
```

O script ajusta o **viewport para a dimensão exata do `.canvas`** antes do
screenshot. É isso que garante que um template de 1080×1350 saia exatamente
1080×1350 (ou 2160×2700 em `@2x`, o padrão), sem sobra lateral.

---

## Estrutura

```
ic-design-system/
├── SKILL.md          instruções para o agente CLI
├── DESIGN.md         regras de decisão: cor, tipografia, voz, 12 regras duras
├── brand-spec.md     os 6 tokens em OKLch com a origem medida de cada um
├── surfaces.md       as 7 categorias: canvas, safe area, --scale, restrições
├── checklist.md      P0 / P1 / P2 + "The Ramon Test"
├── tokens.css        fonte única de verdade dos valores
├── index.html        vitrine navegável das 28 peças
├── templates/        28 peças + _layout.css (composição) + _seed.html (base)
├── scripts/export.mjs
├── docs/             guia de identidade: método PIC, voz, números canônicos
└── assets/
    ├── fonts/        Archivo · Poppins · JetBrains Mono (locais)
    ├── logos/        marcas originais
    ├── derivadas/    logo clara/escura, recortes de rosto prontos
    └── fotos/        banco otimizado (2400px), nome por enquadramento
```

---

## Como trocar a marca inteira

Todos os 28 templates leem `tokens.css`. Trocar o bloco `:root` muda a
biblioteca inteira — nenhum template precisa ser reescrito.

| Token | Valor | Papel |
|---|---|---|
| `--bg` | `#090707` | Canvas (preto quente, não preto puro) |
| `--surface` | `#151111` | Card, faixa, bloco elevado |
| `--border` | `#2E2626` | Filete de 1px |
| `--fg` | `#FFFFFF` | Manchete, número |
| `--muted` | `#B4ACAC` | Corpo, legenda |
| `--accent` | `#FF0A05` | Vermelho exato da logo IC |

A escala tipográfica é escrita para um canvas de 1080px. Cada superfície
declara só o seu `--scale` (A4 = 0.34 · 640px = 0.60 · 1920 = 1.60). É isso
que faz um quote card 1:1 e um one-pager A4 parecerem o mesmo sistema.

---

## Publicar na VPS

### Opção A — vitrine estática (Caddy)

```bash
ssh vps
git clone git@github.com:<org>/ic-design-system.git /var/www/ds
```

```caddyfile
# /etc/caddy/Caddyfile
ds.seudominio.com.br {
    root * /var/www/ds
    file_server
    encode gzip
    basic_auth {
        equipe <hash-do-caddy-hash-password>
    }
}
```

```bash
caddy hash-password        # gera o hash da senha
systemctl reload caddy
```

TLS é automático. A vitrine fica em `https://ds.seudominio.com.br`.

### Opção B — repositório para os agentes

Se o objetivo é só alimentar os agentes CLI, não precisa servir HTTP: basta o
clone no servidor onde eles rodam. Instale a skill apontando para o clone:

```bash
ln -s /var/www/ds ~/.agents/skills/ic-design-system
```

Ou publique como pacote de skill:

```bash
npx skills add https://github.com/<org>/ic-design-system --global -y
```

Para a skill ser encontrada por esse instalador, o `SKILL.md` precisa estar na
raiz do repositório — está.

### Atualização

```bash
cd /var/www/ds && git pull && npm install
```

---

## Peso

| Item | Tamanho |
|---|---|
| Código, docs e templates | ~200 KB |
| Fontes | 476 KB |
| Logos e derivadas | ~700 KB |
| Fotos (2400px, otimizadas) | 6,8 MB |
| **Total do repositório** | **~8 MB** |

As fotos originais (226 MB) e as referências de criativo **não entram no
repositório** — ficam no arquivo de trabalho. Se precisar delas versionadas,
use Git LFS num repositório separado.

---

## Licença e uso

Material proprietário da R7 Treinamentos. As fotografias de Ramon Pessoa e as
marcas Inteligência Comercial® e R7 Treinamentos não são de uso livre.
