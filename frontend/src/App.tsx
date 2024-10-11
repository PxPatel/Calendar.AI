import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignIn from "./SigningIn"; // Make sure the path is correct based on your file structure
import Chatbot from "./Chatbot"; // Make sure the path is correct based on your file structure
import Middle from "./Middle";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/middle" element={<Middle />} />
      </Routes>
    </Router>
  );
};

export default App;
