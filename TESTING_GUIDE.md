# Guidelines for Adding Tests to Visdom

This document provides guidance on adding new tests to the Visdom test suite, following best practices for comprehensive coverage and edge case evaluation.

## Test Directory Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── test_app.py                      # Application class tests
├── test_base_handlers.py            # Base handler tests
├── test_web_handlers.py             # HTTP handler tests
├── test_socket_handlers.py          # WebSocket handler tests
├── test_build.py                    # Build/asset tests
├── test_extended_server_utils.py    # Utility function tests
├── test_integration.py              # Multi-component tests
└── test_defaults.py                 # Configuration tests
```

## Testing Each Component

### 1. HTTP Request Handlers (test_web_handlers.py pattern)

When testing a new HTTP handler:

```python
def test_handler_basic_operation(self):
    """Test handler performs its core function."""
    mock_app = Mock()
    mock_request = Mock()
    mock_request.arguments = {}
    
    with patch('tornado.web.RequestHandler.__init__', return_value=None):
        handler = YourHandler(mock_app, mock_request)
        # Test core functionality
        assert handler is not None

def test_handler_with_invalid_arguments(self):
    """Test handler gracefully handles invalid input."""
    mock_request = Mock()
    mock_request.arguments = {'invalid_param': [b'value']}
    # Should handle gracefully without crashing

def test_handler_with_unicode_data(self):
    """Test handler with unicode characters."""
    mock_request = Mock()
    mock_request.arguments = {'data': [b'\xf0\x9f\x98\x80']}  # emoji
    # Should process unicode correctly

def test_handler_with_large_payload(self):
    """Test handler with large data."""
    large_data = b'x' * (10 * 1024 * 1024)  # 10MB
    mock_request.arguments = {'data': [large_data]}
    # Should handle without memory issues
```

### 2. WebSocket Handlers (test_socket_handlers.py pattern)

When testing WebSocket functionality:

```python
def test_message_processing(self):
    """Test processing incoming WebSocket message."""
    message = {
        'cmd': 'close',
        'win': 'window_id'
    }
    # Verify message route and handling

def test_unknown_command(self):
    """Test handling of unknown commands."""
    message = {'cmd': 'unknown', 'data': {}}
    # Should either reject or log gracefully

def test_missing_required_fields(self):
    """Test message with incomplete data."""
    message = {'cmd': 'close'}  # Missing 'win'
    # Should handle missing fields gracefully

def test_broadcast_message(self):
    """Test broadcasting to multiple clients."""
    # Verify message sent to all connected clients

def test_selective_broadcast(self):
    """Test broadcasting to specific sources."""
    # Verify message sent to selected clients only
```

### 3. Utilities (test_extended_server_utils.py pattern)

When testing utility functions:

```python
def test_function_with_simple_input(self):
    """Test function with standard input."""
    result = your_function(simple_data)
    assert result is not None

def test_function_with_empty_input(self):
    """Test function with empty/null input."""
    result = your_function({})
    # Should handle gracefully

def test_function_with_large_input(self):
    """Test function with very large data."""
    large_data = {'items': [{'data': 'x' * 1000} for _ in range(1000)]}
    result = your_function(large_data)
    # Should not timeout or crash

def test_function_with_special_characters(self):
    """Test function with unicode and special chars."""
    special_data = 'Data with émojis 🚀 and symbols !@#$%'
    result = your_function(special_data)
    # Should handle special chars correctly

def test_function_serialization(self):
    """Test function output is JSON serializable."""
    result = your_function(data)
    json_str = json.dumps(result)  # Should not raise

def test_function_roundtrip(self):
    """Test serialization and deserialization."""
    original = your_function(data1)
    serialized = json.dumps(original)
    deserialized = json.loads(serialized)
    assert deserialized == original
```

### 4. Integration Tests (test_integration.py pattern)

When testing multiple components together:

```python
def test_full_workflow(self):
    """Test complete workflow from start to finish."""
    # 1. Initialize component A
    # 2. Perform operation
    # 3. Verify state in component B
    # 4. Confirm final result

def test_error_recovery(self):
    """Test system recovers from errors."""
    # 1. Create normal state
    # 2. Introduce error
    # 3. Verify graceful handling
    # 4. Confirm system is still functional

def test_data_consistency(self):
    """Test data remains consistent across operations."""
    initial_state = {'windows': {}}
    # Perform operations
    # Verify no data loss or corruption
    assert verify_consistency(final_state)

def test_concurrent_operations(self):
    """Test multiple operations happening together."""
    for i in range(10):
        # Perform operations in parallel concept
        pass
    # Verify no race conditions
```

## Edge Cases to Always Test

### Input Validation
- ✓ None/null values
- ✓ Empty strings, lists, dicts
- ✓ Very large inputs (10MB+ for data)
- ✓ Negative numbers (for numeric inputs)
- ✓ Zero values (for division/counts)

### Unicode & Special Characters
- ✓ Emoji: 🚀 👍 😊
- ✓ Non-Latin: 中文, 日本語, العربية
- ✓ Special symbols: !@#$%^&*()
- ✓ Control characters
- ✓ Unicode normalization issues

### Data Types
- ✓ Strings vs bytes
- ✓ Integers vs floats
- ✓ Lists vs tuples
- ✓ Dicts with various key types
- ✓ Nested structures

### Error Conditions
- ✓ Network failures
- ✓ File not found
- ✓ Corrupted data
- ✓ Permission denied
- ✓ Timeout/slow responses

### Performance
- ✓ Very large datasets
- ✓ Deep nesting (1000+ levels)
- ✓ Many concurrent requests
- ✓ Memory-intensive operations

### Boundary Conditions
- ✓ Min/max values
- ✓ Off-by-one errors
- ✓ Empty collections
- ✓ Single item vs multiple

## Test Structure Template

```python
"""Unit tests for [module name]."""

import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.module_name import ComponentToTest


class TestComponentBasics:
    """Test basic functionality."""

    def test_component_initialization(self):
        """Test component creates without error."""
        component = ComponentToTest()
        assert component is not None

    def test_component_default_values(self):
        """Test component has sensible defaults."""
        component = ComponentToTest()
        assert component.property == expected_default


class TestComponentFunctionality:
    """Test core operations."""

    def test_operation_succeeds(self):
        """Test main operation works correctly."""
        # Setup
        component = ComponentToTest()
        
        # Execute
        result = component.method(data)
        
        # Verify
        assert result == expected_output

    def test_operation_with_edge_case(self):
        """Test operation with edge case input."""
        # Test boundary condition
        pass


class TestComponentErrors:
    """Test error handling."""

    def test_handles_invalid_input(self):
        """Test graceful error handling."""
        component = ComponentToTest()
        
        with pytest.raises(ExpectedException):
            component.method(invalid_data)

    def test_handles_missing_data(self):
        """Test behavior with missing data."""
        component = ComponentToTest()
        result = component.method({})  # Empty input
        assert result is not None or result == sentinel_value


class TestComponentConcurrency:
    """Test concurrent access."""

    def test_multiple_operations(self):
        """Test multiple operations don't interfere."""
        components = [ComponentToTest() for _ in range(5)]
        results = [c.method(data) for c in components]
        # Each should be independent
        assert len(set(results)) == 5

    def test_state_consistency(self):
        """Test state remains consistent."""
        component = ComponentToTest()
        initial_state = component.state.copy()
        
        # Perform operations
        component.method(data)
        
        # Verify only expected changes
        assert component.state != initial_state
```

## Running Tests During Development

### Watch mode (re-run on file change):
```bash
pytest-watch tests/test_your_file.py
```

### Run specific test class:
```bash
pytest tests/test_your_file.py::TestYourClass -v
```

### Run specific test method:
```bash
pytest tests/test_your_file.py::TestYourClass::test_specific_method -v
```

### Run with coverage:
```bash
pytest tests/ --cov=visdom.module --cov-report=html
```

### Run with verbose output:
```bash
pytest tests/ -vv -s  # extra verbose, print statements
```

## Best Practices Checklist

When writing tests, ensure:

- ✓ Test name clearly describes what is being tested
- ✓ Use docstrings to explain the test's purpose
- ✓ Each test covers ONE concept
- ✓ Test should pass/fail for clear reasons
- ✓ Use appropriate assertions (assert, assert_not, assert_in, etc.)
- ✓ Clean up resources (temp files, mocks)
- ✓ Avoid hardcoded paths - use tempfile
- ✓ Mock external dependencies
- ✓ Test both success and failure paths
- ✓ Include edge cases (empty, null, large, unicode, etc.)
- ✓ Use fixtures for shared setup
- ✓ Don't depend on test execution order
- ✓ Keep tests fast (< 1 second each)
- ✓ Avoid flaky tests (random failures)

## Common Testing Patterns

### Mocking External Services
```python
@patch('visdom.module.external_function')
def test_with_mocked_service(self, mock_func):
    mock_func.return_value = expected_value
    result = your_function()
    assert result == expected_value
    mock_func.assert_called_once()
```

### Testing with Temporary Files
```python
def test_file_operations(self):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test data')
        filepath = f.name
    
    try:
        result = your_function(filepath)
        assert result is not None
    finally:
        os.unlink(filepath)
```

### Testing Context Managers
```python
def test_context_manager(self):
    with YourContextManager() as resource:
        assert resource is properly_initialized
        # Use resource
    # Resource is properly cleaned up
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Tornado testing guide](https://www.tornadoweb.org/en/stable/testing.html)
- Visdom test examples in this directory

