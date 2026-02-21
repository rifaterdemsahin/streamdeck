# Learning Assessment Component

A reusable self-evaluation system using Bloom's Taxonomy for the Stream Deck project.

## Overview

This component adds a floating assessment panel to any HTML page, allowing users to self-evaluate their learning progress through Bloom's Taxonomy levels. Progress is stored in cookies and remembered across sessions.

## Features

- **Bloom's Taxonomy Levels**: Remember, Understand, Analyze, Evaluate, Create
- **Progress Tracking**: Visual progress bar and completion indicators
- **Cookie Storage**: Learning progress persists across browser sessions
- **Responsive Design**: Works on desktop and mobile devices
- **Visual Feedback**: Animations, emojis, and color-coded completion states

## Quick Start

### 1. Include the Files

Add these lines to your HTML `<head>`:

```html
<link rel="stylesheet" href="5_Symbols/configs/learning-assessment.css">
<script src="5_Symbols/scripts/learning-assessment.js"></script>
```

### 2. Add the HTML Component

Include this HTML snippet anywhere in your page body:

```html
<!-- Remembered Banner -->
<div class="learning-remembered-banner" id="learning-remembered-banner">
    <div class="learning-banner-content">
        <span class="learning-banner-emoji">🧠</span>
        <span class="learning-banner-text">This page is remembered! 🎯</span>
        <span class="learning-banner-close" onclick="closeLearningBanner()">×</span>
    </div>
</div>

<!-- Learning Assessment Panel -->
<div class="learning-assessment-panel" id="learning-assessment-panel">
    <div class="learning-panel-header">
        <div class="learning-panel-title">🎓 Self-Assessment</div>
        <button class="learning-collapse-btn" onclick="toggleLearningPanel()">−</button>
    </div>

    <div class="learning-panel-content">
        <div class="learning-progress-bar">
            <div class="learning-progress-fill" id="learning-progress-fill"></div>
        </div>

        <!-- Bloom's Taxonomy Checkboxes -->
        <div class="bloom-item" data-level="remember">
            <input type="checkbox" class="bloom-checkbox" id="bloom-remember" onchange="toggleLearningLevel('remember')">
            <label for="bloom-remember" class="bloom-label">
                <span class="custom-checkbox"></span>
                <div>
                    <div class="bloom-emoji">🧠</div>
                    <div class="bloom-text">I can remember the key concepts and facts</div>
                    <div class="bloom-level">REMEMBER</div>
                </div>
            </label>
        </div>

        <!-- Add the other 4 Bloom levels here (understand, analyze, evaluate, create) -->
        <!-- See learning-assessment.html for complete template -->

        <div class="learning-completion-message" id="learning-completion-message">
            🎉 Great job! You've mastered this content!
        </div>
    </div>
</div>
```

### 3. Or Use the Complete Template

For a full working example, copy from `5_Symbols/configs/learning-assessment.html`

## Bloom's Taxonomy Levels

1. **🧠 REMEMBER**: Can recall key concepts and facts
2. **💡 UNDERSTAND**: Comprehends how concepts interconnect
3. **🔍 ANALYZE**: Can break down and examine complex ideas
4. **⚖️ EVALUATE**: Can assess effectiveness and make judgments
5. **🚀 CREATE**: Can develop new applications and solutions

## Customization

### Custom Page ID

```javascript
// Initialize with custom page identifier
window.learningAssessment = new LearningAssessment({
    pageId: 'custom-page-name'
});
```

### Completion Callback

```javascript
window.learningAssessment = new LearningAssessment({
    onComplete: function() {
        console.log('Learning assessment completed!');
        // Add custom completion logic
    }
});
```

### Styling

Modify `learning-assessment.css` to customize:
- Colors and themes
- Panel size and position
- Animation timings
- Responsive breakpoints

## Data Storage

- **Cookie Name**: `streamdeck_learning_assessment`
- **Expiration**: 1 year from last update
- **Format**: JSON object with page IDs as keys
- **Privacy**: Stored locally in browser only

## Browser Support

- Modern browsers with ES6 support
- Cookie storage required
- CSS Grid and Flexbox support
- Backdrop-filter (with webkit prefix fallback)

## Examples

### Basic Implementation
See `3_Simulation/pages/learning-template.html` for a complete working example.

### Integration in Existing Pages
The component is designed to be non-intrusive and can be added to any existing HTML page without affecting layout.

## Troubleshooting

### Panel Not Showing
- Ensure CSS and JS files are properly linked
- Check browser console for JavaScript errors
- Verify HTML structure matches the template

### Progress Not Saving
- Check if cookies are enabled in browser
- Clear cookies if data becomes corrupted
- Verify page ID is unique and valid

### Styling Issues
- Check CSS file path is correct
- Ensure no CSS conflicts with existing styles
- Test responsive behavior on different screen sizes

## Future Enhancements

- Export/import learning progress
- Learning analytics dashboard
- Integration with learning management systems
- Custom assessment criteria
- Multi-language support