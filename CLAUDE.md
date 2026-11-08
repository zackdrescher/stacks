# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_stack.py

# Run a single test by name
poetry run pytest tests/test_stack.py::test_function_name

# Run tests excluding slow/integration
poetry run pytest -m "not slow and not integration"

# Lint
poetry run ruff check

# Format
poetry run ruff format

# Type check
poetry run mypy stacks

# Run CLI
poetry run stacks <command>
```

## Architecture

**stacks** is a Python CLI for Magic: The Gathering card collection management. It performs set operations (union, intersection, difference) on card collections across multiple file formats, and can enrich cards with Scryfall API metadata.

### Card Type Hierarchy

Three Pydantic frozen (immutable) models form the data layer:

- **`Card`** (`stacks/cards/card.py`) — base model with `name`, `tags`, `source`. Equality based on slugified name.
- **`Print`** (`stacks/cards/print.py`) — extends Card with `set`, `foil`, `condition`, `language`, `collector_number`, `price`. Equality uses all fields.
- **`ScryfallCard`** (`stacks/cards/scryfall_card.py`) — extends Card with Scryfall API fields (`oracle_id`, `mana_cost`, `type_line`, `rarity`, etc.). Equality based on `oracle_id`.

### Stack[T]

`Stack[T]` (`stacks/stack.py`) is the core generic container. Internally a `dict[Card, list[Card]]` grouping copies. Key operations:
- Set ops: `union()`, `intersection()`, `difference()`, `split_on_overlap()`
- Mutation: `add()`, `add_tag()`
- Query: `unique_cards()`, `count()`, `match()`
- Export: `to_dataframe()` (returns pandas DataFrame)

All operations return new Stack instances (functional style).

### File I/O — Registry Pattern

`stacks/parsing/io_registry.py` maintains extension→reader/writer mappings via `@register_reader(ext)` and `@register_writer(ext)` decorators. Supported formats:

| Format | Extension | Card Type |
|--------|-----------|-----------|
| Arena | `.arena` | `Card` |
| CSV | `.csv` | `Card`, `Print`, `ScryfallCard`, or Moxfield |
| Moxfield | `.moxfield` | `Print` |

CSV reader auto-detects the card type from column headers. All parsers set `card.source` to the source file path.

### CLI

Entry point: `stacks.cli:cli` (Click group defined in `stacks/cli/__init__.py`).

Commands in `stacks/cli/commands.py`: `difference`, `union`, `intersection`, `enrich`, `filter-stack`, `tag`, `pull`, `pull-collection`, `push`, `list-operations`.

`stacks/cli/operations.py` — `StackOperation` registry handles loading inputs, running the operation, and writing output. `stacks/cli/converters.py` — `normalize_stack_for_output()` converts cards to the appropriate type for the output format (e.g. `Card` → `Print` when writing CSV).

### Moxfield Integration

- `stacks/moxfield/client.py` — `MoxfieldClient` (cloudscraper, optional Bearer token). `get_deck()` hits `api2.moxfield.com/v2/decks/all/{id}`; `get_collection_page()` / `iter_collection()` hit `GET /v1/collections` (paginated, returns the token owner's collection, no ID).
- `stacks/moxfield/puller.py` — `MoxfieldPuller.pull()` (deck) and `pull_collection()` (collection, tagged `mox_collection`) convert API JSON to `Stack[Print]`, expanding quantity into copies. In collection entries `language` is an object (`{"code": "en"}`), handled by `_language_code()`.
- The API is undocumented and has no username/password flow (login is behind Cloudflare/reCAPTCHA), so the token is copied from browser DevTools and supplied via `--token` or `MOXFIELD_TOKEN` (`.env` is loaded by `pull-collection`).

### Scryfall Integration

- `stacks/scryfall/client.py` — `ScryfallClient` makes HTTP requests to `api.scryfall.com`.
- `stacks/scryfall/scryer.py` — `Scryer` wraps the client; `enrich_stack()` batch-enriches a Stack with tqdm progress.

### Filtering

`stacks/filtering.py` — `FilterOperator` enum (EQUALS, CONTAINS, GREATER_THAN, etc.) drives `CardPropertyFilter` and `FilterableStack` for AND-logic multi-filter queries on card properties.

## Testing Conventions

- All Python changes must include corresponding tests.
- New functions and methods get unit tests in the relevant `tests/test_*.py` file.
- New CLI commands get tests in `tests/test_cli_commands.py` or `tests/test_cli_moxfield_commands.py`.
- Run `poetry run pytest` after every change to verify nothing is broken.

## Key Design Conventions

- Cards are immutable (frozen Pydantic models); operations always return new Stack instances.
- `Card.__eq__` uses slugified name; `Print.__eq__` uses all identity fields; `ScryfallCard.__eq__` uses `oracle_id`.
- New file formats: implement `StackReader`/`StackWriter` subclasses in `stacks/parsing/` and register with `@register_reader`/`@register_writer`.
- Tests use markers `slow` and `integration`; coverage must stay ≥ 80%.
