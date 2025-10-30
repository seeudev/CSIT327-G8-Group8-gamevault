/**
 * Review System JavaScript (Module 11)
 * Handles review submission, editing, deletion, and display
 */

const ReviewSystem = {
    gameId: null,
    isAuthenticated: false,
    currentUserReview: null,
    
    /**
     * Initialize the review system
     */
    init: function(gameId, isAuthenticated) {
        this.gameId = gameId;
        this.isAuthenticated = isAuthenticated;
        
        // Load reviews
        this.loadReviews();
        
        // Setup star rating input
        this.setupStarRating();
        
        // Setup review form submission
        if (isAuthenticated) {
            this.setupReviewForm();
        }
    },
    
    /**
     * Load reviews from API
     */
    loadReviews: function() {
        const reviewsList = document.getElementById('reviewsList');
        
        fetch(`/store/api/reviews/${this.gameId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayReviews(data.reviews);
                    this.updateRatingSummary(data.stats);
                    
                    // Check if user has already reviewed
                    if (this.isAuthenticated) {
                        const userReview = data.reviews.find(r => r.is_owner);
                        if (userReview) {
                            this.currentUserReview = userReview;
                            this.hideReviewForm();
                        }
                    }
                } else {
                    reviewsList.innerHTML = '<p class="error-message">Failed to load reviews</p>';
                }
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
                reviewsList.innerHTML = '<p class="error-message">Error loading reviews</p>';
            });
    },
    
    /**
     * Display reviews in the list
     */
    displayReviews: function(reviews) {
        const reviewsList = document.getElementById('reviewsList');
        
        if (reviews.length === 0) {
            reviewsList.innerHTML = `
                <div class="no-reviews">
                    <p>No reviews yet</p>
                    <p style="font-size: 0.9rem; color: #aaa;">Be the first to review this game!</p>
                </div>
            `;
            return;
        }
        
        reviewsList.innerHTML = reviews.map(review => this.renderReviewItem(review)).join('');
        
        // Attach event listeners for edit/delete buttons
        reviews.forEach(review => {
            if (review.is_owner) {
                const editBtn = document.querySelector(`[data-review-id="${review.id}"][data-action="edit"]`);
                const deleteBtn = document.querySelector(`[data-review-id="${review.id}"][data-action="delete"]`);
                
                if (editBtn) {
                    editBtn.addEventListener('click', () => this.showEditForm(review));
                }
                if (deleteBtn) {
                    deleteBtn.addEventListener('click', () => this.deleteReview(review.id));
                }
            }
        });
    },
    
    /**
     * Render a single review item
     */
    renderReviewItem: function(review) {
        const stars = this.renderStars(review.rating);
        const date = new Date(review.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const editedBadge = review.created_at !== review.updated_at ? 
            '<span style="color: #999; font-size: 0.85rem; margin-left: 0.5rem;">(edited)</span>' : '';
        
        return `
            <div class="review-item" id="review-${review.id}">
                <div class="review-header">
                    <div class="review-author">
                        <span class="author-name">${this.escapeHtml(review.username)}</span>
                        <span class="review-stars">${stars}</span>
                    </div>
                    <span class="review-date">${date}${editedBadge}</span>
                </div>
                ${review.review_text ? `<p class="review-text">${this.escapeHtml(review.review_text)}</p>` : ''}
                ${review.is_owner ? `
                    <div class="review-actions">
                        <button class="btn-edit-review" data-review-id="${review.id}" data-action="edit">Edit</button>
                        <button class="btn-delete-review" data-review-id="${review.id}" data-action="delete">Delete</button>
                    </div>
                ` : ''}
            </div>
        `;
    },
    
    /**
     * Render star rating display
     */
    renderStars: function(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            stars += i <= rating ? '★' : '☆';
        }
        return stars;
    },
    
    /**
     * Update rating summary at the top
     */
    updateRatingSummary: function(stats) {
        const ratingNumber = document.querySelector('.rating-number');
        const averageStars = document.getElementById('averageStars');
        const reviewCount = document.getElementById('reviewCount');
        
        if (stats.average_rating) {
            ratingNumber.textContent = stats.average_rating.toFixed(1);
            averageStars.textContent = this.renderStars(Math.round(stats.average_rating));
        } else {
            ratingNumber.textContent = '--';
            averageStars.textContent = '☆☆☆☆☆';
        }
        
        reviewCount.textContent = stats.total_reviews;
    },
    
    /**
     * Setup star rating input interaction
     */
    setupStarRating: function() {
        const starContainer = document.getElementById('starRatingInput');
        if (!starContainer) return;
        
        const stars = starContainer.querySelectorAll('.star');
        const ratingInput = document.getElementById('ratingValue');
        
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                ratingInput.value = rating;
                
                // Update visual state
                stars.forEach(s => {
                    const sRating = parseInt(s.getAttribute('data-rating'));
                    if (sRating <= rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
            
            star.addEventListener('mouseenter', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                stars.forEach(s => {
                    const sRating = parseInt(s.getAttribute('data-rating'));
                    if (sRating <= rating) {
                        s.style.color = '#ffc107';
                    } else {
                        s.style.color = '#ddd';
                    }
                });
            });
        });
        
        starContainer.addEventListener('mouseleave', function() {
            const currentRating = parseInt(ratingInput.value);
            stars.forEach(s => {
                const sRating = parseInt(s.getAttribute('data-rating'));
                if (currentRating > 0 && sRating <= currentRating) {
                    s.style.color = '#ffc107';
                } else {
                    s.style.color = '#ddd';
                }
            });
        });
    },
    
    /**
     * Setup review form submission
     */
    setupReviewForm: function() {
        const form = document.getElementById('reviewForm');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitReview();
        });
    },
    
    /**
     * Submit a new review
     */
    submitReview: function() {
        const rating = parseInt(document.getElementById('ratingValue').value);
        const reviewText = document.getElementById('reviewText').value.trim();
        const submitBtn = document.querySelector('.btn-submit-review');
        
        if (!rating || rating < 1 || rating > 5) {
            alert('Please select a rating');
            return;
        }
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/store/api/reviews/${this.gameId}/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                rating: rating,
                review_text: reviewText
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload reviews
                this.loadReviews();
                
                // Reset form
                document.getElementById('reviewForm').reset();
                document.getElementById('ratingValue').value = 0;
                document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
                
                // Show success message
                this.showMessage('Review submitted successfully!', 'success');
            } else {
                alert(data.error || 'Failed to submit review');
            }
        })
        .catch(error => {
            console.error('Error submitting review:', error);
            alert('Error submitting review');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Review';
        });
    },
    
    /**
     * Show edit form for a review
     */
    showEditForm: function(review) {
        const reviewItem = document.getElementById(`review-${review.id}`);
        
        const stars = Array.from({length: 5}, (_, i) => {
            const rating = i + 1;
            const active = rating <= review.rating ? 'active' : '';
            return `<span class="star ${active}" data-rating="${rating}">★</span>`;
        }).join('');
        
        reviewItem.innerHTML = `
            <div class="review-edit-form">
                <div class="form-group">
                    <label class="form-label">Rating</label>
                    <div class="star-rating-input" id="editStarRating-${review.id}">
                        ${stars}
                    </div>
                    <input type="hidden" id="editRatingValue-${review.id}" value="${review.rating}">
                </div>
                <div class="form-group">
                    <label class="form-label">Review</label>
                    <textarea class="form-textarea" id="editReviewText-${review.id}" rows="4">${this.escapeHtml(review.review_text)}</textarea>
                </div>
                <div class="review-edit-actions">
                    <button class="btn-save-review" onclick="ReviewSystem.saveReviewEdit(${review.id})">Save</button>
                    <button class="btn-cancel-edit" onclick="ReviewSystem.loadReviews()">Cancel</button>
                </div>
            </div>
        `;
        
        // Setup star rating for edit form
        const editStarContainer = document.getElementById(`editStarRating-${review.id}`);
        const editStars = editStarContainer.querySelectorAll('.star');
        const editRatingInput = document.getElementById(`editRatingValue-${review.id}`);
        
        editStars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                editRatingInput.value = rating;
                
                editStars.forEach(s => {
                    const sRating = parseInt(s.getAttribute('data-rating'));
                    if (sRating <= rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });
    },
    
    /**
     * Save edited review
     */
    saveReviewEdit: function(reviewId) {
        const rating = parseInt(document.getElementById(`editRatingValue-${reviewId}`).value);
        const reviewText = document.getElementById(`editReviewText-${reviewId}`).value.trim();
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/store/api/reviews/${reviewId}/update/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                rating: rating,
                review_text: reviewText
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.loadReviews();
                this.showMessage('Review updated successfully!', 'success');
            } else {
                alert(data.error || 'Failed to update review');
            }
        })
        .catch(error => {
            console.error('Error updating review:', error);
            alert('Error updating review');
        });
    },
    
    /**
     * Delete a review
     */
    deleteReview: function(reviewId) {
        if (!confirm('Are you sure you want to delete this review?')) {
            return;
        }
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/store/api/reviews/${reviewId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.currentUserReview = null;
                this.loadReviews();
                this.showReviewForm();
                this.showMessage('Review deleted successfully!', 'success');
            } else {
                alert(data.error || 'Failed to delete review');
            }
        })
        .catch(error => {
            console.error('Error deleting review:', error);
            alert('Error deleting review');
        });
    },
    
    /**
     * Hide review form (when user already reviewed)
     */
    hideReviewForm: function() {
        const formContainer = document.getElementById('reviewFormContainer');
        if (formContainer) {
            formContainer.style.display = 'none';
        }
    },
    
    /**
     * Show review form (when user deletes their review)
     */
    showReviewForm: function() {
        const formContainer = document.getElementById('reviewFormContainer');
        if (formContainer) {
            formContainer.style.display = 'block';
        }
    },
    
    /**
     * Show success/error message
     */
    showMessage: function(message, type) {
        // You can enhance this with a better notification system
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => messageDiv.remove(), 300);
        }, 3000);
    },
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
