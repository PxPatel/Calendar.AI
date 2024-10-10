import React from 'react';
import logo from './logo.svg';
import './App.css';
import Chatbot from './Chatbot';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
      <main>
        <h1>My Chatbot</h1>
        <Chatbot />
      </main>
    </div>
  );
}

export default App;
