import React, {useState} from 'react';
import SessionTabs from './SessionTabs';
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [exampleUrl, setExampleUrl] = useState("https://en.wikipedia.org/wiki/Led_Zeppelin");
  const [targetUrl, setTargetUrl] = useState("https://en.wikipedia.org/wiki/Jonas_Brothers");

  const handleBeginSession = async () => {
    const response = await fetch('http://localhost:8000/sessions/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        example_url: exampleUrl,
        target_url: targetUrl
      })
    });
    if (!response.ok) {
      console.error(`Failed to start session: ${response.status}`);
    }
    const { session_id } = await response.json();
    setSessionId(session_id);
    console.log(`Set session id to ${session_id}`);
  };

  return (
      <div className="App">
        {!sessionId ? (
            <div className="App-input-container">
              Source Wikipedia Page:
              <input

                  type="text"
                  className="App-input-field"
                  value={exampleUrl}
                  onChange={e => setExampleUrl(e.target.value)}
                  placeholder="Example URL"
              />
              Target Wikipedia Page:
              <input
                  type="text"
                  className="App-input-field"
                  value={targetUrl}
                  onChange={e => setTargetUrl(e.target.value)}
                  placeholder="Target URL"
              />
              <button className="App-begin-button" onClick={handleBeginSession}>Begin Session</button>
            </div>
        ) : (
            <SessionTabs sessionId={sessionId} />
        )}
      </div>
  );
}

export default App;
