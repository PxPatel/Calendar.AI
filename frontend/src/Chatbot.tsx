import React, { useEffect, useState } from "react";
import "./chatbot.css";

interface Message {
  sender: "user" | "bot"; // Ensure sender is strictly 'user' or 'bot'
  text: string;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string | null>(null); // State to hold the access token

  useEffect(() => {
    // Retrieve access token from local storage or context
    const token = localStorage.getItem("access_token"); // Adjust according to your storage method
    if (token) {
      setAccessToken(token); // Store it in state
    }
  }, []);

  // Handle user input submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !accessToken) return; // Ensure token is available

    // Add user's message to the chat
    const newMessages: Message[] = [
      ...messages,
      { sender: "user", text: userInput },
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      // Make the API call to your FastAPI backend
      const response = await fetch("http://127.0.0.1:8000/scheduleEvent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userInput, accessToken }), // Sending the prompt and access token
      });

      const data = await response.json();
      console.log(data);

      if (!response.ok || data.verbalStatus === "MISSING_FIELDS") {
        // Handle human-friendly response when there are missing fields
        const missingMessage = data.message;
        setMessages([
          ...newMessages,
          { sender: "bot", text: missingMessage},
        ]);
      } else {
        // Successful response
        setMessages([
          ...newMessages,
          {
            sender: "bot",
            text: `Scheduled successfully!`,
          },
        ]);
      }
    } catch (error) {
      console.error("Error fetching API:", error);
      setMessages([
        ...newMessages,
        { sender: "bot", text: "Something went wrong, please try again." },
      ]);
    } finally {
      setLoading(false);
    }

    setUserInput(""); // Reset input
  };

  return (
    <div className="chatbot-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`slab ${msg.sender}`}>
            <div className="message">{msg.text}</div>
          </div>
        ))}
        {loading && (
          <div className="slab bot">
            <div className="message">Thinking...</div>
          </div>
        )}
      </div>

      <form className="interactive" onSubmit={handleSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ask something..."
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
