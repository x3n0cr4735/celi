import React, {useState} from 'react';

function SectionTab({ sessionId, sectionId, content, draft }) {
    const [output, setOutput] = useState('');
    const [input, setInput] = useState('');

    const handleInputSubmit = async () => {
        await fetch(`http://localhost:8000/session/${sessionId}/human_input`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ section_id:sectionId, input: input })
        });
        setInput(''); // Optionally clear input after submit
    };

    return (
        <div>
            <h2>{sectionId}</h2>
            <div>CELI Processing</div>
            <div style={{overflowY: 'scroll', height: '200px'}}>
                {content.map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                ))}
            </div>
            <div>Draft Text</div>
            <div style={{overflowY: 'scroll', height: '300px'}}>{draft}</div>
            <textarea rows="3" cols="88" value={input} onChange={e => setInput(e.target.value)}/>
            <button onClick={handleInputSubmit}>Submit Response</button>
        </div>
    );
}

export default SectionTab;
