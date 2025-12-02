/**
 * Module 17: AI Hybrid Market Analysis - Frontend
 * Handles fetching and displaying AI consensus data
 */

const AIConsensus = {
    gameId: null,
    
    init: function(gameId) {
        this.gameId = gameId;
        this.loadConsensus();
    },
    
    loadConsensus: function(forceRefresh = false) {
        const url = `/store/api/ai/consensus/${this.gameId}/${forceRefresh ? '?refresh=true' : ''}`;
        
        // Show loading state
        document.getElementById('consensusLoading').style.display = 'flex';
        document.getElementById('consensusContent').style.display = 'none';
        document.getElementById('consensusError').style.display = 'none';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.renderConsensus(data.data);
                } else {
                    this.showError(data.error);
                }
            })
            .catch(error => {
                console.error('Error loading consensus:', error);
                this.showError('Failed to load AI analysis');
            });
    },
    
    renderConsensus: function(data) {
        // Hide loading, show content
        document.getElementById('consensusLoading').style.display = 'none';
        document.getElementById('consensusContent').style.display = 'block';
        
        // Render local sentiment
        if (data.local_sentiment !== null) {
            document.getElementById('localScore').textContent = data.local_sentiment.toFixed(1);
            document.getElementById('localCount').textContent = data.local_review_count;
            document.getElementById('localBar').style.width = data.local_sentiment + '%';
        } else {
            document.getElementById('localScore').textContent = 'N/A';
            document.getElementById('localCount').textContent = '0';
            document.getElementById('localBar').style.width = '0%';
        }
        
        // Render global sentiment
        if (data.global_sentiment !== null && data.exists_externally) {
            document.getElementById('globalScore').textContent = data.global_sentiment.toFixed(1);
            document.getElementById('globalLabel').textContent = `${data.sources.length} external sources`;
            document.getElementById('globalBar').style.width = data.global_sentiment + '%';
        } else if (!data.exists_externally) {
            document.getElementById('globalScore').textContent = 'N/A';
            document.getElementById('globalLabel').textContent = 'Not found externally';
            document.getElementById('globalBar').style.width = '0%';
        } else {
            document.getElementById('globalScore').textContent = '--';
            document.getElementById('globalLabel').textContent = 'No data available';
            document.getElementById('globalBar').style.width = '0%';
        }
        
        // Render AI verdict
        document.getElementById('verdictText').textContent = data.verdict;
        
        // Render sources if available
        if (data.sources && data.sources.length > 0) {
            this.renderSources(data.sources);
            document.getElementById('verifiedSources').style.display = 'block';
        } else {
            document.getElementById('verifiedSources').style.display = 'none';
        }
        
        // Add divergence badge if applicable
        if (data.divergence !== null) {
            this.showDivergenceBadge(data.divergence);
        }
    },
    
    renderSources: function(sources) {
        const sourcesGrid = document.getElementById('sourcesGrid');
        sourcesGrid.innerHTML = '';
        
        sources.forEach(source => {
            const sourceCard = document.createElement('a');
            sourceCard.href = source.url;
            sourceCard.target = '_blank';
            sourceCard.rel = 'noopener noreferrer';
            sourceCard.className = 'source-card';
            
            // Determine sentiment color
            let sentimentClass = 'mixed';
            if (source.sentiment === 'Positive') sentimentClass = 'positive';
            else if (source.sentiment === 'Negative') sentimentClass = 'negative';
            
            sourceCard.innerHTML = `
                <div class="source-header">
                    <span class="source-name">${this.escapeHtml(source.source_name)}</span>
                    <span class="source-sentiment sentiment-${sentimentClass}">${source.sentiment}</span>
                </div>
                ${source.excerpt ? `<div class="source-excerpt">${this.escapeHtml(source.excerpt)}</div>` : ''}
                <div class="source-link">
                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                        <polyline points="15 3 21 3 21 9"></polyline>
                        <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                    Visit Source
                </div>
            `;
            
            sourcesGrid.appendChild(sourceCard);
        });
    },
    
    showDivergenceBadge: function(divergence) {
        let badge = '';
        let badgeClass = '';
        
        if (divergence < 10) {
            badge = 'Strong Agreement';
            badgeClass = 'agreement-high';
        } else if (divergence < 20) {
            badge = 'General Agreement';
            badgeClass = 'agreement-medium';
        } else if (divergence < 30) {
            badge = 'Moderate Divergence';
            badgeClass = 'divergence-medium';
        } else {
            badge = 'Significant Divergence';
            badgeClass = 'divergence-high';
        }
        
        const verdictDiv = document.getElementById('aiVerdict');
        const existingBadge = verdictDiv.querySelector('.divergence-badge');
        if (existingBadge) existingBadge.remove();
        
        const badgeEl = document.createElement('div');
        badgeEl.className = `divergence-badge ${badgeClass}`;
        badgeEl.textContent = badge;
        verdictDiv.insertBefore(badgeEl, verdictDiv.firstChild);
    },
    
    showError: function(message) {
        document.getElementById('consensusLoading').style.display = 'none';
        document.getElementById('consensusContent').style.display = 'none';
        document.getElementById('consensusError').style.display = 'block';
        document.getElementById('consensusError').querySelector('p').textContent = message;
    },
    
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Global function for refresh button
function refreshConsensus() {
    const btn = document.getElementById('refreshBtn');
    btn.disabled = true;
    btn.innerHTML = `
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" class="spin-animation">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
        </svg>
        Refreshing...
    `;
    
    fetch(`/store/api/ai/consensus/${AIConsensus.gameId}/refresh/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Analysis refreshed successfully', 'success');
            AIConsensus.loadConsensus();
        } else {
            showToast(data.error || 'Failed to refresh analysis', 'error');
        }
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
            Refresh
        `;
    })
    .catch(error => {
        console.error('Error refreshing consensus:', error);
        showToast('Failed to refresh analysis', 'error');
        btn.disabled = false;
    });
}
