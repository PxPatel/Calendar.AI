import React, { useState } from 'react';
import './chatbot.css'; 

interface Message {
  sender: 'user' | 'bot'; // Ensure sender is strictly 'user' or 'bot'
  text: string;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  
  // Replace with actual access token logic
  const accessToken = 'ya29.a0AcM612wNj-QgTOW_8ChHx8u6ToAWR5h3bMoQjGjtKZcLOPGLnmZ7Cxasm8WSYzvoRIXt-c1wK6By-6zXhkeKcQUnz5d-5_B-gC6fkT5DBbQB6VKS8oKKBTJRHAzbfN4Yh3F4yzkUJvZ9tkKllQ3GUHKU4_KC-ZMlLE5KKEd5aCgYKASMSARESFQHGX2MiP9zLjXhDhGs5i9enfhJ0JA0175'; 

  // Handle user input submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    // Add user's message to the chat
    const newMessages: Message[] = [...messages, { sender: 'user', text: userInput }];
    setMessages(newMessages);
    setLoading(true);
    
    try {
      // Make the API call to your FastAPI backend
      const response = await fetch('http://127.0.0.1:8000/scheduleEvent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(
            { prompt: userInput,
              accessToken: accessToken
            }), // Sending the prompt and access token
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle error responses
        const missingFields = data.message.join(', ');
        setMessages([...newMessages, { sender: 'bot', text: `Please provide: ${missingFields}` }]);
      } else {
        // Successful response
        setMessages([...newMessages, { sender: 'bot', text: `Event created: ${JSON.stringify(data.eventDetails)}` }]);
      }
    } catch (error) {
      console.error('Error fetching API:', error);
      setMessages([...newMessages, { sender: 'bot', text: 'Something went wrong, please try again.' }]);
    } finally {
      setLoading(false);
    }

    setUserInput(''); // Reset input
  };

  return (
    <div className="chatbot-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.sender === 'bot' ? (
              <div className="typewriter">
                <h1>{msg.text}</h1>
              </div>
            ) : (
              msg.text
            )}
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="typewriter">
              <h1>Thinking...</h1>
            </div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ask something..."
        />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );
};

export default Chatbot;
