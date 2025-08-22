# AI Opportunity Explorator - Claude Instructions

## Python Environment
- **Always use `uv` instead of `python3` or `pip`** for Python commands
- This project uses uv for dependency management
- Commands should be: `uv run python` instead of `python3`
- For package installation: `uv add <package>` instead of `pip install`

## Development Commands
- Run the application: `uv run python src/main.py`
- Install dependencies: `uv sync`
- Add new dependencies: `uv add <package-name>`

## Testing
- Run tests with: `uv run pytest` (if tests exist)
- For quick Python scripts: `uv run python -c "..."`

## Project Structure
- Main application: `src/main.py`
- Frontend: `public/` directory
- Data: `src/data/catalog.json`
- Key modules: catalog_manager.py, roi_calculator.py, ai_client.py

## Important Notes
- Always use uv commands for consistency with the project setup
- The project has a pyproject.toml and uv.lock file indicating uv is the preferred tool
- When running Python code for testing, use `uv run python` prefix