/**
 * Onboarding Tour for Agentic Analytics Studio
 * Uses Shepherd.js for guided product walkthrough
 */

import Shepherd from 'shepherd.js';
// import 'shepherd.js/dist/css/shepherd.css'; // Moved to index.html <link>

// Tour configuration
const TOUR_STORAGE_KEY = 'aas_tour_completed';
const TOUR_VERSION = '1.0';

/**
 * Check if user has completed the tour
 */
export function hasTourCompleted() {
    try {
        const completed = localStorage.getItem(TOUR_STORAGE_KEY);
        return completed === TOUR_VERSION;
    } catch (e) {
        return false;
    }
}

/**
 * Mark tour as completed
 */
export function markTourCompleted() {
    try {
        localStorage.setItem(TOUR_STORAGE_KEY, TOUR_VERSION);
    } catch (e) {
        console.warn('Could not save tour completion status');
    }
}

/**
 * Reset tour (for testing or "Take Tour Again")
 */
export function resetTour() {
    try {
        localStorage.removeItem(TOUR_STORAGE_KEY);
    } catch (e) {
        console.warn('Could not reset tour status');
    }
}

/**
 * Create and configure the tour
 */
export function createTour() {
    const tour = new Shepherd.Tour({
        useModalOverlay: true,
        defaultStepOptions: {
            classes: 'aas-tour-step',
            scrollTo: { behavior: 'smooth', block: 'center' },
            cancelIcon: {
                enabled: true
            },
            modalOverlayOpeningPadding: 8,
            modalOverlayOpeningRadius: 8,
        }
    });

    // Step 1: Welcome & Play Selection
    tour.addStep({
        id: 'welcome',
        title: '👋 Welcome to Agentic Analytics Studio',
        text: `
      <p>AAS transforms business questions into actionable insights using AI agents.</p>
      <p>Let's take a quick tour to see how it works!</p>
    `,
        buttons: [
            {
                text: 'Skip Tour',
                action: tour.cancel,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Start Tour',
                action: tour.next
            }
        ]
    });

    // Step 2: Play Selector
    tour.addStep({
        id: 'play-selector',
        title: '🎯 Select a Hero Play',
        text: `
      <p>Choose from our hero plays:</p>
      <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
        <li><strong>Pipeline Leakage:</strong> Find at-risk deals</li>
        <li><strong>Churn Rescue:</strong> Identify churn risks</li>
        <li><strong>Spend Anomaly:</strong> Detect unusual spending</li>
        <li><strong>Revenue Forecasting:</strong> Predict shortfalls</li>
      </ul>
    `,
        attachTo: {
            element: '#play-select',
            on: 'bottom'
        },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Next',
                action: tour.next
            }
        ]
    });

    // Step 3: Run Audit Button
    tour.addStep({
        id: 'run-audit',
        title: '🚀 Run an Agentic Audit',
        text: `
      <p>Click here to run an AI-powered audit against your Tableau-backed dataset.</p>
      <p>The agent will analyze the data and generate ranked recommendations.</p>
    `,
        attachTo: {
            element: '#run-pipeline-btn',
            on: 'bottom'
        },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Next',
                action: tour.next
            }
        ]
    });

    // Step 4: Tableau Visualization
    tour.addStep({
        id: 'tableau-viz',
        title: '📊 Live Tableau Dashboard',
        text: `
      <p>Your Tableau visualization appears here, providing real-time context for the analysis.</p>
      <p>The agent uses this data to generate insights and recommendations.</p>
    `,
        attachTo: {
            element: '#viz-panel',
            on: 'right'
        },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Next',
                action: tour.next
            }
        ]
    });

    // Step 5: Action Panel
    tour.addStep({
        id: 'actions-panel',
        title: '✨ Ranked Recommendations',
        text: `
      <p>Actions are ranked by <strong>Impact Score</strong> with AI-generated rationales.</p>
      <p>Each action shows:</p>
      <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
        <li>Priority (High/Medium/Low)</li>
        <li>Impact Score (potential ROI)</li>
        <li>AI Rationale (transparent reasoning)</li>
      </ul>
    `,
        attachTo: {
            element: '#action-panel',
            on: 'left'
        },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Next',
                action: tour.next
            }
        ]
    });

    // Step 6: Approve Actions
    tour.addStep({
        id: 'approve-actions',
        title: '✅ One-Click Execution',
        text: `
      <p>Approve actions to execute them automatically:</p>
      <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
        <li><strong>With Salesforce:</strong> Creates real tasks</li>
        <li><strong>Without Salesforce:</strong> Safe stub mode</li>
        <li><strong>Slack:</strong> Instant notifications (if configured)</li>
      </ul>
      <p style="margin-top: 0.5rem;">All actions are logged for audit trails.</p>
    `,
        attachTo: {
            element: '#approve-all-btn',
            on: 'top'
        },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
                classes: 'shepherd-button-secondary'
            },
            {
                text: 'Finish Tour',
                action: () => {
                    markTourCompleted();
                    tour.complete();
                }
            }
        ]
    });

    // Tour event handlers
    tour.on('cancel', () => {
        markTourCompleted(); // Don't show again even if cancelled
    });

    tour.on('complete', () => {
        console.log('Tour completed!');
    });

    return tour;
}

/**
 * Start the tour if it hasn't been completed
 */
export function startTourIfNeeded() {
    if (!hasTourCompleted()) {
        const tour = createTour();
        // Small delay to ensure DOM is ready
        setTimeout(() => tour.start(), 500);
    }
}

/**
 * Manually start the tour (for "Take Tour" button)
 */
export function startTour() {
    const tour = createTour();
    tour.start();
}
