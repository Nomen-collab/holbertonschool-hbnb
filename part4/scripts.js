// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    // Get the login form element
    const loginForm = document.getElementById('login-form');
    const loginLink = document.getElementById('login-link'); // Get the login/logout link
    const placesListSection = document.getElementById('places-list'); // Section where places will be displayed

    // API Endpoints
    const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
    const API_LOGIN_ENDPOINT = `${API_BASE_URL}/auth/login`;
    const API_PLACES_ENDPOINT = `${API_BASE_URL}/places`;

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

    // Function to update login/logout link visibility
    function updateLoginLink() {
        if (loginLink) { // Check if the element exists (i.e., we are on index.html or login.html)
            if (isLoggedIn()) {
                loginLink.textContent = 'Logout';
                loginLink.href = '#'; // Change to a hash or prevent default to handle logout via JS
                loginLink.addEventListener('click', handleLogout);
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

    // Only proceed if the login form exists on the current page (login.html)
    if (loginForm) {
        // Add an event listener for the form submission
        loginForm.addEventListener('submit', async (event) => {
            // Prevent the default form submission behavior (page reload)
            event.preventDefault();

            // Get the email and password values from the form inputs
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                // Make the AJAX request to the login endpoint
                const response = await fetch(API_LOGIN_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    // Send the email and password in the request body as a JSON object
                    body: JSON.stringify({ email, password })
                });

                // Check if the response was successful (status 2xx)
                if (response.ok) {
                    // Parse the JSON response
                    const data = await response.json();

                    // Store the JWT token in a cookie
                    document.cookie = `token=${data.access_token}; path=/;`; // For production, add: secure; samesite=Lax

                    // Redirect the user to the main page (index.html) after successful login
                    window.location.href = 'index.html';
                } else {
                    // If the login fails, parse the error message from the response
                    let errorMessage = 'Login failed. Please try again.';
                    try {
                        const errorData = await response.json();
                        if (errorData.message) {
                            errorMessage = errorData.message;
                        } else if (response.statusText) {
                            errorMessage = `Login failed: ${response.statusText}`;
                        }
                    } catch (e) {
                        // If response is not JSON, use status text
                        errorMessage = `Login failed: ${response.status} - ${response.statusText}`;
                    }
                    // Display an error message to the user
                    alert(errorMessage);
                }
            } catch (error) {
                // Catch any network errors or issues with the fetch request
                console.error('Error during login:', error);
                alert('An error occurred. Please check your network connection.');
            }
        });
    }

    // Logic for index.html - Fetch and display places
    if (placesListSection) { // Check if we are on the index.html page
        const priceFilter = document.getElementById('price-filter');
        let currentPlaces = []; // To store all fetched places

        async function fetchPlaces() {
            try {
                const response = await fetch(API_PLACES_ENDPOINT, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                        // No Authorization header needed for public access to places list
                    }
                });

                if (response.ok) {
                    currentPlaces = await response.json(); // Store all places
                    displayPlaces(currentPlaces); // Display them initially
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
            placesListSection.innerHTML = '<h2>Available Places</h2>'; // Clear previous content and add title
            if (placesToDisplay.length === 0) {
                placesListSection.innerHTML += '<p>No places found matching your criteria.</p>';
                return;
            }

            placesToDisplay.forEach(place => {
                const placeCard = document.createElement('article');
                placeCard.classList.add('place-card');
                placeCard.innerHTML = `
                    <h3>${place.title}</h3>
                    <p class="price-per-night">$${place.price_by_night} / night</p>
                    <p>${place.description || ''}</p>
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

        // Add event listener for the price filter
        priceFilter.addEventListener('change', filterAndDisplayPlaces);

        // Fetch places when the index page loads
        fetchPlaces();
    }

    // Initialize the login/logout link status when any page loads
    updateLoginLink();
});

// The getCookie and isLoggedIn functions are already defined inside DOMContentLoaded.
// If you want them globally accessible, define them outside or attach to window object.
// For this structure, keeping them inside `DOMContentLoaded` is fine as they are called within the script.
