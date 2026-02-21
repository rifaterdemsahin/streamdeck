/**
 * Learning Assessment System with Bloom's Taxonomy
 * Reusable component for self-evaluation and progress tracking
 */

class LearningAssessment {
    constructor(options = {}) {
        this.pageId = options.pageId || this.getPageId();
        this.cookieName = 'streamdeck_learning_assessment';
        this.bloomLevels = ['remember', 'understand', 'analyze', 'evaluate', 'create'];
        this.completedLevels = this.loadProgress();
        this.onComplete = options.onComplete || null;

        this.init();
    }

    getPageId() {
        // Use pathname as unique identifier for the page
        return window.location.pathname.split('/').pop().replace('.html', '') || 'index';
    }

    loadProgress() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === this.cookieName) {
                try {
                    const data = JSON.parse(decodeURIComponent(value));
                    return data[this.pageId] || [];
                } catch (e) {
                    console.error('Error parsing learning assessment cookie:', e);
                }
            }
        }
        return [];
    }

    saveProgress() {
        const cookies = document.cookie.split(';');
        let existingData = {};

        // Load existing cookie data
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === this.cookieName) {
                try {
                    existingData = JSON.parse(decodeURIComponent(value));
                } catch (e) {}
                break;
            }
        }

        // Update with current page progress
        existingData[this.pageId] = this.completedLevels;

        // Save back to cookie (expires in 1 year)
        const expiryDate = new Date();
        expiryDate.setFullYear(expiryDate.getFullYear() + 1);
        document.cookie = `${this.cookieName}=${encodeURIComponent(JSON.stringify(existingData))}; expires=${expiryDate.toUTCString()}; path=/`;
    }

    init() {
        // Check if page was previously completed
        if (this.completedLevels.length === this.bloomLevels.length) {
            this.showRememberedBanner();
            this.collapsePanel();
        }

        // Restore checkbox states
        this.completedLevels.forEach(level => {
            const checkbox = document.getElementById(`bloom-${level}`);
            if (checkbox) {
                checkbox.checked = true;
                this.markCompleted(level);
            }
        });

        this.updateProgress();
    }

    toggleLevel(level) {
        const checkbox = document.getElementById(`bloom-${level}`);
        if (!checkbox) return;

        const item = checkbox.closest('.bloom-item');

        if (checkbox.checked) {
            if (!this.completedLevels.includes(level)) {
                this.completedLevels.push(level);
            }
            item.classList.add('completed');
        } else {
            this.completedLevels = this.completedLevels.filter(l => l !== level);
            item.classList.remove('completed');
        }

        this.saveProgress();
        this.updateProgress();

        // Check if all levels completed
        if (this.completedLevels.length === this.bloomLevels.length) {
            this.showCompletion();
        }
    }

    markCompleted(level) {
        const item = document.getElementById(`bloom-${level}`).closest('.bloom-item');
        item.classList.add('completed');
    }

    updateProgress() {
        const progressFill = document.getElementById('learning-progress-fill');
        if (progressFill) {
            const progress = (this.completedLevels.length / this.bloomLevels.length) * 100;
            progressFill.style.width = progress + '%';
        }
    }

    showCompletion() {
        const message = document.getElementById('learning-completion-message');
        if (message) {
            message.style.display = 'block';
            setTimeout(() => {
                this.showRememberedBanner();
                this.collapsePanel();
                if (this.onComplete) {
                    this.onComplete();
                }
            }, 2000);
        }
    }

    showRememberedBanner() {
        const banner = document.getElementById('learning-remembered-banner');
        if (banner) {
            banner.style.display = 'block';
            setTimeout(() => {
                banner.style.display = 'none';
            }, 5000);
        }
    }

    collapsePanel() {
        const panel = document.getElementById('learning-assessment-panel');
        if (panel) {
            panel.classList.add('collapsed');
            const btn = panel.querySelector('.learning-collapse-btn');
            if (btn) {
                btn.textContent = '+';
                btn.onclick = () => this.expandPanel();
            }
        }
    }

    expandPanel() {
        const panel = document.getElementById('learning-assessment-panel');
        if (panel) {
            panel.classList.remove('collapsed');
            const btn = panel.querySelector('.learning-collapse-btn');
            if (btn) {
                btn.textContent = '−';
                btn.onclick = () => this.collapsePanel();
            }
        }
    }
}

// Global functions for HTML onclick handlers
function toggleLearningLevel(level) {
    if (window.learningAssessment) {
        window.learningAssessment.toggleLevel(level);
    }
}

function toggleLearningPanel() {
    if (window.learningAssessment) {
        const panel = document.getElementById('learning-assessment-panel');
        if (panel.classList.contains('collapsed')) {
            window.learningAssessment.expandPanel();
        } else {
            window.learningAssessment.collapsePanel();
        }
    }
}

function closeLearningBanner() {
    const banner = document.getElementById('learning-remembered-banner');
    if (banner) {
        banner.style.display = 'none';
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if the panel exists on the page
    if (document.getElementById('learning-assessment-panel')) {
        window.learningAssessment = new LearningAssessment();
    }
});