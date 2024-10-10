import React, { useState } from "react";
import "./Chatbot.css";

interface Message {
  sender: "user" | "bot"; // Ensure sender is strictly 'user' or 'bot'
  text: string;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  // Replace with actual access token logic
  const accessToken =
    "ya29.a0AcM612xUaOTye8G1670FINbfiu1Vb_2mm3AkfSy2s0c0H81jhn1AmrVIu-BogPslw2k5n7E7bPhkZ_9RAprQ27tqFJEWwvoEl_drtQtSok2mZZZ9JoqOVEXL1DvtbxRFhq5G0t1HzOWNPSZACQOXiNM2K9MiS06-Q79swZwuaCgYKAf4SARISFQHGX2MipyP-MbmDPS4pC6RP85ybVA0175";
  // Handle user input submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

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
        body: JSON.stringify({ prompt: userInput, accessToken: accessToken }), // Sending the prompt and access token
      });

      const data = await response.json();
      console.log(data);

      if (!response.ok) {
        // Handle error responses
        const missingFields = data.message.join(", ");
        setMessages([
          ...newMessages,
          { sender: "bot", text: `Please provide: ${missingFields}` },
        ]);
      } else {
        // Successful response
        setMessages([
          ...newMessages,
          {
            sender: "bot",
            text: `Event created: ${JSON.stringify(data.eventDetails)}`,
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
