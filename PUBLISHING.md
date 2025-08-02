# PyPI Publishing Guide

This guide covers how to publish `macos-ui-automation-mcp` to PyPI.

## 🔧 Setup (One-time)

### 1. Configure PyPI Trusted Publishing

**For PyPI (production):**
1. Go to https://pypi.org/manage/account/publishing/
2. Add trusted publisher with these settings:
   - **PyPI Project Name**: `macos-ui-automation-mcp`
   - **Owner**: `mb-dev`
   - **Repository name**: `macos-ui-automation-mcp`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

**For TestPyPI (testing):**
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add trusted publisher with same settings but environment name: `testpypi`

### 2. Create GitHub Environments

1. Go to your repository **Settings** → **Environments**
2. Create environment `pypi` for production releases
3. Create environment `testpypi` for test releases
4. Optionally add environment protection rules (require reviewers, etc.)

## 🚀 Publishing Workflow

### Method 1: Automatic Release (Recommended)

Use the included release script for version management:

```bash
# Show current version
python scripts/release.py version

# Bump patch version (e.g., 0.1.0 → 0.1.1)
python scripts/release.py bump patch

# Bump minor version (e.g., 0.1.0 → 0.2.0)  
python scripts/release.py bump minor

# Bump major version (e.g., 0.1.0 → 1.0.0)
python scripts/release.py bump major

# Create specific version
python scripts/release.py release 1.0.0

# Dry run to see what would happen
python scripts/release.py bump patch --dry-run
```

**What the script does:**
1. Updates version in `pyproject.toml`
2. Builds and tests the package
3. Commits version change
4. Creates and pushes git tag
5. Creates GitHub release
6. 🚀 **GitHub Actions automatically publishes to PyPI**

### Method 2: Manual Release

```bash
# 1. Update version in pyproject.toml
vim pyproject.toml

# 2. Commit and tag
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin main
git push origin vX.Y.Z

# 3. Create GitHub release
gh release create vX.Y.Z --title "Release X.Y.Z" --notes "Release version X.Y.Z"
```

### Method 3: Test Publishing

To test on TestPyPI before real release:

1. Go to **Actions** tab in GitHub
2. Click **Publish to PyPI** workflow
3. Click **Run workflow**
4. Select `testpypi` environment
5. Click **Run workflow**

## 📦 Package Structure

The package includes:
- **MCP Server**: `macos-ui-automation-mcp` command
- **CLI Tool**: `macos-ui-automation` command  
- **Python Library**: `from macos_ui_automation import ...`

### Installation After Publishing

```bash
# Install from PyPI
pip install macos-ui-automation-mcp

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ macos-ui-automation-mcp

# Verify installation
macos-ui-automation-mcp --help
macos-ui-automation --help
```

## 🔍 Verification

After publishing, verify the package:

```bash
# Create clean environment
python -m venv test-env
source test-env/bin/activate

# Install from PyPI
pip install macos-ui-automation-mcp

# Test MCP server
macos-ui-automation-mcp --help

# Test CLI
macos-ui-automation test

# Test Python import
python -c "from macos_ui_automation import SystemStateDumper; print('Import successful')"
```

## 🛡️ Security Features

- **Trusted Publishing**: No API keys needed, uses GitHub OIDC
- **Signed Releases**: Packages signed with Sigstore
- **Environment Protection**: Optional manual approval for production
- **Artifact Verification**: All build artifacts uploaded to GitHub releases

## 📊 Package Metadata

Key package information:
- **Name**: `macos-ui-automation-mcp`
- **Platform**: macOS only (`Operating System :: MacOS`)
- **Python**: 3.10+ (`requires-python = ">=3.10"`)
- **License**: MIT
- **Keywords**: mcp, macos, automation, ui, accessibility, claude

## 🔗 Useful Links

- **PyPI Page**: https://pypi.org/project/macos-ui-automation-mcp/
- **TestPyPI Page**: https://test.pypi.org/project/macos-ui-automation-mcp/
- **GitHub Releases**: https://github.com/mb-dev/macos-ui-automation-mcp/releases
- **Documentation**: https://github.com/mb-dev/macos-ui-automation-mcp#readme

## 🐛 Troubleshooting

### Publishing Fails
1. Check GitHub Actions logs in **Actions** tab
2. Verify PyPI trusted publishing configuration
3. Ensure version isn't already published
4. Check if package name conflicts exist

### Import Errors After Install
1. Verify PyObjC dependencies install correctly on macOS
2. Check Python version compatibility (3.10+)
3. Test in clean virtual environment

### Permission Errors
1. Verify GitHub repository settings allow workflow runs
2. Check environment protection rules aren't blocking
3. Ensure trusted publishing is configured correctly