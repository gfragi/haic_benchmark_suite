#!/bin/bash

# HAIC Backend Testing Script
# This script runs basic backend tests to verify the system is working

set -e

echo "🧪 HAIC Backend Testing Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "bench-env" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "📁 Checking project structure..."
if [ -d "backend" ] && [ -d "bench-env" ] && [ -d "haic_env_builder" ]; then
    print_status "Project structure looks good"
else
    print_error "Missing required directories"
    exit 1
fi

echo ""
echo "🐍 Checking Python environment..."

# Check if bench-env exists and is activated
if [ -z "$VIRTUAL_ENV" ] || [[ "$VIRTUAL_ENV" != *"bench-env" ]]; then
    echo "🔧 Activating virtual environment..."
    source bench-env/bin/activate
    if [ $? -ne 0 ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    print_status "Virtual environment activated"
else
    print_status "Virtual environment already active"
fi

# Check if haic_env_builder is installed
echo ""
echo "📦 Checking dependencies..."
python -c "import haic_env_builder" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "haic_env_builder package available"
else
    print_warning "haic_env_builder not found, installing..."
    cd haic_env_builder && pip install -e . > /dev/null 2>&1 && cd ..
    if [ $? -eq 0 ]; then
        print_status "haic_env_builder installed"
    else
        print_error "Failed to install haic_env_builder"
        exit 1
    fi
fi

# Run unit tests
echo ""
echo "🧪 Running unit tests..."
cd backend

# Test 1: Import test
echo "   Testing imports..."
python -c "
try:
    from app.services.evaluate import calculate_prediction_accuracy, calculate_response_time
    print('✅ Imports successful')
except ImportError as e:
    print('❌ Import failed:', str(e))
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    print_error "Import test failed"
    exit 1
fi

# Test 2: Function test
echo "   Testing functions..."
python -c "
from app.services.evaluate import calculate_prediction_accuracy, calculate_response_time

# Test accuracy
data = [{'result': 'true_positive'}, {'result': 'true_negative'}, {'result': 'false_positive'}]
acc = calculate_prediction_accuracy(data)
assert abs(acc - (2/3)) < 0.001, f'Accuracy test failed: {acc}'

# Test response time
data = [{'response_time': 1.0}, {'response_time': 1.5}, {'response_time': 0.5}]
rt = calculate_response_time(data)
assert abs(rt - 1.0) < 0.001, f'Response time test failed: {rt}'

print('✅ Function tests passed')
" 2>/dev/null

if [ $? -ne 0 ]; then
    print_error "Function test failed"
    exit 1
fi

# Test 3: Pytest
echo "   Running pytest..."
PYTHONPATH=. pytest tests/test_data_evaluation.py -q >/dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

cd ..

echo ""
print_status "All basic unit tests passed!"
echo ""
echo "📊 Test Coverage Summary:"
echo "   ✅ Unit Tests (No Dependencies): test_data_evaluation.py"
echo "   ⚠️  Integration Tests (Require Docker): All API tests"
echo ""
echo "🚀 Next Steps:"
echo "   • For unit testing only: cd backend && PYTHONPATH=. pytest tests/test_data_evaluation.py -v"
echo "   • For full integration testing: make dev && make test"
echo "   • For manual integration tests: make test-backend"
echo "   • See backend/TESTING_README.md for comprehensive testing guide"
echo ""
echo "🎉 Backend core functionality verified and ready for development!"
