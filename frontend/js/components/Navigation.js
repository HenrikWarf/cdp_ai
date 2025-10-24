/**
 * Shared Navigation Component
 * Provides consistent navigation across all pages
 */

export class NavigationComponent {
    constructor() {
        this.currentPage = this.detectCurrentPage();
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('campaign-segmentation')) return 'campaign-segmentation';
        if (path.includes('conversational-analytics')) return 'conversational-analytics';
        return 'overview'; // Default to overview (index.html)
    }

    render(containerId = 'main-nav') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Navigation container not found');
            return;
        }

        const nav = document.createElement('nav');
        nav.className = 'main-navigation';
        nav.innerHTML = `
            <div class="nav-container">
                <div class="nav-brand">
                    <div class="brand-icon">✨</div>
                    <span class="brand-name">AetherSegment AI</span>
                    <span class="brand-tagline">Customer Intelligence Platform</span>
                </div>
                <ul class="nav-menu">
                    <li class="nav-item ${this.currentPage === 'overview' ? 'active' : ''}">
                        <a href="index.html" class="nav-link">
                            <span class="nav-icon">📊</span>
                            <span class="nav-text">Overview</span>
                        </a>
                    </li>
                    <li class="nav-item ${this.currentPage === 'campaign-segmentation' ? 'active' : ''}">
                        <a href="campaign-segmentation.html" class="nav-link">
                            <span class="nav-icon">🎯</span>
                            <span class="nav-text">Campaign Segmentation</span>
                        </a>
                    </li>
                    <li class="nav-item ${this.currentPage === 'conversational-analytics' ? 'active' : ''}">
                        <a href="conversational-analytics.html" class="nav-link">
                            <span class="nav-icon">💬</span>
                            <span class="nav-text">Conversational Analytics</span>
                        </a>
                    </li>
                </ul>
            </div>
        `;

        container.appendChild(nav);
    }
}

