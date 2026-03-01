# calvincTools-CS

A Python package for calvincTools. This is the client-server version, not the standalone version.

## Installation

You can install the package using pip:

```bash
pip install calvincTools
```

Or install from source:

```bash
git clone https://github.com/yourusername/calvincTools.git
cd calvincTools
pip install -e .
```

## Usage

```python
import calvincTools

# Add usage examples here
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Legacy Database Overrides (init_cDatabase)

`calvincTools.models.init_cDatabase(...)` supports adapting to legacy schemas in two ways:

1. **Table name only differs**
   - Use `cTools_tablenames`.
   - Keys: `menuGroups`, `menuItems`, `cParameters`, `cGreetings`, `User`.

2. **Columns/types differ**
   - Use `cTools_models` with caller-provided SQLAlchemy models for one or more keys.

### Minimal pattern

```python
cTools_tablenames = {
	'menuGroups': 'cMenu_menugroups',
	'User': 'WICS4_users',
}

cTools_models = {
	'menuItems': WICS3_menuItems,
	'cParameters': WICS3_cParameters,
}

calvincTools_init(
	app,
	app_db,
	cTools_tablenames=cTools_tablenames,
	cTools_models=cTools_models,
)
```

### Important relationship rule

If a caller-provided model uses `relationship(...)`, ensure the target class resolves in the **same SQLAlchemy registry** as that model. String targets such as `'menuGroups'` can fail when the target class is dynamically created in a different registry.

Recommended options for caller-provided legacy models:
- Omit cross-registry relationships and let `init_cDatabase` attach compatible links.
- Or use class-object targets only when both models are guaranteed to be in the same registry.


## Development

To install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black .
```

Lint code:

```bash
flake8 calvincTools
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Calvin C - calvinc404@gmail.com

## Changelog

### 1.0.0 (2026-02-01)
- Initial release
