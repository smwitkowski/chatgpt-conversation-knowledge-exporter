# Review Addons

Directory for custom addons. Each addon should be a Python module that implements the `Addon` interface from `review_api.addons`.

## Creating an Addon

1. Create a new Python file in this directory
2. Import and implement `ExporterAddon` or `PanelAddon`
3. Register it in the addon registry (or use auto-discovery in the future)

Example:

```python
from review_api.addons import ExporterAddon
from review_api.store import KnowledgeStore

class MyExporter(ExporterAddon):
    @property
    def addon_id(self) -> str:
        return "my-exporter"
    
    # ... implement required methods
```
