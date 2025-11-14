'use strict';

const { useState, useEffect, useRef } = React;

function ChatMessage({ message }) {
    const isUser = message.author === 'user';
    const authorName = isUser ? 'You' : message.author;
    const messageClass = isUser ? 'user' : 'agent';

    // For agent messages, parse Markdown and sanitize the output.
    // For user messages, display plain text.
    const createMarkup = (content) => {
        if (!isUser) {
            // Convert Markdown to HTML using marked, then sanitize with DOMPurify
            const rawMarkup = marked.parse(content || '');
            return { __html: DOMPurify.sanitize(rawMarkup) };
        }
        return null;
    };

    return (
        <div className={`message ${messageClass}`}>
            <div className="message-author">{authorName}</div>
            {isUser ? (
                <div>{message.content}</div>
            ) : (
                <div dangerouslySetInnerHTML={createMarkup(message.content)} />
            )}
        </div>
    );
}

function ChatApp() {
    const [messages, setMessages] = useState([
        { author: 'customer_segmentation_analyst', content: "Hello! I'm the Customer Segmentation Agent. How can I help you analyze your BigQuery data today?" }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [status, setStatus] = useState('Idle');
    const ws = useRef(null);
    const messageListRef = useRef(null);

    useEffect(() => {
        // Establish WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log("WebSocket connection established");
            setStatus('Connected');
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'error') {
                console.error("Error from server:", data.content);
                setStatus('Error');
                return;
            }

            // Display content from final responses, tool outputs, or generic events from any agent
            if (data.content && (data.type === 'FinalResponseEvent' || data.type === 'ToolOutputEvent' || data.type === 'Event')) {
                 // The tool's author is generically named; let's give it a user-friendly name.
                 const author = data.author === '_sub_agent_tool' ? 'bigquery_expert' : data.author;
                 setMessages(prevMessages => [...prevMessages, { author: author, content: data.content }]);
                 setStatus('Idle');
            } else if (data.type !== 'FinalResponseEvent') {
                // Show that the agent is "thinking" or a tool is working
                setStatus(`Thinking... (${data.author})`);
            }
        };

        ws.current.onclose = () => {
            console.log("WebSocket connection closed");
            setStatus('Disconnected. Please refresh.');
        };

        ws.current.onerror = (error) => {
            console.error("WebSocket error:", error);
            setStatus('Connection Error. Please refresh.');
        };

        // Cleanup on component unmount
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    useEffect(() => {
        // Auto-scroll to the latest message
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (inputValue.trim() && ws.current && ws.current.readyState === WebSocket.OPEN) {
            const userMessage = { author: 'user', content: inputValue };
            setMessages(prevMessages => [...prevMessages, userMessage]);
            ws.current.send(inputValue);
            setInputValue('');
            setStatus('Waiting for response...');
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                Customer Segmentation Agent
            </div>
            <div className="message-list" ref={messageListRef}>
                {messages.map((msg, index) => (
                    <ChatMessage key={index} message={msg} />
                ))}
            </div>
            <div className="status-indicator">
                {status !== 'Idle' && status !== 'Connected' && <span>{status}</span>}
            </div>
            <form className="message-input-form" onSubmit={handleSendMessage}>
                <input
                    type="text"
                    className="form-control"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask about datasets, tables, or start segmentation..."
                    disabled={status !== 'Idle' && status !== 'Connected'}
                />
                <button type="submit" className="btn btn-primary" disabled={status !== 'Idle' && status !== 'Connected'}>
                    Send
                </button>
            </form>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ChatApp />);
