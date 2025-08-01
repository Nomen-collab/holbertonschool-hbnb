// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    // Get the login form element
    const loginForm = document.getElementById('login-form');

    // Only proceed if the login form exists on the current page
    if (loginForm) {
        // Add an event listener for the form submission
        loginForm.addEventListener('submit', async (event) => {
            // Prevent the default form submission behavior (page reload)
            event.preventDefault();

            // Get the email and password values from the form inputs
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Define your API base URL
            // IMPORTANT: The corrected URL to match your Flask API's /api/v1/auth/login endpoint
            const API_LOGIN_ENDPOINT = 'http://127.0.0.1:5000/api/v1/auth/login'; // <--- CORRECTION APPLIQUÉE ICI

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
                    // 'token' is the name of the cookie
                    // 'data.access_token' is the value of the token from the API response
                    // 'path=/' makes the cookie available across the entire domain
                    // You might also want to add 'secure' and 'samesite=Lax' for production environments
                    document.cookie = `token=${data.access_token}; path=/;`; // Consider adding secure and samesite=Lax for production: secure; samesite=Lax

                    // Redirect the user to the main page (index.html) after successful login
                    window.location.href = 'index.html';
                } else {
                    // If the login fails, parse the error message from the response
                    let errorMessage = 'Login failed. Please try again.';
                    // Attempt to parse JSON error message if available
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

    // --- You will add other scripts for other pages here as you progress ---
    // Example: Code for place.html or add_review.html could go below, or in separate files.
});

// Helper function to get a cookie value by name (useful for later tasks)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Helper function to check if user is logged in (useful for later tasks)
function isLoggedIn() {
    return getCookie('token') !== null;
}
