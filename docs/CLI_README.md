# Stack Operations CLI

A command-line interface for performing set operations on Magic: The Gathering card collections.

## Features

- **Three core operations**: difference, union, and intersection
- **Multiple file formats**: Supports both Arena deck files (`.arena`) and CSV collection files (`.csv`)
- **Mixed format operations**: Can combine different file formats in a single operation
- **Extensible design**: Easy to add new operations

## Installation

```bash
poetry install
```

## Usage

The CLI provides three main commands for performing set operations on card stacks:

### Basic Commands

```bash
# Union: Combine all cards from both files
stacks union deck1.arena deck2.arena combined.arena

# Intersection: Find cards that exist in both files  
stacks intersection collection.csv deck.arena shared.csv

# Difference: Find cards in first file but not in second
stacks difference collection.csv deck.arena missing.csv

# List available operations
stacks list-operations
```

### File Format Support

The CLI automatically detects file formats based on extension:

- **`.arena`**: Arena deck format (mainboard cards only)
- **`.csv`**: CSV collection format with metadata (set, foil, price, etc.)

#### Arena Format Example
```
Deck
4 Lightning Bolt
3 Counterspell
2 Island

Sideboard
```

#### CSV Format Example
```csv
Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
```

### Mixed Format Operations

You can mix file formats in operations. When outputting to CSV, Arena cards will be converted to Print objects with default values (empty set, non-foil, no price).

```bash
# Combine Arena deck with CSV collection, output as CSV
stacks union deck.arena collection.csv updated_collection.csv

# Find intersection, output as Arena deck  
stacks intersection collection.csv deck.arena available.arena
```

## Set Operations

### Union
Combines all cards from both inputs. If the same card appears in both files, all copies are included.

**Example:**
- File A: 4 Lightning Bolt, 2 Island
- File B: 2 Lightning Bolt, 3 Forest  
- Result: 6 Lightning Bolt, 2 Island, 3 Forest

### Intersection  
Returns cards that appear in both inputs. The result contains the minimum count of each shared card.

**Example:**
- File A: 4 Lightning Bolt, 2 Island
- File B: 2 Lightning Bolt, 3 Forest
- Result: 2 Lightning Bolt

### Difference
Returns cards from the first input that are not in the second input, or have higher counts.

**Example:**
- File A: 4 Lightning Bolt, 2 Island  
- File B: 2 Lightning Bolt, 3 Forest
- Result: 2 Lightning Bolt, 2 Island

## Extensibility

The CLI is designed to be easily extensible. New operations can be added by:

1. Creating a `StackOperation` object with your operation logic
2. Adding it to the `OPERATIONS` registry
3. Adding a corresponding Click command

Example of adding a new operation:

```python
from stacks.cli import OPERATIONS, StackOperation

def custom_operation(stack1, stack2):
    # Your operation logic here
    return result_stack

OPERATIONS["custom"] = StackOperation(
    name="custom",
    description="Description of your operation", 
    operation=custom_operation
)
```

## Examples

See `demo.sh` for a complete example showing all operations.

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run ruff format
```

Lint code:
```bash  
poetry run ruff check
```
