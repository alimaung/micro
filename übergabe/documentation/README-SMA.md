# SMA Modular Architecture

This directory contains the refactored, modular version of the SMA automation system. The original monolithic `sma.py` file has been broken down into focused, maintainable modules.

## 📁 Module Structure

### Core Modules

#### `sma_controller.py` - Main Orchestrator
- **Purpose**: High-level workflow coordination and entry point
- **Key Classes**: `SMAController`
- **Responsibilities**: 
  - Command-line interface handling
  - Module coordination
  - Overall process flow management
  - Error handling and recovery

#### `sma_config.py` - Configuration Management
- **Purpose**: Configuration loading, file operations, and environment setup
- **Key Classes**: `SMAConfiguration`, `FileManager`, `DirectoryManager`
- **Responsibilities**:
  - Template and INI file management
  - Log directory creation
  - Path validation
  - Configuration parameter handling

#### `ui_automation.py` - UI Automation Core ⚠️ CRITICAL
- **Purpose**: All pywinauto operations for SMA application interaction
- **Key Classes**: `UIAutomationCore`, `WindowManager`, `ControlFinder`
- **Responsibilities**:
  - Window finding and management
  - Control detection and interaction
  - Button clicking and text input
  - Timing and retry logic

**⚠️ WARNING**: This module contains the most brittle and timing-sensitive code. Any modifications must be tested extensively in the actual SMA environment.

#### `sma_workflow.py` - SMA Application Workflow
- **Purpose**: Step-by-step SMA application interaction sequence
- **Key Classes**: `SMAWorkflowManager`, `SessionManager`, `DialogHandler`
- **Responsibilities**:
  - New session initialization
  - Session recovery logic
  - Dialog handling
  - Application lifecycle management

#### `progress_monitor.py` - Progress Tracking System
- **Purpose**: Progress monitoring, ETA calculation, and notifications
- **Key Classes**: `ProgressMonitor`, `ETACalculator`, `NotificationManager`
- **Responsibilities**:
  - Real-time progress tracking
  - ETA calculation and logging
  - Firebase notification management
  - Progress control detection

#### `advanced_finish.py` - Advanced Warning System
- **Purpose**: Red overlay, mouse control, and finish warnings
- **Key Classes**: `AdvancedFinishSystem`, `RedOverlay`, `MouseLocker`, `MonitorManager`
- **Responsibilities**:
  - Multi-monitor detection
  - Red warning overlay display
  - Mouse position control
  - Finish stage coordination

#### `post_processing.py` - End-of-Process Handling
- **Purpose**: End prompts, film transport, and cleanup operations
- **Key Classes**: `PostProcessor`, `PromptHandler`, `TransportManager`, `CleanupManager`
- **Responsibilities**:
  - Endsymbole/Nachspann prompt handling
  - Film transport monitoring
  - Application cleanup
  - Log file management

### Supporting Modules

#### `sma_exceptions.py` - Custom Exception Classes
- **Purpose**: Centralized error handling and custom exceptions
- **Key Classes**: `SMAException`, `UIAutomationError`, `ConfigurationError`, etc.
- **Responsibilities**:
  - Structured error reporting
  - Context-aware exception handling
  - Error categorization

#### `sma_utils.py` - Utility Functions and Helpers
- **Purpose**: Shared utilities, constants, and helper functions
- **Key Classes**: `SMAConstants`, `PerformanceTimer`, `StateTracker`
- **Responsibilities**:
  - Common utility functions
  - System constants
  - Performance monitoring
  - State tracking

## 🔄 Migration Status

### ✅ Completed
- [x] Module structure design
- [x] Empty module files with class skeletons
- [x] Documentation and planning
- [x] Exception hierarchy
- [x] Utility functions and constants

### 🚧 Pending (Critical Path)
- [ ] Extract utility functions from original `sma.py`
- [ ] Migrate configuration logic to `sma_config.py`
- [ ] **CAREFULLY** migrate UI automation functions to `ui_automation.py` ⚠️
- [ ] Extract workflow logic to `sma_workflow.py`
- [ ] Migrate progress monitoring to `progress_monitor.py`
- [ ] Extract post-processing logic to `post_processing.py`
- [ ] Wire modules together in `sma_controller.py`
- [ ] Comprehensive testing and validation

### ⚠️ Critical Preservation Areas

#### UI Automation Functions (HIGHEST PRIORITY)
Functions that must be migrated with **ZERO** changes to timing or logic:
- `find_window()`
- `find_control()`
- `wait_for_window()`
- `click_button()`
- `handle_main_screen()`
- `handle_data_source_selection()`
- `handle_film_start()`
- `handle_film_insert()`
- `handle_film_number_entry()`

#### Progress Monitoring (HIGH PRIORITY)
Functions requiring exact preservation:
- `monitor_progress()` - Core monitoring loop
- `find_progress_controls()` - Control detection
- All notification timing and triggers

#### Post-Processing (HIGH PRIORITY)
Functions requiring exact preservation:
- `handle_endsymbole_prompt()`
- `handle_nachspann_prompt()`
- `wait_for_transport_start()`
- `wait_for_transport_completion()`

## 🧪 Testing Strategy

### Phase 1: Module Integration Testing
1. Test each module independently
2. Validate configuration loading
3. Test utility functions
4. Verify exception handling

### Phase 2: UI Automation Testing ⚠️ CRITICAL
1. Test each UI automation function in isolation
2. Validate timing preservation
3. Test with actual SMA application
4. Verify error handling and recovery

### Phase 3: Full Integration Testing
1. Test complete workflow end-to-end
2. Test recovery scenarios
3. Test advanced finish system
4. Validate notification system

### Phase 4: Production Validation
1. Test with real SMA processes
2. Compare results with original system
3. Performance benchmarking
4. Stability testing

## 🚀 Quick Start Migration Guide

### Step 1: Backup Original
```bash
cp sma.py sma_original_backup.py
```

### Step 2: Start with Low-Risk Modules
1. Implement utility functions in `sma_utils.py`
2. Implement configuration logic in `sma_config.py`
3. Implement exception classes in `sma_exceptions.py`

### Step 3: UI Automation Migration ⚠️ HIGH RISK
1. **CAREFULLY** copy functions to `ui_automation.py`
2. Preserve exact function signatures
3. Maintain all timing and sleep calls
4. Test each function individually
5. **DO NOT** modify error handling patterns

### Step 4: Workflow and Monitoring
1. Migrate workflow functions to `sma_workflow.py`
2. Extract progress monitoring to `progress_monitor.py`
3. Migrate post-processing to `post_processing.py`

### Step 5: Controller Integration
1. Implement `SMAController` class
2. Wire all modules together
3. Test integration
4. Validate complete workflow

### Step 6: Validation and Cleanup
1. Compare with original system
2. Run full test suite
3. Document any changes
4. Remove original file after validation

## 🔧 Development Guidelines

### Code Style
- Follow existing Python conventions
- Maintain comprehensive docstrings
- Include type hints where possible
- Use descriptive variable names

### Error Handling
- Use custom exception classes
- Provide context in error messages
- Log errors with appropriate levels
- Implement graceful degradation

### Documentation
- Document all critical functions
- Include usage examples
- Maintain module README files
- Update this guide as needed

### Testing
- Write unit tests for non-UI functions
- Test UI functions in actual environment
- Include edge case testing
- Document test procedures

## 📞 Support and Maintenance

### When to Modify Modules
- **Configuration**: Safe to modify, test configuration loading
- **Utilities**: Safe to modify, test thoroughly
- **UI Automation**: **EXTREME CAUTION** - test extensively
- **Workflow**: Moderate risk - preserve timing
- **Progress Monitoring**: High risk - preserve exact logic

### Debugging Tips
1. Use logging extensively
2. Test one module at a time
3. Compare outputs with original system
4. Monitor timing and performance
5. Test in actual SMA environment

### Rollback Strategy
If issues arise during migration:
1. Identify problematic module
2. Rollback to previous working version
3. Analyze differences
4. Apply fixes incrementally
5. Re-test thoroughly

---

**Remember**: The goal is improved maintainability while preserving 100% functionality. When in doubt, preserve the original behavior exactly. 