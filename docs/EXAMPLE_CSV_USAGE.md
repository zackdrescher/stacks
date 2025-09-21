# CSV Collection Parser Usage

This document shows how to use the CSV collection parser to import card collections into the stacks library. The parser supports multiple CSV formats including standard collection exports and Moxfield collection files.

## Basic Usage

```python
from stacks.parsing.csv import parse_csv_collection_file
from pathlib import Path

# Parse a CSV collection file (automatically detects format)
csv_file = Path('data/export_simple_1751163593.csv')
stack = parse_csv_collection_file(csv_file)

print(f'Total cards in collection: {len(list(stack))}')
print(f'Unique cards: {len(stack.unique_cards())}')

# Show some cards with their details
for card, count in list(stack.items())[:5]:
    print(f'{count}x {card.name} ({card.set}) - Foil: {card.foil}, Price: ${card.price}')
```

## Supported CSV Formats

The parser automatically detects and supports multiple CSV formats:

### 1. Standard Collection Format

Basic collection export format with standard column names.

**Required columns:**
- `Count`: Number of copies of the card (positive integer)
- `Card Name`: Name of the card (cannot be empty)
- `Set Name`: Name of the set the card is from

**Optional columns:**
- `Foil`: Whether the card is foil (true/false, 1/0, yes/no)
- `Price`: Price of the card (decimal number, can be empty)
- `Collector Number`: Card's collector number within the set
- `Tags`: Comma-separated list of tags

Example:
```csv
Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
1,Black Lotus,Alpha,3,false,5000.00
```

### 2. Moxfield Collection Format

Support for Moxfield collection CSV exports with their specific column names and format.

**Required columns:**
- `Count`: Number of copies
- `Name`: Card name (maps to Card Name)
- `Edition`: Set code (maps to Set Name)

**Optional columns:**
- `Condition`: Card condition (Mint, Near Mint, Lightly Played, etc.)
- `Language`: Language (English, French, Japanese, etc.) - defaults to English
- `Foil`: Foil type (blank, "foil", "etched") - blank = non-foil
- `Collector Number`: Card's collector number
- `Purchase Price`: Purchase price (maps to Price)
- `Alter`: Whether card is altered (True/False)
- `Playtest Card`: Whether it's a playtest card (True/False)
- `Tags`: Comma-separated tags

**Language support:** Moxfield language codes are automatically mapped to standard codes:
- English/en → en
- French/fr → fr  
- German/de → de
- Japanese/jp/ja → ja
- Korean/kr/ko → ko
- Spanish/sp/es → es
- And many more...

**Foil support:** Moxfield foil values are handled:
- Empty/blank → non-foil (False)
- "foil" → foil (True)
- "etched" → foil (True)

Example Moxfield CSV:
```csv
Count,Name,Edition,Condition,Language,Foil,Collector Number,Purchase Price
1,Lightning Bolt,lea,Near Mint,English,,1,
2,Counterspell,leb,Lightly Played,English,foil,5,25.50
1,Black Lotus,lea,Mint,English,etched,10,5000.00
```

## Error Handling

The parser will raise `ValueError` in the following cases:

- Missing required columns
- Invalid count (non-numeric or zero/negative)
- Empty card name
- Invalid price (non-numeric when not empty)

## Working with Print Objects

The CSV parser creates `Print` objects which are specialized `Card` objects that include additional metadata:

```python
# Access print-specific properties
for card in stack.unique_cards():
    print(f"Card: {card.name}")
    print(f"Set: {card.set}")
    print(f"Foil: {card.foil}")
    print(f"Price: ${card.price}" if card.price else "Price: N/A")
    print("---")
```

## Integration with Existing Stack Operations

Since `Print` extends `Card`, all existing stack operations work:

```python
# Find specific cards
lightning_bolt = Print(name="Lightning Bolt", set="Beta", foil=False, price=100.00)
count = stack.count(lightning_bolt)

# Combine with other stacks
arena_deck = parse_arena_deck_file('deck.arena')
combined = stack.union(arena_deck)

# Find cards in common
shared = stack.intersect(arena_deck)
```
