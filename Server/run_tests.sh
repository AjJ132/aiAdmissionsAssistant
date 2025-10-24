#!/bin/bash
# Test runner script for AI Admissions Assistant Server
# Usage: ./run_tests.sh [options]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Admissions Assistant Test Runner ===${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Parse command line arguments
case "${1:-all}" in
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest -v
        ;;
    "unit")
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest -v -m unit
        ;;
    "async")
        echo -e "${GREEN}Running async tests only...${NC}"
        pytest -v -m asyncio
        ;;
    "coverage")
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov --cov-report=term-missing --cov-report=html
        echo -e "\n${GREEN}Coverage report generated in coverage_html/index.html${NC}"
        ;;
    "handler")
        echo -e "${GREEN}Running handler tests...${NC}"
        pytest -v tests/test_handler.py
        ;;
    "controller")
        echo -e "${GREEN}Running controller tests...${NC}"
        pytest -v tests/test_scraping_controller.py
        ;;
    "service")
        echo -e "${GREEN}Running service tests...${NC}"
        pytest -v tests/test_web_request_service.py
        ;;
    "utils")
        echo -e "${GREEN}Running utility tests...${NC}"
        pytest -v tests/test_scraping_utils.py
        ;;
    "scrape")
        echo -e "${GREEN}Running scrape.py tests...${NC}"
        pytest -v tests/test_scrape.py
        ;;
    "quick")
        echo -e "${GREEN}Running quick test suite (no coverage)...${NC}"
        pytest -v --tb=short
        ;;
    "watch")
        echo -e "${GREEN}Running tests in watch mode...${NC}"
        echo -e "${YELLOW}Install pytest-watch: pip install pytest-watch${NC}"
        ptw -- -v
        ;;
    "help"|"-h"|"--help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all        - Run all tests (default)"
        echo "  unit       - Run only unit tests"
        echo "  async      - Run only async tests"
        echo "  coverage   - Run tests with coverage report"
        echo "  handler    - Run handler tests only"
        echo "  controller - Run controller tests only"
        echo "  service    - Run service tests only"
        echo "  utils      - Run utility tests only"
        echo "  scrape     - Run scrape.py tests only"
        echo "  quick      - Run tests without coverage"
        echo "  watch      - Run tests in watch mode (requires pytest-watch)"
        echo "  help       - Show this help message"
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

echo -e "\n${GREEN}=== Test run complete ===${NC}"
