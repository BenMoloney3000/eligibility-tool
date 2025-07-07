# Agent Guidelines

This project contains a Python backend and a small JavaScript front end.

## Testing and formatting
- Run `make test` before committing to ensure all Python tests and lint checks pass.
- Run `pre-commit run --files <changed files>` or `pre-commit run --all` if pre-commit hooks are installed.
- For front end changes you can run `npm test` to execute the JavaScript tests and `npm run build` to compile assets.

## Documentation
- Documentation lives in the `docs/` directory. Build docs with `make -C docs html`.

## Commits
- Make small, focused commits with descriptive messages.
- Ensure tests pass before pushing any changes.
