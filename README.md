# gitenvy

🔐 **Manage encrypted `.env` files with Git as the single source of truth.**

`gitenvy` helps teams and individuals securely version-control their environment files.  
It encrypts `.env` files before committing them, so sensitive secrets never appear in plaintext inside Git.  

---

## ✨ Features

- 🔒 **Secure by default** — uses [Fernet encryption](https://cryptography.io/en/latest/fernet/)  
- 📂 **Git-backed storage** — treat your Git repo as the source of truth for `.env` versions  
- 📈 **Versioned environments** — each push creates a new version for rollback and audit  
- 👥 **Team-ready** — share encrypted `.env` files with teammates  
- 💻 **Simple CLI** — intuitive commands for `init`, `push`, `pull`, and `list`  

---

## 📦 Installation

Install via pip directly from GitHub:

```bash
pip install git+https://github.com/swapnilravi10/gitenvy.git
```
(Coming soon to PyPI: pip install gitenvy)

## 🚀 Quick Start
1. Initialize gitenvy with your storage repo
```bash
gitenvy init --repo git@github.com:your-org/your-storage-repo.git
```
2. Push a .env file securely
```bash
gitenvy push --project sales --env prod
```
3. Pull and decrypt a version
```bash
gitenvy pull --project sales --env prod --version latest --out .env
```
4. List available versions
```bash
gitenvy list --project sales --env prod
```
## 🔑 Encryption Key Management

- On first use, gitenvy generates a Fernet key and stores it locally (~/.gitenvy/key).

- To collaborate, share the key with your team securely (1Password, Vault, etc).

- Everyone using the same key can encrypt/decrypt .env files.

## 🛠 Development

Clone the repo:
```bash
git clone https://github.com/swapnilravi10/gitenvy.git
cd gitenvy
poetry install
```
Run the CLI locally:
```bash
poetry run gitenvy --help
```
## 📜 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🙌 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check out the [issues page](https://github.com/swapnilravi10/gitenvy/issues) to get started.
Before contributing, please read our [Code of Conduct](CODE_OF_CONDUCT.md).  

Thank you for helping improve Gitenvy! 💜