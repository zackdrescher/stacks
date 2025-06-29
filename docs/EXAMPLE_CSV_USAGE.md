# CSV Collection Parser Usage

This document shows how to use the CSV collection parser to import card collections into the stacks library.

## Basic Usage

```python
from stacks.parsing.csv_reader import parse_csv_collection_file
from pathlib import Path

# Parse a CSV collection file
csv_file = Path('data/export_simple_1751163593.csv')
stack = parse_csv_collection_file(csv_file)

print(f'Total cards in collection: {len(list(stack))}')
print(f'Unique cards: {len(stack.unique_cards())}')

# Show some cards with their details
for card, count in list(stack.items())[:5]:
    print(f'{count}x {card.name} ({card.set}) - Foil: {card.foil}, Price: ${card.price}')
```

## CSV Format Requirements

The CSV file must contain the following columns:

- `Count`: Number of copies of the card (positive integer)
- `Card Name`: Name of the card (cannot be empty)
- `Set Name`: Name of the set the card is from
- `Foil`: Whether the card is foil (true/false, 1/0, yes/no)
- `Price`: Price of the card (decimal number, can be empty)

Example CSV format:

```csv
Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
1,Black Lotus,Alpha,3,false,5000.00
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
