// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    // Get the login form element
    const loginForm = document.getElementById('login-form');
    const loginLink = document.getElementById('login-link'); // Get the login/logout link
    const placesListSection = document.getElementById('places-list'); // Section where places will be displayed

    // New elements for place.html
    const placeDetailsSection = document.getElementById('place-details');
    const addReviewSection = document.getElementById('add-review');
    const reviewForm = document.getElementById('review-form');

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
        if (loginLink) { // Check if the element exists (i.e., we are on index.html or login.html or place.html)
            if (isLoggedIn()) {
                loginLink.textContent = 'Logout';
                loginLink.href = '#'; // Change to a hash or prevent default to handle logout via JS
                loginLink.removeEventListener('click', handleLogout); // Remove previous listener to avoid duplicates
                loginLink.addEventListener('click', handleLogout); // Add listener for logout
            } else {
                loginLink.textContent = 'Login';
                loginLink.href = 'login.html';
                loginLink.removeEventListener('click', handleLogout); // Remove listener if not logged in
            }
        }
    }

    // Function to handle logout
    function handleLogout(event) {
        event.preventDefault(); // Prevent navigation
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;'; // Delete the token cookie
        alert('You have been logged out.');
        window.location.href = 'index.html'; // Redirect to home page
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
                    document.cookie = `token=${data.access_token}; path=/;`; // Consider adding secure and samesite=Lax for production
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
        let currentPlaces = []; // To store all fetched places

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
                    <h3>${place.name}</h3> <p class="price-per-night">$${place.price_by_night} / night</p>
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
    if (placeDetailsSection) { // Check if we are on the place.html page
        const placeId = getPlaceIdFromURL();

        if (!placeId) {
            placeDetailsSection.innerHTML = '<h2>Error: Place ID not found in URL.</h2>';
            if (addReviewSection) addReviewSection.style.display = 'none'; // Hide review form if no place
            return;
        }

        // Fetch and display place details on page load
        fetchPlaceDetails(placeId);

        // Manage add review form visibility and submission
        if (addReviewSection) {
            if (isLoggedIn()) {
                addReviewSection.style.display = 'block';
                if (reviewForm) {
                    reviewForm.addEventListener('submit', async (event) => {
                        event.preventDefault();
                        const rating = document.getElementById('rating').value;
                        const comment = document.getElementById('comment').value;
                        await submitReview(placeId, rating, comment);
                    });
                }
            } else {
                addReviewSection.style.display = 'none';
            }
        }
    }

    // Function to extract place ID from URL query parameters
    function getPlaceIdFromURL() {
        const params = new URLSearchParams(window.location.search);
        return params.get('id'); // Assumes the ID parameter is named 'id'
    }

    // Function to fetch place details from the API
    async function fetchPlaceDetails(placeId) {
        try {
            const response = await fetch(API_PLACE_DETAILS_ENDPOINT(placeId), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // No Authorization header needed if place details are public
                    // If your API requires it, uncomment and add:
                    // 'Authorization': `Bearer ${getJwtToken()}`
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

        placeDetailsSection.innerHTML = ''; // Clear previous content

        const placeInfoDiv = document.createElement('div');
        placeInfoDiv.classList.add('place-info'); // Use your existing style for place details

        placeInfoDiv.innerHTML = `
            <h2>${place.name}</h2>
            <p class="price-per-night">$${place.price_by_night} / night</p>
            <p><strong>Description:</strong> ${place.description || 'No description available.'}</p>
            <p><strong>Max Guests:</strong> ${place.max_guest}</p>
            <p><strong>Number of Rooms:</strong> ${place.number_rooms}</p>
            <p><strong>Number of Bathrooms:</strong> ${place.number_bathrooms}</p>
        `;
        placeDetailsSection.appendChild(placeInfoDiv);

        // Display Amenities
        if (place.amenities && place.amenities.length > 0) {
            const amenitiesTitle = document.createElement('h3');
            amenitiesTitle.textContent = 'Amenities';
            placeDetailsSection.appendChild(amenitiesTitle);

            const amenitiesList = document.createElement('ul');
            amenitiesList.classList.add('amenities-list');
            place.amenities.forEach(amenity => {
                const amenityItem = document.createElement('li');
                // Assuming you have images for amenities, e.g., images/icon_wifi.png
                // You might need to map amenity.name to specific image filenames
                // For now, let's just display the name. If you have icons, adjust this.
                // amenityItem.innerHTML = `<img src="images/icon_${amenity.name.toLowerCase()}.png" alt="${amenity.name}"> ${amenity.name}`;
                amenityItem.textContent = amenity.name; // Simpler text-only display
                amenitiesList.appendChild(amenityItem);
            });
            placeDetailsSection.appendChild(amenitiesList);
        } else {
            const noAmenities = document.createElement('p');
            noAmenities.textContent = 'No amenities listed.';
            placeDetailsSection.appendChild(noAmenities);
        }

        // Display Reviews
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

    // Function to submit a new review
    async function submitReview(placeId, rating, comment) {
        const token = getJwtToken();
        if (!token) {
            alert('You must be logged in to submit a review.');
            window.location.href = 'login.html'; // Redirect to login
            return;
        }

        try {
            const response = await fetch(API_ADD_REVIEW_ENDPOINT(placeId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Include JWT token for authentication
                },
                body: JSON.stringify({ rating: parseInt(rating), comment: comment })
            });

            if (response.ok) {
                alert('Review submitted successfully!');
                // Optionally, clear the form and refresh reviews
                if (reviewForm) {
                    reviewForm.reset(); // Clear the form
                }
                fetchPlaceDetails(placeId); // Re-fetch place details to show the new review
            } else {
                const errorData = await response.json();
                alert(`Failed to submit review: ${errorData.message || response.statusText}`);
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            alert('An error occurred while submitting your review. Please try again.');
        }
    }

    // Initialize the login/logout link status when any page loads
    updateLoginLink();
});
