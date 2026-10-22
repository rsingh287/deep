# 🤝 Contributing to D.E.E.P

Thank you for your interest in contributing to **D.E.E.P (Dynamic Executive Edge Platform)**! We welcome contributions that adhere to our engineering rigor and zero-trust security standards.

---

## 🛠️ Getting Started

1. **Fork the Repository**:
   Click the **Fork** button at the top right of this repository.

2. **Clone your Fork**:
   ```bash
   git clone https://github.com/<your-username>/deep.git
   cd deep
   ```

3. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your local testing parameters
   ```

---

## 🔒 Crucial Security Rules Before Committing

Before creating any git commit or opening a Pull Request:

- **NEVER commit your `.env` file** or any file containing live tokens, passwords, or personal credentials.
- **NEVER commit local database files** (`*.db`, `*.sqlite`, `qdrant_db/`).
- **NEVER commit personal browser profiles** (`pc_app_profile/`).
- Run the code sanitization checks:
  ```bash
  python sanitize_secrets.py
  ```

---

## 🧪 Testing & Code Quality

We enforce strict formatting and linting:

1. **Format Code**:
   ```bash
   black .
   isort .
   ```

2. **Run Test Suites**:
   ```bash
   python -m pytest
   # or run the enhanced test suite:
   python test_enhanced_system_suite.py
   ```

---

## 🌿 Git & Pull Request Guidelines

1. **Branch Naming**:
   - `feat/feature-name` for new capabilities.
   - `fix/bug-fix-description` for bug fixes.
   - `refactor/subsystem-name` for code cleanup.
   - `docs/documentation-update` for documentation changes.

2. **Commit Messages**:
   Follow conventional commits:
   - `feat: implement autonomous intent routing for IoT appliances`
   - `fix: resolve PTY terminal websocket buffer overflow`
   - `docs: add PIC18F hardware pinout diagrams to README`

3. **Submitting a Pull Request**:
   - Push your branch to your fork.
   - Open a PR targeting the `master` or `main` branch.
   - Fill out the PR template detailing the change, verification steps, and hardware compatibility.
