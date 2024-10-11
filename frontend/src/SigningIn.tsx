import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const SignIn: React.FC = () => {
  const navigate = useNavigate();

  const handleSignIn = async () => {
    try {
      
      // Fetch the Google auth URL from the FastAPI backend
      const response = await fetch("http://127.0.0.1:8000/generate-auth-url");
      console.log("made it to the response");
      const data = await response.json();

      // Redirect to Google for authentication
      const authUrl = data.auth_url.auth_url; // Convert to string

        // Check if authUrl is valid and not empty
        if (typeof(authUrl) === 'string' && authUrl.trim()) {
            console.log("Redirecting to:", authUrl); // Log the URL to be redirected
            window.location.href = authUrl; // Redirect to the auth URL
        } else {
            console.error("Auth URL is missing or not a valid string:", authUrl);
        }
          } catch (error) {
      console.error("Error fetching auth URL:", error);
    }
  };

  const handleTokenSave = useCallback(async (token: string) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/store-token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token }),
      });

      if (response.ok) {
        navigate("/calendar"); // Redirect after successful sign-in
      } else {
        console.error("Failed to save token");
      }
    } catch (error) {
      console.error("Error saving token:", error);
    }
  }, [navigate]); // Include navigate as a dependency

  // Use useEffect to check for access_token in the URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");

    if (accessToken) {
      console.log("Access Token from URL:", accessToken);
      handleTokenSave(accessToken);
    }
  }, [handleTokenSave]); // Include handleTokenSave as a dependency

  return (
    <div className="signin-container">
      <h1>Sign In</h1>
      <button onClick={handleSignIn} className="signin-button">
        Sign in with Google
      </button>
    </div>
  );
};

export default SignIn;