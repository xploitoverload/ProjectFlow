# Quick Reference: Package vs Traditional Commands

## Installation

### Package Method (Recommended)
```bash
pip install -e .
```

### Traditional Method
```bash
pip install -r requirements.txt
```

## Running the Application

| Task | Package Command | Traditional Command |
|------|----------------|---------------------|
| Start server | `project-management` | `python run.py` |
| Initialize DB | `pm-init-db` | `python run.py init-db` |
| Migrate DB | `pm-migrate` | `python run.py migrate` |
| Show routes | `pm-routes` | `python run.py routes` |
| Interactive shell | N/A | `python run.py shell` |
| Help | `project-management --help` | `python run.py --help` |

## Key Differences

### Package Installation
- ✅ Global CLI commands
- ✅ Import from anywhere
- ✅ Cleaner syntax
- ✅ Better for development

### Traditional Installation
- ✅ Explicit dependencies
- ✅ Simpler for beginners
- ✅ More control
- ✅ Better for CI/CD pipelines

## Quick Start

### New Users (Package Method)
```bash
git clone <repo-url>
cd project-management
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
pm-init-db --with-sample-data
project-management
```

### Traditional Method
```bash
git clone <repo-url>
cd project-management
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py init-db --with-sample-data
python run.py
```

## Important Notes

1. Both methods are **fully supported**
2. You can use **both simultaneously**
3. No breaking changes to existing workflows
4. Choose what works best for you!
