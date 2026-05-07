# stacks

CLI for managing Magic: The Gathering card collections. Supports set operations across formats (Arena, CSV, Moxfield) and Scryfall enrichment.

## Installation

```bash
poetry install
```

## Commands

### Set Operations

**`union`** — combine all cards from two stacks

```bash
stacks union deck1.arena deck2.arena combined.arena
stacks union collection.csv new_cards.csv updated_collection.csv
```

**`intersection`** — cards that appear in both stacks

```bash
stacks intersection deck1.arena deck2.arena shared.arena
stacks intersection collection.csv wishlist.csv available.csv
```

**`difference`** — cards in the first stack but not the second

```bash
stacks difference deck1.arena deck2.arena result.arena
stacks difference collection.csv deck.arena missing.csv
```

### Enrichment & Filtering

**`enrich`** — add Scryfall metadata (prices, mana cost, rarity, etc.) to a stack

```bash
stacks enrich deck.arena enriched_deck.csv
stacks enrich collection.csv updated.csv --set m21
```

**`filter-stack`** — filter cards by property

```bash
stacks filter-stack collection.csv output.csv --rarity mythic
stacks filter-stack collection.csv output.csv --price-min 10 --colors R,G
stacks filter-stack collection.csv output.csv --filter 'price_usd:gte:5'
```

Filter options: `--filter` (raw `property:operator:value`), `--colors`, `--type-line`, `--mana-cost`, `--rarity`, `--set-code`, `--price-min`, `--price-max`

**`tag`** — add tags to all cards in a stack

```bash
stacks tag collection.csv tagged.csv commander
stacks tag deck.csv deck_tagged.csv budget staple
```

### Moxfield

**`pull`** — fetch a Moxfield deck and save locally

```bash
stacks pull https://moxfield.com/decks/AbCd1234 deck.mox
stacks pull AbCd1234 deck.csv --sideboard
stacks pull AbCd1234 deck.arena --maybeboard --token eyJ...
```

Options: `--token` (bearer token for private decks, or set `MOXFIELD_TOKEN`), `-s/--sideboard`, `-m/--maybeboard`

**`push`** — convert a local file to Moxfield-importable format

```bash
stacks push deck.csv deck.mox
stacks push deck.arena deck.txt
```

**`sync`** — pull all tracked Moxfield decks from a config file

```bash
stacks sync
stacks sync --sideboard --maybeboard
stacks sync --config path/to/tracked_decks.json
```

Options: `--config` (default: `data/tracked_decks.json`, or set `STACKS_TRACKED_DECKS`), `--token`, `-s/--sideboard`, `-m/--maybeboard`

Config format:

```json
{
  "decks": [
    {
      "url": "https://moxfield.com/decks/AbCd1234",
      "output": "data/decks/my_deck.moxfield",
      "sideboard": false,
      "maybeboard": false
    }
  ]
}
```

## Supported Formats

| Extension | Format | Card Type |
|-----------|--------|-----------|
| `.arena` | MTG Arena export | Card (name only) |
| `.csv` | CSV (auto-detected) | Card, Print, ScryfallCard, or Moxfield |
| `.moxfield` / `.mox` | Moxfield | Print |
