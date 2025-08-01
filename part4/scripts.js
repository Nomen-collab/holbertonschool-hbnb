// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    // Get the login form element
    const loginForm = document.getElementById('login-form');
    const loginLink = document.getElementById('login-link'); // Get the login/logout link
    const placesListSection = document.getElementById('places-list'); // Section where places will be displayed

    // New elements for place.html
    const placeDetailsSection = document.getElementById('place-details');
    const addReviewSectionOnPlacePage = document.getElementById('add-review'); // Renommé pour éviter conflit avec add_review.html
    const reviewFormOnPlacePage = document.getElementById('review-form'); // Renommé pour éviter conflit

    // New elements for add_review.html
    const addReviewFormPage = document.getElementById('review-form'); // Le formulaire principal sur add_review.html
    const placeIdDisplayInput = document.getElementById('place-id-display');
    const placeIdHiddenInput = document.getElementById('place-id-hidden');


    // API Endpoints
    const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
    const API_LOGIN_ENDPOINT = `${API_BASE_URL}/auth/login`;
    const API_PLACES_ENDPOINT = `${API_BASE_URL}/places`; // Endpoint for all places (index page)
    const API_PLACE_DETAILS_ENDPOINT = (placeId) => `${API_BASE_URL}/places/${placeId}`; // Endpoint for specific place details
    const API_ADD_REVIEW_ENDPOINT = (placeId) => `${API_BASE_URL}/places/${placeId}/reviews`; // Endpoint to add review for a place

    // Helper function to get a cookie value by name
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Helper function to check if user is logged in
    function isLoggedIn() {
        return getCookie('token') !== null;
    }

    // Function to get the JWT token
    function getJwtToken() {
        return getCookie('token');
    }

    // Function to update login/logout link visibility
    function updateLoginLink() {
        if (loginLink) {
            if (isLoggedIn()) {
                loginLink.textContent = 'Logout';
                loginLink.href = '#';
                loginLink.removeEventListener('click', handleLogout);
                loginLink.addEventListener('click', handleLogout);
            } else {
                loginLink.textContent = 'Login';
                loginLink.href = 'login.html';
                loginLink.removeEventListener('click', handleLogout);
            }
        }
    }

    // Function to handle logout
    function handleLogout(event) {
        event.preventDefault();
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
        alert('You have been logged out.');
        window.location.href = 'index.html';
    }

    // --- Logic for login.html ---
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(API_LOGIN_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/;`;
                    window.location.href = 'index.html';
                } else {
                    let errorMessage = 'Login failed. Please try again.';
                    try {
                        const errorData = await response.json();
                        if (errorData.message) {
                            errorMessage = errorData.message;
                        } else if (response.statusText) {
                            errorMessage = `Login failed: ${response.statusText}`;
                        }
                    } catch (e) {
                        errorMessage = `Login failed: ${response.status} - ${response.statusText}`;
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Error during login:', error);
                alert('An error occurred. Please check your network connection.');
            }
        });
    }

    // --- Logic for index.html - Fetch and display places ---
    if (placesListSection) {
        const priceFilter = document.getElementById('price-filter');
        let currentPlaces = [];

        async function fetchPlaces() {
            try {
                const response = await fetch(API_PLACES_ENDPOINT, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    currentPlaces = await response.json();
                    displayPlaces(currentPlaces);
                } else {
                    console.error('Failed to fetch places:', response.status, response.statusText);
                    placesListSection.innerHTML = '<p>Error: Could not load places. Please try again later.</p>';
                }
            } catch (error) {
                console.error('Network error fetching places:', error);
                placesListSection.innerHTML = '<p>Network error: Could not fetch places.</p>';
            }
        }

        function displayPlaces(placesToDisplay) {
            placesListSection.innerHTML = '<h2>Available Places</h2>';
            if (placesToDisplay.length === 0) {
                placesListSection.innerHTML += '<p>No places found matching your criteria.</p>';
                return;
            }

            placesToDisplay.forEach(place => {
                const placeCard = document.createElement('article');
                placeCard.classList.add('place-card');
                placeCard.innerHTML = `
                    <h3>${place.name}</h3>
                    <p class="price-per-night">$${place.price_by_night} / night</p>
                    <p>${place.description || 'No description available.'}</p>
                    <a href="place.html?id=${place.id}" class="details-button">View Details</a>
                `;
                placesListSection.appendChild(placeCard);
            });
        }

        function filterAndDisplayPlaces() {
            const maxPrice = parseFloat(priceFilter.value);
            let filteredPlaces = currentPlaces;

            if (!isNaN(maxPrice) && maxPrice > 0) {
                filteredPlaces = currentPlaces.filter(place => place.price_by_night <= maxPrice);
            }
            displayPlaces(filteredPlaces);
        }

        priceFilter.addEventListener('change', filterAndDisplayPlaces);
        fetchPlaces();
    }

    // --- Logic for place.html - Display place details and add review form ---
    if (placeDetailsSection) {
        const placeId = getPlaceIdFromURL();

        if (!placeId) {
            placeDetailsSection.innerHTML = '<h2>Error: Place ID not found in URL.</h2>';
            if (addReviewSectionOnPlacePage) addReviewSectionOnPlacePage.style.display = 'none';
            return;
        }

        fetchPlaceDetails(placeId);

        if (addReviewSectionOnPlacePage) {
            if (isLoggedIn()) {
                addReviewSectionOnPlacePage.style.display = 'block';
                if (reviewFormOnPlacePage) {
                    reviewFormOnPlacePage.addEventListener('submit', async (event) => {
                        event.preventDefault();
                        // Changed IDs here to match new add_review.html structure for consistency
                        const rating = document.getElementById('rating').value;
                        const comment = document.getElementById('comment').value; // Changed from review-text
                        await submitReview(placeId, rating, comment);
                    });
                }
            } else {
                addReviewSectionOnPlacePage.style.display = 'none';
            }
        }
    }

    // Function to extract place ID from URL query parameters
    function getPlaceIdFromURL() {
        const params = new URLSearchParams(window.location.search);
        return params.get('id');
    }

    // Function to fetch place details from the API
    async function fetchPlaceDetails(placeId) {
        try {
            const response = await fetch(API_PLACE_DETAILS_ENDPOINT(placeId), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${getJwtToken()}` // Uncomment if place details require auth
                }
            });

            if (response.ok) {
                const place = await response.json();
                displayPlaceDetails(place);
            } else {
                console.error('Failed to fetch place details:', response.status, response.statusText);
                placeDetailsSection.innerHTML = `<h2>Error: Could not load details for place ID ${placeId}.</h2>`;
            }
        } catch (error) {
            console.error('Network error fetching place details:', error);
            placeDetailsSection.innerHTML = '<h2>Network error: Could not fetch place details.</h2>';
        }
    }

    // Function to dynamically display place details
    function displayPlaceDetails(place) {
        if (!placeDetailsSection) return;

        placeDetailsSection.innerHTML = '';

        const placeInfoDiv = document.createElement('div');
        placeInfoDiv.classList.add('place-info');

        placeInfoDiv.innerHTML = `
            <h2>${place.name}</h2>
            <p class="price-per-night">$${place.price_by_night} / night</p>
            <p><strong>Description:</strong> ${place.description || 'No description available.'}</p>
            <p><strong>Max Guests:</strong> ${place.max_guest}</p>
            <p><strong>Number of Rooms:</strong> ${place.number_rooms}</p>
            <p><strong>Number of Bathrooms:</strong> ${place.number_bathrooms}</p>
        `;
        placeDetailsSection.appendChild(placeInfoDiv);

        if (place.amenities && place.amenities.length > 0) {
            const amenitiesTitle = document.createElement('h3');
            amenitiesTitle.textContent = 'Amenities';
            placeDetailsSection.appendChild(amenitiesTitle);

            const amenitiesList = document.createElement('ul');
            amenitiesList.classList.add('amenities-list');
            place.amenities.forEach(amenity => {
                const amenityItem = document.createElement('li');
                amenityItem.textContent = amenity.name;
                amenitiesList.appendChild(amenityItem);
            });
            placeDetailsSection.appendChild(amenitiesList);
        } else {
            const noAmenities = document.createElement('p');
            noAmenities.textContent = 'No amenities listed.';
            placeDetailsSection.appendChild(noAmenities);
        }

        const reviewsTitle = document.createElement('h3');
        reviewsTitle.textContent = 'Reviews';
        placeDetailsSection.appendChild(reviewsTitle);

        if (place.reviews && place.reviews.length > 0) {
            place.reviews.forEach(review => {
                const reviewCard = document.createElement('article');
                reviewCard.classList.add('review-card');
                reviewCard.innerHTML = `
                    <p class="review-comment">"${review.comment}"</p>
                    <p class="review-meta">Rating: ${review.rating}/5 - by User ${review.user_id} on ${new Date(review.created_at).toLocaleDateString()}</p>
                `;
                placeDetailsSection.appendChild(reviewCard);
            });
        } else {
            const noReviews = document.createElement('p');
            noReviews.textContent = 'No reviews yet. Be the first to review!';
            placeDetailsSection.appendChild(noReviews);
        }
    }

    // Function to submit a new review (used by both place.html and add_review.html)
    async function submitReview(placeId, rating, comment) {
        const token = getJwtToken();
        if (!token) {
            alert('You must be logged in to submit a review.');
            window.location.href = 'login.html';
            return false; // Indicate failure
        }

        try {
            const response = await fetch(API_ADD_REVIEW_ENDPOINT(placeId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ rating: parseInt(rating), comment: comment })
            });

            if (response.ok) {
                alert('Review submitted successfully!');
                return true; // Indicate success
            } else {
                const errorData = await response.json();
                alert(`Failed to submit review: ${errorData.message || response.statusText}`);
                return false; // Indicate failure
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            alert('An error occurred while submitting your review. Please try again.');
            return false; // Indicate failure
        }
    }

    // --- Logic for add_review.html - Specific logic for adding a review on a dedicated page ---
    if (addReviewFormPage) { // Check if we are on the add_review.html page by checking for the form
        const token = getJwtToken();
        const placeId = getPlaceIdFromURL();

        // 1. Check User Authentication & Redirect
        if (!token) {
            alert('You must be logged in to add a review. Redirecting to home page.');
            window.location.href = 'index.html'; // Redirect if not authenticated
            return; // Stop further execution on this page
        }

        // 2. Get Place ID from URL (already handled by getPlaceIdFromURL)
        if (!placeId) {
            alert('Error: Place ID not found in URL. Redirecting to home page.');
            window.location.href = 'index.html'; // Redirect if no place ID
            return;
        }

        // Display the place ID in the disabled input field and set it in the hidden input
        if (placeIdDisplayInput) {
            placeIdDisplayInput.value = placeId;
        }
        if (placeIdHiddenInput) {
            placeIdHiddenInput.value = placeId;
        }

        // 3. Setup Event Listener for Review Form
        addReviewFormPage.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Get review text and rating from form
            const rating = document.getElementById('rating').value;
            const comment = document.getElementById('comment').value; // Changed from review-text

            // Validate inputs (optional but good practice)
            if (!rating || !comment) {
                alert('Please provide both a rating and a comment.');
                return;
            }
            if (parseInt(rating) < 1 || parseInt(rating) > 5) {
                alert('Rating must be between 1 and 5.');
                return;
            }

            // 4. Make AJAX Request to Submit Review & Handle API Response
            const success = await submitReview(placeId, rating, comment);

            if (success) {
                // Clear the form
                addReviewFormPage.reset();
                // Optionally, redirect back to place details page or index page
                alert('Review submitted. Redirecting to place details page.');
                window.location.href = `place.html?id=${placeId}`;
            }
            // Error handling is inside submitReview function already
        });
    }

    // Initialize the login/logout link status when any page loads
    updateLoginLink();
});
