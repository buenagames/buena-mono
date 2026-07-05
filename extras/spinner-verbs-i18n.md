# Spinner verbs in other languages — research notes (PEFINGTS)

Research for localizing `spinner-verbs.json` beyond English, covering
**P**ortuguese, **E**nglish, **F**rench, **I**talian, **N**ederlands (Dutch),
**G**erman, **T**urkish, **S**panish.

## State of the art

- Claude Code's `spinnerVerbs` setting accepts arbitrary UTF-8 strings
  (`mode: "replace"` / `"append"`), so localized packs need no tooling —
  just a verbs array per language.
- The only community localization found is **Korean**
  ([jaehongpark-agent/claude-code-spinner-verbs](https://github.com/jaehongpark-agent/claude-code-spinner-verbs)),
  which pairs each English verb with a Korean rendering
  ("Accomplishing 완수하는중"). The large themed collections
  ([wynandw87](https://github.com/wynandw87/claude-code-spinner-verbs), 2,534
  verbs / 98 categories; [stoodiohq](https://github.com/stoodiohq/spinner-verbs);
  [spinnerverbs.com](https://spinnerverbs.com/)) are English-only.
  **No European-language pack exists yet** — a PEFINGTS set would be first.
- Buena Mono covers all glyphs these languages need (ã ç é ï ü ğ ş İ ı …)
  and ships `locl` for Turkish/Azerbaijani i/ı casing — a localized spinner
  doubles as a live demo of the font's language support.

## The linguistic problem

English spinner verbs work because the bare *-ing* participle reads as
"currently happening" with no subject. Not every language has an equivalent
one-word progressive, so each needs its own idiomatic *loading-message*
register — the form native UIs already use for "Loading…".

| Lang | Idiomatic form | Pattern | "Percolating…" becomes |
|------|----------------|---------|------------------------|
| **E**nglish | present participle | *-ing* | Percolating… |
| **S**panish | gerundio (standard UI form, cf. "Cargando…") | *-ando / -iendo* | Percolando… |
| **P**ortuguese | gerúndio (pt-BR; cf. "Carregando…") | *-ando / -endo / -indo* | Percolando… — pt-PT prefers *a* + infinitive: "A percolar…" |
| **I**talian | gerundio (cf. "Elaborando…") | *-ando / -endo* | Percolando… |
| **F**rench | **noun**, not participle — French UI says "Chargement…", never "Chargeant…" | *-age / -tion / -ment* | Percolation… |
| **N**ederlands (Dutch) | *aan het* + infinitive (colloquial progressive), or bare infinitive-as-noun (cf. "Laden…") | *aan het X-en* | Aan het percoleren… / Percoleren… |
| **G**erman | *am*-Progressiv (colloquial, playful — fits the joke) or bare nominalized infinitive (cf. "Laden…") | *Am X-en* / *X-en* | Am Perkolieren… / Perkolieren… |
| **T**urkish | 3rd-person present progressive — exactly how Turkish UIs already phrase it ("Yükleniyor…" = "it is loading") | *-iyor* | Demleniyor… |

Notes:
- **French** is the odd one out: the participle ("Percolant…") reads as
  literary/wrong in UI. Nominalizations in *-age* keep the humor
  ("Mijotage…", "Tambouille…").
- **German** *am*-Progressiv ("Am Grübeln…") is regional-colloquial, which
  *is* the right register for this feature; bare infinitives are the neutral
  fallback. Bonus: *spinnen* is a real German verb (to spin / to be nuts) —
  "Am Spinnen…" is the perfect pun for a *spinner*.
- **Turkish** is agglutinative gold: one word carries verb + progressive +
  subject ("Kafa yoruyor…" = "it's racking its brain").
- **Dutch** *aan het* keeps the ongoing feel; bare infinitives are shorter
  and match system UI.
- **pt-PT vs pt-BR**: gerúndio is the safe default (universally understood,
  standard in software), but a pt-PT purist pack would use "A matutar…".

## Starter sets (12 per language, tone-matched to the English pack)

Translated in spirit — coffee, cooking, and overthinking metaphors — not literally.

**Español** — `Cavilando`, `Maquinando`, `Rumiando`, `Percolando`,
`Fermentando`, `Amasando`, `Tramando`, `Garabateando`, `Destilando`,
`Devanándose los sesos`, `Afinando`, `Conjurando`

**Português (BR)** — `Cismando`, `Matutando`, `Maquinando`, `Fermentando`,
`Coando o café`, `Amassando`, `Tramando`, `Rabiscando`, `Lapidando`,
`Devaneando`, `Destilando`, `Cozinhando em fogo baixo`

**Italiano** — `Rimuginando`, `Almanaccando`, `Arrovellandosi`, `Macinando`,
`Lievitando`, `Sobbollendo`, `Tramando`, `Cesellando`, `Rovistando`,
`Fantasticando`, `Distillando`, `Orchestrando`

**Français** — `Percolation`, `Mijotage`, `Rumination`, `Gribouillage`,
`Cogitation`, `Tambouille`, `Distillation`, `Échafaudage`, `Pétrissage`,
`Machination`, `Remue-méninges`, `Alchimie`

**Nederlands** — `Aan het prakkiseren`, `Aan het broeien`, `Aan het malen`,
`Aan het knutselen`, `Aan het sudderen`, `Aan het brouwen`,
`Aan het piekeren`, `Aan het puzzelen`, `Aan het kneden`,
`Aan het polijsten`, `Aan het mijmeren`, `Aan het dromen`

**Deutsch** — `Am Grübeln`, `Am Brodeln`, `Am Tüfteln`, `Am Knobeln`,
`Am Brauen`, `Am Kneten`, `Am Simmern`, `Am Feilen`, `Am Spinnen`,
`Am Werkeln`, `Am Sinnieren`, `Am Destillieren`

**Türkçe** — `Demleniyor`, `Mayalanıyor`, `Kıvamına geliyor`, `Düşünüyor`,
`Kurcalıyor`, `Harmanlıyor`, `Yoğruluyor`, `Damıtılıyor`, `Pişiyor`,
`Cilalanıyor`, `Kafa yoruyor`, `Mırıldanıyor`

## Usage

Any set drops into `~/.claude/settings.json` exactly like the English pack:

```jsonc
{
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": ["Demleniyor", "Mayalanıyor", "Kafa yoruyor", "…"]
  }
}
```

## Possible next step

Ship full packs as `extras/spinner-verbs.<lang>.json` (es, pt, it, fr, nl,
de, tr) expanded to ~50 verbs each, and let the minisite's spinner section
cycle through languages as a live demo of Buena Mono's 621-language coverage.
