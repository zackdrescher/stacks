# stacks

CLI for managing Magic: The Gathering card collections. Perform set operations
(union, intersection, difference) across deck/collection files, pull decks
from Moxfield, enrich cards with Scryfall metadata, filter by card
properties, and tag cards.

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run stacks <command> [args]
```

### Commands

| Command | Description |
|---------|-------------|
| `union INPUT1 INPUT2 OUTPUT` | Combine all cards from both stacks |
| `intersection INPUT1 INPUT2 OUTPUT` | Cards present in both stacks |
| `difference INPUT1 INPUT2 OUTPUT` | Cards in INPUT1 not in INPUT2 |
| `enrich INPUT_FILE OUTPUT [--set CODE]` | Enrich cards with Scryfall data, write CSV |
| `filter-stack INPUT_FILE OUTPUT [--filter ...] [--colors] [--type-line] [--mana-cost] [--rarity] [--set-code] [--price-min] [--price-max]` | Filter cards by property |
| `tag INPUT_FILE OUTPUT TAGS...` | Add one or more tags to every card |
| `pull SOURCE OUTPUT [--token] [--sideboard] [--maybeboard]` | Fetch a deck from Moxfield |
| `pull-collection OUTPUT [--token]` | Fetch your Moxfield collection (requires a token) |
| `push INPUT_FILE OUTPUT [--collection]` | Convert a file to a Moxfield-importable format; `--collection` writes a collection-import CSV (set names mapped to codes via Scryfall) |
| `sync [--config] [--token] [--sideboard] [--maybeboard]` | Pull all decks tracked in `data/tracked_decks.json` |
| `list-operations` | List available stack operations |

Run `poetry run stacks <command> --help` for full option details and examples.

### Moxfield token

`pull-collection` needs a Moxfield Bearer token (`pull` only needs one for private decks). Moxfield has no public API or documented login flow, so copy the token from your browser: log in at moxfield.com, open DevTools → Network, click any request to `api2.moxfield.com`, and copy the value after `Bearer ` in the `Authorization` header. Pass it with `--token` or set `MOXFIELD_TOKEN` in the environment or a `.env` file. Tokens expire, so copy a fresh one if requests start failing with 401/403.

### Examples

```bash
# Set operations
poetry run stacks union deck1.arena deck2.arena combined.arena
poetry run stacks intersection collection.csv wishlist.csv available.csv
poetry run stacks difference collection.csv deck.arena missing.csv

# Pull a deck from Moxfield and convert formats
poetry run stacks pull https://moxfield.com/decks/AbCd1234 deck.csv --sideboard
poetry run stacks push deck.csv deck.mox

# Prepare a CSV from another site for Moxfield's collection import
poetry run stacks push --collection export.csv collection.csv

# Pull your own Moxfield collection (needs MOXFIELD_TOKEN, see below)
poetry run stacks pull-collection collection.csv

# Enrich with Scryfall data, then filter
poetry run stacks enrich deck.arena enriched.csv
poetry run stacks filter-stack enriched.csv mythics.csv --rarity mythic --price-min 5

# Tag cards
poetry run stacks tag collection.csv tagged.csv commander budget
```

## Supported File Formats

| Format | Extension | Card Type |
|--------|-----------|-----------|
| Arena | `.arena` | `Card` |
| CSV | `.csv` | `Card`, `Print`, or `ScryfallCard` (auto-detected) |
| Moxfield | `.mox` | `Print` |
| Moxfield import | `.txt` | `Print` (write-only) |

## Development

```bash
poetry run pytest          # run tests
poetry run ruff check       # lint
poetry run ruff format      # format
poetry run mypy stacks      # type check
```

See `CLAUDE.md` for architecture details.
