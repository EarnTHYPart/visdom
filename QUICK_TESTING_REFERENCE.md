# Quick Reference Guide - Visdom Testing

## 🚀 Quick Start

### Import Testing Utilities
```python
import pytest
from tests.test_utils import (
    EnvironmentBuilder, 
    WebSocketMessageBuilder,
    create_mock_handler,
    EnvironmentValidator,
    temp_env_file,
)
from tests.conftest import mock_tornado_app, sample_environment
```

---

## 📋 Common Patterns

### 1. Test a Handler
```python
@pytest.mark.handler
def test_handler_basic_operation(mock_handler_context):
    handler = create_mock_handler(
        application=mock_handler_context['app']
    )
    assert handler is not None
```

### 2. Test with Sample Data
```python
def test_with_environment(sample_environment):
    assert 'win_1' in sample_environment['windows']
```

### 3. Create Complex Environment
```python
@pytest.mark.integration
def test_building_environment():
    env = (EnvironmentBuilder()
        .add_text_window('text_1', 'Hello')
        .add_plot_window('plot_1', {'x': [1,2], 'y': [1,4]})
        .add_layout('main')
        .build())
    
    assert EnvironmentValidator.window_count(env) == 2
```

### 4. WebSocket Messages
```python
def test_websocket_message():
    msg = WebSocketMessageBuilder.close_window('win_1')
    assert msg['cmd'] == 'close'
```

### 5. File Operations
```python
def test_file_handling():
    env_data = {'windows': {'w1': {}}}
    
    with temp_env_file(env_data) as filepath:
        process(filepath)
        # File auto-cleaned up
```

### 6. Large Data Testing
```python
def test_performance(large_environment):
    assert len(large_environment['windows']) == 100
```

### 7. Data Change Detection
```python
def test_data_changes():
    before = {'windows': {'w1': {'content': 'old'}}}
    after = {'windows': {'w1': {'content': 'new'}}}
    
    assert_data_changed(before, after, 'windows.w1.content')
```

---

## 🏗️ Builder Usage

### EnvironmentBuilder
```python
(EnvironmentBuilder()
    .add_text_window('id', 'content', title='Title')
    .add_plot_window('id', {'x': [], 'y': []}, title='')
    .add_image_window('id', 'src', title='')
    .add_layout('layout_id')
    .build())
```

### WebSocketMessageBuilder
```python
WebSocketMessageBuilder.close_window('win_id')
WebSocketMessageBuilder.save_environment('env_id')
WebSocketMessageBuilder.update_window('win_id', data)
WebSocketMessageBuilder.update_layout(layout)
```

---

## 🔍 Assertion Helpers

```python
# Environment validation
EnvironmentValidator.has_window(env, 'win_1')
EnvironmentValidator.window_has_property(env, 'win_1', 'type')
EnvironmentValidator.is_valid_structure(env)
EnvironmentValidator.window_count(env)
EnvironmentValidator.has_layout(env, 'main')

# Data change detection
assert_data_changed(before, after, 'path.to.value')
assert_data_unchanged(before, after, 'path.to.value')

# Serialization validation
assert_json_serializable(obj)

# Environment comparison
assert_environment_unchanged(before, after)
assert_window_exists(env, 'win_id')
```

---

## 🎯 Test Markers

Add to your test functions:

```python
@pytest.mark.slow           # Long-running tests
@pytest.mark.integration    # Multi-component tests
@pytest.mark.edge_case      # Edge case coverage
@pytest.mark.handler        # Handler tests
@pytest.mark.network        # Network-related tests
```

Usage in command line:
```bash
pytest -m integration       # Only integration tests
pytest -m "not slow"        # Skip slow tests
pytest -m "handler or integration"
```

---

## 🛠️ Factory Functions

```python
# Create mock handler
handler = create_mock_handler(
    write=MagicMock(),
    application=create_mock_app()
)

# Create mock request
request = create_mock_request(
    method='POST',
    arguments={'key': [b'value']},
    headers={'Content-Type': 'application/json'},
    body=b'test'
)

# Create mock app
app = create_mock_app(
    state={'windows': {}},
    layouts={'main': {}}
)
```

---

## 📊 Test Data Generation

```python
from tests.test_utils import TestDataGenerator

# Generate various test strings
TestDataGenerator.unicode_strings()        # 中文, العربية, etc.
TestDataGenerator.special_characters()     # !@#$%, \n, etc.
TestDataGenerator.large_strings(1024)      # 1KB string
TestDataGenerator.edge_case_numbers()      # 0, -1, inf, etc.

# Generate realistic data
plot_data = TestDataGenerator.sample_plot_data(points=100)
```

---

## 📝 Complete Test Template

```python
"""Tests for my_module.py"""

import pytest
from tests.test_utils import (
    EnvironmentBuilder,
    EnvironmentValidator,
    create_mock_handler,
)


@pytest.mark.handler
class TestMyHandler:
    """Test MyHandler class."""
    
    def test_basic_operation(self, mock_tornado_app):
        """Test handler performs basic operation."""
        handler = create_mock_handler(application=mock_tornado_app)
        assert handler is not None
    
    def test_with_sample_data(self, sample_environment):
        """Test handler with sample environment."""
        assert 'win_1' in sample_environment['windows']


@pytest.mark.integration
class TestMyWorkflow:
    """Test end-to-end workflows."""
    
    def test_complete_workflow(self):
        """Test complete workflow."""
        env = (EnvironmentBuilder()
            .add_text_window('w1', 'Hello')
            .build())
        
        assert EnvironmentValidator.has_window(env, 'w1')
```

---

## 🔧 Common Test Scenarios

### Testing Handler with Custom Request
```python
def test_handler_with_arguments(mock_handler_context):
    handler = create_mock_handler(
        application=mock_handler_context['app'],
        request=create_mock_request(
            arguments={'win': [b'win_1']}
        )
    )
    # Test logic
```

### Testing Large Dataset
```python
def test_large_environment_handling(large_environment):
    # large_environment has 100 windows
    assert EnvironmentValidator.window_count(large_environment) == 100
```

### Testing Unicode Support
```python
def test_unicode_handling():
    for text in TestDataGenerator.unicode_strings():
        result = process_text(text)
        assert result is not None
```

### Testing File I/O
```python
def test_environment_persistence():
    env = EnvironmentBuilder().add_text_window('w1', 'Hello').build()
    
    with temp_env_file(env) as filepath:
        loaded = load_env(filepath)
        assert EnvironmentValidator.has_window(loaded, 'w1')
```

### Testing Concurrent Operations
```python
@pytest.mark.slow
def test_concurrent_operations(large_environment):
    # Test with large environment (100 windows)
    for window_id in list(large_environment['windows'].keys()):
        process(window_id)
```

---

## 📊 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_web_handlers.py -v

# Run specific test class
pytest tests/test_handlers.py::TestMyClass -v

# Run specific test method
pytest tests/test_handlers.py::TestMyClass::test_method -v

# Run tests by marker
pytest tests/ -m integration -v
pytest tests/ -m "not slow" -v

# Run with coverage report
pytest tests/ --cov=visdom --cov-report=html

# Run in parallel
pytest tests/ -n auto

# Run with detailed output
pytest tests/ -vv -s

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l
```

---

## 🐛 Debugging Tips

```bash
# Print statements show up with -s flag
pytest tests/ -s

# Drop into debugger on failure
pytest tests/ --pdb

# Show full local variables on failure
pytest tests/ -l

# Verbose output with extra info
pytest tests/ -vv

# Show slowest tests
pytest tests/ --durations=10

# Quiet output
pytest tests/ -q
```

---

## 📚 Documentation

- **Full Guide:** `CODE_OPTIMIZATION_GUIDE.md`
- **Optimization Summary:** `OPTIMIZATION_SUMMARY.md`
- **Testing Guide:** `TESTING_GUIDE.md`
- **Test Summary:** `TEST_SUMMARY.md`

---

## ✅ Test Writing Checklist

When writing a test:

- ✅ Choose appropriate fixture (or create one)
- ✅ Use EnvironmentBuilder for data construction
- ✅ Use create_mock_* for mocks
- ✅ Use EnvironmentValidator for assertions
- ✅ Use context managers for resources
- ✅ Add appropriate marker (@pytest.mark)
- ✅ Clear test name describing what's tested
- ✅ One concept per test
- ✅ Add docstring explaining purpose

---

## 🚨 Common Issues & Solutions

### Issue: Mock handler doesn't have attribute
**Solution:** Use `create_mock_handler()` instead of manual mocking

### Issue: Temporary files not cleaned up
**Solution:** Use context managers: `with temp_env_file() as f:`

### Issue: Test is slow or hangs
**Solution:** Mark with `@pytest.mark.slow` and investigate timeout

### Issue: Unicode test failures
**Solution:** Use `TestDataGenerator.unicode_strings()` for proper coverage

### Issue: Tests depend on execution order
**Solution:** Each test should be independent, use fixtures for setup

---

## 📖 Examples by Component

### Handler Testing
See: `tests/test_web_handlers.py` (22 tests)

### WebSocket Testing
See: `tests/test_socket_handlers.py` (25 tests)

### Configuration Testing
See: `tests/test_defaults.py` (29 tests)

### Integration Testing
See: `tests/test_integration.py` (20 tests)

---

## 🎓 Learning Path

1. **Start:** Read this quick reference
2. **Practice:** Copy one test pattern and customize
3. **Explore:** Look at similar tests in the codebase
4. **Deep Dive:** Read `CODE_OPTIMIZATION_GUIDE.md`
5. **Master:** Review all test files and patterns

---

## 💡 Pro Tips

1. **Use builders for complex objects** - More readable than dicts
2. **Use factories for mocks** - Consistent configuration
3. **Use validators for assertions** - Self-documenting
4. **Use context managers** - Automatic cleanup
5. **Add markers early** - Easier to filter tests
6. **Group related tests** - Use test classes
7. **Name tests clearly** - `test_<what>_<when>_<expected>`
8. **Use fixtures** - Reduces boilerplate significantly

---

## 🔗 Related Files

```
tests/
├── conftest.py              # Fixtures and configuration
├── test_utils.py            # Builders, factories, validators
├── test_web_handlers.py     # HTTP handler tests
├── test_socket_handlers.py  # WebSocket tests
├── test_defaults.py         # Configuration tests
├── test_integration.py      # Workflow tests
└── test_app.py              # Application tests

docs/
├── CODE_OPTIMIZATION_GUIDE.md  # Detailed optimization guide
├── OPTIMIZATION_SUMMARY.md     # Summary of all changes
├── TESTING_GUIDE.md           # How to write tests
└── TEST_SUMMARY.md            # Test coverage overview
```

---

**Happy Testing! 🎉**
