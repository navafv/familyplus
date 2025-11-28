// Show Message Banner
function showMessage(type = 'info', title, message, duration = 5000) {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const banner = document.createElement('div');
    
    let bgColor, textColor, iconClass;

    switch (type) {
        case 'success':
            bgColor = 'bg-accent';
            textColor = 'text-white';
            iconClass = 'fa-check-circle';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            iconClass = 'fa-times-circle';
            break;
        case 'info':
        default:
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
            iconClass = 'fa-info-circle';
            break;
    }

    banner.className = `w-full max-w-4xl mx-auto ${bgColor} ${textColor} rounded-lg shadow-lg flex items-center justify-between p-4 mb-2 message-banner-enter pointer-events-auto`;
    
    banner.innerHTML = `
        <div class="flex items-center">
            <span class="text-xl mr-3"><i class="fas ${iconClass}"></i></span>
            <p class="text-sm"><span class="font-bold mr-1">${title}</span> ${message}</p>
        </div>
        <button class="text-xl opacity-70 hover:opacity-100 focus:outline-none">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(banner);

    requestAnimationFrame(() => {
        banner.classList.add('message-banner-enter-active');
    });

    const closeButton = banner.querySelector('button');
    
    const removeBanner = () => {
        banner.classList.remove('message-banner-enter-active');
        banner.classList.add('message-banner-exit-active');
        banner.addEventListener('transitionend', () => {
            banner.remove();
        });
    };
    
    closeButton.addEventListener('click', removeBanner);

    if (duration > 0) {
        setTimeout(removeBanner, duration);
    }
}

// DOMContentLoaded Logic for Menus, Search, Modals
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu & Search
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileSearchButton = document.getElementById('mobile-search-button');
    const mobileSearchOverlay = document.getElementById('mobile-search-overlay');
    const closeSearchButton = document.getElementById('close-search-button');

    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
    }

    if (mobileSearchButton && mobileSearchOverlay && closeSearchButton) {
        mobileSearchButton.addEventListener('click', () => {
            mobileSearchOverlay.classList.remove('hidden');
            mobileSearchOverlay.querySelector('input').focus();
            if (mobileMenu) mobileMenu.classList.add('hidden');
        });
        closeSearchButton.addEventListener('click', () => mobileSearchOverlay.classList.add('hidden'));
    }

    // Review Modal Logic
    const reviewModal = document.getElementById('review-modal');
    const openReviewModalBtn = document.getElementById('open-review-modal-btn');
    const closeReviewModalBtn = document.getElementById('close-review-modal');
    const starRatingContainer = document.getElementById('star-rating');
    const ratingValueInput = document.getElementById('rating-value');

    if (reviewModal && openReviewModalBtn && closeReviewModalBtn && starRatingContainer && ratingValueInput) {
        const stars = starRatingContainer.querySelectorAll('.fa-star');

        openReviewModalBtn.addEventListener('click', () => {
            reviewModal.classList.remove('hidden');
            reviewModal.classList.add('flex');
        });

        const closeModal = () => {
            reviewModal.classList.add('hidden');
            reviewModal.classList.remove('flex');
        };

        closeReviewModalBtn.addEventListener('click', closeModal);
        reviewModal.addEventListener('click', (e) => {
            if (e.target === reviewModal) closeModal();
        });

        stars.forEach(star => {
            star.addEventListener('mouseover', () => {
                const rating = star.dataset.value;
                stars.forEach(s => {
                    s.classList.toggle('text-yellow-400', s.dataset.value <= rating);
                    s.classList.toggle('text-gray-300', s.dataset.value > rating);
                });
            });

            star.addEventListener('mouseout', () => {
                const currentRating = ratingValueInput.value;
                stars.forEach(s => {
                    s.classList.toggle('text-yellow-400', s.dataset.value <= currentRating);
                    s.classList.toggle('text-gray-300', s.dataset.value > currentRating);
                });
            });

            star.addEventListener('click', () => ratingValueInput.value = star.dataset.value);
        });
    }

    // Dashboard Navigation Logic
    const dashboardNavLinks = document.querySelectorAll('.dashboard-nav-link');
    const dashboardPages = document.querySelectorAll('.dashboard-page');

    dashboardNavLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = e.currentTarget.dataset.dashboardPage;
            if (!pageId) return;

            dashboardNavLinks.forEach(nav => {
                nav.classList.remove('bg-secondary', 'text-primary');
                nav.classList.add('text-text-dark');
            });
            e.currentTarget.classList.add('bg-secondary', 'text-primary');
            e.currentTarget.classList.remove('text-text-dark');

            dashboardPages.forEach(page => page.classList.add('hidden'));
            const pageToShow = document.getElementById(`dashboard-${pageId}`);
            if (pageToShow) pageToShow.classList.remove('hidden');
        });
    });
});

// Django messages integration
window.addEventListener('load', function() {
    if (typeof messages !== 'undefined') {
        messages.forEach(msg => {
            let type = msg.tags === 'warning' ? 'info' : msg.tags;
            let title = type.charAt(0).toUpperCase() + type.slice(1) + '!';
            showMessage(type, title, msg.message);
        });
    }
});
