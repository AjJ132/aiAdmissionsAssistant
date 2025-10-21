# Git Hooks

This directory contains Git hooks that are tracked in version control.

## Available Hooks

### pre-push
Runs Server tests before allowing a push to remote. This ensures that only code with passing tests gets pushed to the repository.

## Installation

**Important:** After cloning the repository or when the `.git` directory is reinitialized, you must install the hooks by running:

```bash
./.githooks/install-hooks.sh
```

This needs to be run once after cloning the repository or when hooks are updated.

## Manual Installation

You can also manually copy hooks:

```bash
cp .githooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## How It Works

- **Commit**: Hooks do NOT run on commit
- **Push**: The pre-push hook automatically runs your Server tests before allowing the push
  - ✅ **Tests Pass**: Push proceeds normally
  - ❌ **Tests Fail**: Push is blocked until tests pass

## Bypassing Hooks (Not Recommended)

In rare cases where you need to bypass the hooks, you can use:

```bash
git push --no-verify
```

**Warning:** Only bypass hooks if you know what you're doing!
