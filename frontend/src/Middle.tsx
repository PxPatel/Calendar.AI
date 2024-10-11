import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const Middle = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Extract the query parameters
    const params = new URLSearchParams(location.search);
    const accessToken = params.get("access_token");

    if (accessToken) {
      // Save the token to localStorage
      localStorage.setItem("access_token", accessToken);
      // Redirect to /chatbot
      navigate("/chatbot", { replace: true });
    } else {
      // If no access token, redirect to /signin
      navigate("/signin", { replace: true });
    }
  }, [location, navigate]);

  return (
    <div>
      {/* You can add a loading spinner or message here if needed */}
      <p>Processing authentication...</p>
    </div>
  );
};

export default Middle;
