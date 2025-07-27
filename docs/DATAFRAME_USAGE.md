# Converting a Stack to a pandas DataFrame

The `Stack.to_dataframe()` method allows you to convert any Stack of cards into a pandas DataFrame for data analysis and manipulation.

## Installation

First, make sure you have pandas installed:

```bash
pip install pandas
```

## Basic Usage

```python
from stacks.cards.card import Card
from stacks.stack import Stack

# Create some cards
lightning_bolt = Card(name="Lightning Bolt", tags={"red", "instant"})
counterspell = Card(name="Counterspell", tags={"blue", "instant"})

# Create a stack with multiple copies
stack = Stack([lightning_bolt, lightning_bolt, counterspell])

# Convert to DataFrame
df = stack.to_dataframe()
print(df)
```

Output:
```
             name             tags source            slug  count
0  Lightning Bolt   [instant, red]   None  lightning-bolt      2
1    Counterspell  [blue, instant]   None    counterspell      1
```

## Working with Different Card Types

### ScryfallCard Example

```python
from stacks.cards.scryfall_card import ScryfallCard
from stacks.cards.colors import Color

# Create enriched cards with Scryfall data
bolt = ScryfallCard(
    name="Lightning Bolt",
    oracle_id="abc123",
    set_code="M21",
    mana_cost="{R}",
    type_line="Instant",
    rarity="Common",
    colors=[Color.RED],
    price_usd=0.25
)

counter = ScryfallCard(
    name="Counterspell",
    oracle_id="def456",
    set_code="M21",
    mana_cost="{U}{U}",
    type_line="Instant",
    rarity="Common",
    colors=[Color.BLUE],
    price_usd=0.50
)

stack = Stack([bolt, bolt, bolt, counter])
df = stack.to_dataframe()

# Now you have a DataFrame with all Scryfall data
print(df.columns.tolist())
# ['name', 'tags', 'source', 'oracle_id', 'set_code', 'collector_number', 
#  'mana_cost', 'type_line', 'rarity', 'oracle_text', 'price_usd', 
#  'image_url', 'colors', 'slug', 'count']
```

### Print Card Example

```python
from stacks.cards.print import Print

# Create specific print versions
bolt_lea = Print(
    name="Lightning Bolt",
    set="LEA",
    foil=False,
    condition="NM",
    price=15.99
)

bolt_foil = Print(
    name="Lightning Bolt", 
    set="M21",
    foil=True,
    condition="NM",
    price=5.99
)

stack = Stack([bolt_lea, bolt_lea, bolt_foil])
df = stack.to_dataframe()

# Analyze by set, condition, foil status, etc.
print(df.groupby(['set', 'foil'])['count'].sum())
```

## Data Analysis Examples

Once you have a DataFrame, you can use all of pandas' powerful data analysis features:

```python
# Total value of the stack
total_value = (df['price_usd'] * df['count']).sum()

# Group by color
color_summary = df.groupby('colors')['count'].sum()

# Filter by rarity
mythic_cards = df[df['rarity'] == 'Mythic']

# Sort by price
expensive_cards = df.sort_values('price_usd', ascending=False)
```

## Error Handling

If pandas is not installed, the method will raise an `ImportError` with a helpful message:

```python
try:
    df = stack.to_dataframe()
except ImportError as e:
    print(f"Error: {e}")
    # Output: Error: pandas is required for this operation. Install with: pip install pandas
```

## Notes

- Set fields (like `tags` and `colors`) are automatically converted to lists for DataFrame compatibility
- Each row represents a unique card with its count
- All card attributes are preserved as columns
- Empty stacks return an empty DataFrame with expected column names
