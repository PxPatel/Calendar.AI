import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SignIn.css'; // Optional: Add a CSS file for styling

const SignIn: React.FC = () => {
  const navigate = useNavigate();

  const handleSignIn = async () => {
    try {
      // Call the FastAPI backend to get the authentication URL
      const response = await fetch("http://127.0.0.1:8000/generate-auth-url");
      const data = await response.json();

      // Redirect the user to the Google sign-in page
      window.location.href = data.auth_url;
    } catch (error) {
      console.error("Error fetching auth URL:", error);
    }
  };

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