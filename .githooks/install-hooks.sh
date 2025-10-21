#!/bin/bash
# Install git hooks from .githooks directory
# Run this script to set up git hooks for this repository

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Installing Git Hooks ===${NC}\n"

# Get the root directory of the git repository
REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Check if .githooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${RED}Error: .githooks directory not found${NC}"
    exit 1
fi

# Copy hooks and make them executable
for hook in "$HOOKS_DIR"/*; do
    # Skip the install script itself
    if [[ "$(basename "$hook")" == "install-hooks.sh" ]]; then
        continue
    fi
    
    # Skip if not a file
    if [ ! -f "$hook" ]; then
        continue
    fi
    
    hook_name=$(basename "$hook")
    
    # Copy hook to .git/hooks
    cp "$hook" "$GIT_HOOKS_DIR/$hook_name"
    chmod +x "$GIT_HOOKS_DIR/$hook_name"
    
    echo -e "${GREEN}✓${NC} Installed $hook_name"
done

echo -e "\n${GREEN}Git hooks installed successfully!${NC}"
echo -e "${YELLOW}Note: Hooks will run automatically on git operations${NC}\n"
