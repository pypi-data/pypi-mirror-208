# monday
A python client for the monday.com GraphQL API


For the Monday API docs, [click here](https://monday.com/developers/v2#introduction-section).


#### Requirements
- Python >= 3.6

#### Getting started
`pip install monday`

`monday` sample usage:
```python
from monday import MondayClient


monday = MondayClient('your token')

monday.items.create_item(board_id='12345678', group_id='today',  item_name='Do a thing')

```
