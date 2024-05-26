import React, {useEffect, useRef, useState} from 'react';
import 'react-tabs/style/react-tabs.css';
import SectionTab from './SectionTab';
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";

function SessionTabs({ sessionId }) {
    const [sections, setSections] = useState([]);
    const websocket = useRef(null);

    useEffect(() => {
        const fetchSchema = async () => {
            const response = await fetch(`http://localhost:8000/session/${sessionId}/schema`);
            const schema = await response.json();
            const formattedSections = Object.entries(schema).map(([key, value]) => ({
                key: key,
                title: `${key}-${value}`,
                content: [],
                draft: "",
            }));
            setSections(formattedSections);
        };
        fetchSchema();

        // Setup WebSocket connection
        websocket.current = new WebSocket(`ws://localhost:8000/session/${sessionId}/updates`);
        websocket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Received data:", data);

            if (data.type === 'message') {
                setSections(prevSections => prevSections.map(section =>
                    section.key === data.section ? { ...section, content: [...section.content, data.message] } : section
                ));
            }
            else if (data.type === 'output') {
                setSections(prevSections => prevSections.map(section =>
                    section.key === data.section ? { ...section, draft: data.output } : section
                ));
            }
        };

        websocket.current.onerror = (event) => {
            console.error("WebSocket error:", event);
        };

        websocket.current.onclose = (event) => {
            console.log("WebSocket closed:", event);
        };

        // Clean up WebSocket connection when component unmounts
        return () => {
            if (websocket.current) {
                websocket.current.close();
            }
        };
    }, [sessionId]);

    return (
        <Tabs>
            <TabList>
                {sections.map(section => (
                    <Tab key={section.key}>{section.title}</Tab> // Use the key for React key and title for display
                ))}
            </TabList>
            {sections.map(section => (
                <TabPanel key={section.key}>
                    <SectionTab sectionId={section.key} sessionId={sessionId} content={section.content} draft={section.draft}/>
                </TabPanel>
            ))}
        </Tabs>
    );
}

export default SessionTabs;
