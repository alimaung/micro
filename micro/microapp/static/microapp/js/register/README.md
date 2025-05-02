# Progress Component Architecture

## Overview

The Register module uses a centralized Progress Component to manage the workflow progress bar and step indicators. This architecture ensures consistency across the application and prevents race conditions from multiple modules trying to update the same UI elements.

## Key Components

### Progress Component (progress.js)

This is the single source of truth for progress management. It provides:

- Methods to update the active step
- Methods to set the workflow mode
- Events for other modules to listen to step changes
- Initialization based on URL or saved state

### Integration with Page-Specific Modules

Each page-specific module (analysis.js, index.js, etc.) should use the Progress Component API instead of directly manipulating DOM elements.

## Using the Progress Component

### Setting the Active Step

```javascript
// Set the active step (0-based index)
if (window.progressComponent) {
    // Example: Set "Index" (step 4) as active
    window.progressComponent.setActiveStep(3);  // 0-based index (3 = step 4)
}
```

### Setting the Workflow Mode

```javascript
// Set the workflow mode
if (window.progressComponent) {
    window.progressComponent.setWorkflowMode('auto'); // 'auto', 'semi', or 'manual'
}
```

### Listening for Step Changes

```javascript
// Listen for step changes
document.addEventListener('workflow-step-changed', function(e) {
    console.log('Step changed to:', e.detail.stepName, '(', e.detail.stepNumber + 1, ')');
    // Update page-specific UI based on step change
});
```

### Listening for Mode Changes

```javascript
// Listen for workflow mode changes
document.addEventListener('workflow-mode-changed', function(e) {
    console.log('Workflow mode changed to:', e.detail.mode);
    // Update page-specific UI based on mode change
});
```

## Best Practices

1. **Never directly manipulate progress steps** - Always use the Progress Component API

2. **Listen for events** instead of polling for state changes

3. **Initialize page-specific components first**, then call setActiveStep

4. **Respect the single responsibility principle** - Progress Component manages the progress bar, other modules manage their specific functionality

5. **Use the correct step numbers** - Remember that steps are 0-based in the API (step 1 = index 0)

## Step Mapping

| Step Name | Display Number | API Index |
|-----------|----------------|-----------|
| Project   | 1              | 0         |
| Analysis  | 2              | 1         |
| Allocation| 3              | 2         |
| Index     | 4              | 3         |
| Assignment| 5              | 4         |
| References| 6              | 5         |
| Distribution| 7            | 6         |
| Export    | 8              | 7         |

## Examples

### Correct Implementation:

```javascript
// In a page-specific module
document.addEventListener('DOMContentLoaded', function() {
    // First initialize page-specific functionality
    initializeMyPageModule();
    
    // Then update the progress component if needed
    // (though typically this is managed by progress.js based on URL)
    if (window.progressComponent) {
        window.progressComponent.setActiveStep(2); // For Allocation page
    }
});
```

### Incorrect Implementation:

```javascript
// DON'T DO THIS:
document.addEventListener('DOMContentLoaded', function() {
    // Don't directly manipulate progress steps
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach((step, idx) => {
        if (idx === 2) {
            step.classList.add('active');
        } else if (idx < 2) {
            step.classList.add('completed');
        }
    });
});
``` 