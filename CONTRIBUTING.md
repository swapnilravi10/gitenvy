# Contributing to gitenvy

First off, thank you for considering contributing! 🙌  
We appreciate all kinds of contributions: bug fixes, improvements, documentation, and new features.

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button on the top-right of the repository page to create your own copy.

### 2. Clone Your Fork
If you prefer SSH:
```bash
git clone git@github.com:swapnilravi10/gitenvy.git
cd gitenvy
```
Or if you prefer HTTPS:
```bash
git clone https://github.com/swapnilravi10/gitenvy.git
cd gitenvy
```

### 3. Install Dependencies

We recommend using Poetry to manage dependencies:
```bash
poetry install
poetry shell
```
### 4. Create a Branch
```bash
git checkout -b feature/your-feature-name
```
### 5. Make Changes

- Keep your code clean and well-documented.
- Follow existing coding style and conventions.
- Update tests if you add or change functionality.

### 6. Run Tests

We use pytest for testing. Make sure all tests pass:
```bash
pytest
```
### 7. Commit Changes
```bash
git add .
git commit -m "Describe your changes"
```

### 8. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub, describing your changes.

## Reporting Issues

If you find a bug or have a feature request:

1. Check the [issues](https://github.com/swapnilravi10/gitenvy/issues) page to see if it already exists.
2. Open a new issue with a clear description and steps to reproduce (if applicable).

## Code of Conduct

Please be respectful and follow the [Code of Conduct](CODE_OF_CONDUCT.md) when contributing.

---

Thank you for helping improve **gitenvy**! 💜
