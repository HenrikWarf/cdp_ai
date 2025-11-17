'use strict';

const { useState, useEffect, useRef } = React;

// ============================================
// Utility Functions
// ============================================

/**
 * Parse table data from markdown table format
 */
function parseTableData(content) {
    const lines = content.split('\n').filter(line => line.trim());
    
    // Find table in content (lines with |)
    const tableLines = lines.filter(line => line.includes('|'));
    
    if (tableLines.length < 2) return null;
    
    // Parse headers
    const headers = tableLines[0]
        .split('|')
        .map(h => h.trim())
        .filter(h => h);
    
    // Skip separator line (----)
    const dataLines = tableLines.slice(2);
    
    // Parse rows
    const rows = dataLines.map(line => {
        const cells = line.split('|').map(c => c.trim()).filter(c => c);
        const row = {};
        headers.forEach((header, index) => {
            row[header] = cells[index] || '';
        });
        return row;
    });
    
    return { headers, rows };
}

/**
 * Export data to CSV format
 */
function exportToCSV(data) {
    if (!data || !data.rows) return;
    
    const { headers, rows } = data;
    
    // Create CSV content
    const csvContent = [
        headers.join(','),
        ...rows.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
    ].join('\n');
    
    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query_results_${new Date().getTime()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Export data to JSON format
 */
function exportToJSON(data) {
    if (!data || !data.rows) return;
    
    const jsonContent = JSON.stringify(data.rows, null, 2);
    
    // Download file
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query_results_${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy:', err);
        return false;
    }
}

// ============================================
// Chat Message Component
// ============================================

function ChatMessage({ message }) {
    const isUser = message.author === 'user';
    const authorName = isUser ? 'You' : message.author;
    const messageClass = isUser ? 'user' : 'agent';

    // For agent messages, parse Markdown and sanitize the output.
    const createMarkup = (content) => {
        if (!isUser) {
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

// ============================================
// Tab Navigation Component
// ============================================

function TabNavigation({ activeTab, onTabChange, hasResults }) {
    const tabs = [
        { id: 'overview', label: 'Overview', icon: '📊', disabled: false },
        { id: 'table', label: 'Table', icon: '📋', disabled: !hasResults },
        { id: 'chart', label: 'Chart', icon: '📈', disabled: !hasResults },
        { id: 'sql', label: 'SQL Query', icon: '💻', disabled: !hasResults }
    ];

    return (
        <div className="results-tabs">
            <div className="tabs-left">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => onTabChange(tab.id)}
                        disabled={tab.disabled}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span>{tab.label}</span>
                    </button>
                ))}
            </div>
            <div className="tabs-right">
                <button
                    className={`tab-button metadata-button ${activeTab === 'metadata' ? 'active' : ''}`}
                    onClick={() => onTabChange('metadata')}
                >
                    <span className="tab-icon">📖</span>
                    <span>Table Metadata</span>
                </button>
            </div>
        </div>
    );
}

// ============================================
// Table Metadata Component
// ============================================

function TableMetadataView() {
    const metadata = [
        // Core Profile
        { column: 'customer_id', description: 'Unique identifier for each customer' },
        { column: 'email_address', description: 'Customer email address' },
        { column: 'first_name', description: 'Customer first name' },
        { column: 'location_city', description: 'City where customer is located' },
        { column: 'location_country', description: 'Country where customer is located' },
        { column: 'acquisition_source', description: 'Channel through which customer was acquired' },
        { column: 'creation_date', description: 'Date when customer account was created' },
        { column: 'days_as_customer', description: 'Number of days since account creation' },
        { column: 'age', description: 'Customer age in years' },
        { column: 'gender', description: 'Customer gender (Male, Female, Non-Binary, Prefer Not to Say)' },
        { column: 'income_level', description: 'Income bracket (low, medium, high, premium)' },
        { column: 'clv_score', description: 'Customer Lifetime Value score (0-1 scale)' },
        
        // ML Scores & Affinities
        { column: 'discount_sensitivity_score', description: 'Likelihood to purchase with discount (0-1 scale)' },
        { column: 'free_shipping_sensitivity_score', description: 'Likelihood to purchase with free shipping (0-1 scale)' },
        { column: 'exclusivity_seeker_flag', description: 'Whether customer prefers exclusive/premium products (boolean)' },
        { column: 'churn_probability_score', description: 'Probability of customer churn (0-1 scale)' },
        { column: 'social_proof_affinity', description: 'Responsiveness to social proof and reviews (0-1 scale)' },
        { column: 'content_engagement_score', description: 'Level of engagement with content and marketing (0-1 scale)' },
        
        // Product Category Affinities
        { column: 'living_room_affinity', description: 'Affinity for living room furniture category (0-1 scale)' },
        { column: 'bedroom_affinity', description: 'Affinity for bedroom furniture category (0-1 scale)' },
        { column: 'kitchen_dining_affinity', description: 'Affinity for kitchen & dining category (0-1 scale)' },
        { column: 'office_affinity', description: 'Affinity for office furniture category (0-1 scale)' },
        { column: 'outdoor_affinity', description: 'Affinity for outdoor furniture category (0-1 scale)' },
        { column: 'lighting_affinity', description: 'Affinity for lighting products category (0-1 scale)' },
        { column: 'storage_affinity', description: 'Affinity for storage solutions category (0-1 scale)' },
        { column: 'textiles_affinity', description: 'Affinity for textiles category (0-1 scale)' },
        { column: 'bathroom_affinity', description: 'Affinity for bathroom products category (0-1 scale)' },
        { column: 'decoration_affinity', description: 'Affinity for decoration category (0-1 scale)' },
        
        // Purchase Profile
        { column: 'favorite_category', description: 'Customer\'s most frequently purchased category' },
        { column: 'secondary_category', description: 'Customer\'s second most purchased category' },
        { column: 'cross_category_shopper', description: 'Whether customer shops across multiple categories (boolean)' },
        { column: 'price_tier_preference', description: 'Preferred price tier (budget, mid-range, premium)' },
        
        // Transaction Metrics (All-time)
        { column: 'total_purchases', description: 'Total number of purchases (all-time)' },
        { column: 'total_revenue', description: 'Total revenue generated by customer (all-time)' },
        { column: 'avg_order_value', description: 'Average order value across all purchases' },
        { column: 'first_purchase_date', description: 'Date of first purchase' },
        { column: 'last_purchase_date', description: 'Date of most recent purchase' },
        { column: 'days_since_last_purchase', description: 'Number of days since last purchase' },
        { column: 'purchase_frequency_per_month', description: 'Average number of purchases per month' },
        
        // Transaction Metrics (90 days)
        { column: 'purchases_90d', description: 'Number of purchases in last 90 days' },
        { column: 'revenue_90d', description: 'Revenue generated in last 90 days' },
        { column: 'avg_order_value_90d', description: 'Average order value for last 90 days' },
        
        // Transaction Metrics (30 days)
        { column: 'purchases_30d', description: 'Number of purchases in last 30 days' },
        { column: 'revenue_30d', description: 'Revenue generated in last 30 days' },
        { column: 'avg_order_value_30d', description: 'Average order value for last 30 days' },
        
        // Transaction Category Insights
        { column: 'most_purchased_category', description: 'Product category purchased most frequently' },
        { column: 'most_recent_category', description: 'Product category of most recent purchase' },
        
        // Cart Abandonment Metrics
        { column: 'total_abandoned_carts', description: 'Total number of abandoned carts (all-time)' },
        { column: 'total_abandoned_cart_value', description: 'Total value of abandoned carts (all-time)' },
        { column: 'avg_abandoned_cart_value', description: 'Average value per abandoned cart' },
        { column: 'last_cart_abandonment_date', description: 'Date of most recent cart abandonment' },
        { column: 'days_since_last_cart_abandonment', description: 'Days since last cart abandonment' },
        { column: 'abandoned_carts_30d', description: 'Number of abandoned carts in last 30 days' },
        { column: 'abandoned_cart_value_30d', description: 'Value of abandoned carts in last 30 days' },
        { column: 'abandoned_carts_90d', description: 'Number of abandoned carts in last 90 days' },
        
        // Behavioral Engagement Metrics
        { column: 'total_events_lifetime', description: 'Total number of behavioral events (all-time)' },
        { column: 'last_event_date', description: 'Date of most recent behavioral event' },
        { column: 'days_since_last_event', description: 'Days since last behavioral event' },
        { column: 'events_90d', description: 'Number of behavioral events in last 90 days' },
        { column: 'events_30d', description: 'Number of behavioral events in last 30 days' },
        { column: 'most_viewed_category', description: 'Product category viewed most frequently' },
        { column: 'engagement_rate_per_day', description: 'Average number of events per day' },
        
        // Campaign Response Metrics
        { column: 'total_campaigns_received', description: 'Total number of campaigns received (all-time)' },
        { column: 'total_campaigns_converted', description: 'Total number of campaigns that led to conversion' },
        { column: 'overall_conversion_rate', description: 'Overall campaign conversion rate (0-1 scale)' },
        { column: 'campaigns_90d', description: 'Number of campaigns received in last 90 days' },
        { column: 'conversions_90d', description: 'Number of conversions in last 90 days' },
        { column: 'conversion_rate_90d', description: 'Campaign conversion rate for last 90 days (0-1 scale)' },
        { column: 'campaigns_30d', description: 'Number of campaigns received in last 30 days' },
        { column: 'most_responsive_trigger_type', description: 'Trigger type that generates most conversions' },
        { column: 'last_campaign_date', description: 'Date of most recent campaign' },
        { column: 'days_since_last_campaign', description: 'Days since last campaign was sent' },
        
        // Metadata
        { column: 'last_updated_at', description: 'Timestamp of last table update' }
    ];

    return (
        <div className="metadata-container">
            <div className="metadata-header">
                <div className="metadata-title">
                    <span className="metadata-icon">📖</span>
                    <h3>cdp_data.customers</h3>
                </div>
                <div className="metadata-subtitle">
                    {metadata.length} columns • Consolidated customer table with all behavioral, transactional, and ML-driven insights
                </div>
            </div>
            <div className="metadata-grid">
                {metadata.map((item, index) => (
                    <div key={index} className="metadata-row">
                        <div className="metadata-column-name">
                            <span className="column-type-icon">▸</span>
                            <code>{item.column}</code>
                        </div>
                        <div className="metadata-description">{item.description}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ============================================
// Empty State Component
// ============================================

function OverviewEmptyState({ onExampleClick }) {
    const examples = [
        'Show top 10 customers by CLV score',
        'Find high-value customers with high churn risk',
        'List customers who purchased in last 30 days',
        'Analyze customer distribution by country',
        'Show customers with high discount sensitivity',
        'Find customers aged 25-40 with premium income',
        'List customers by most purchased category',
        'Show customers with low days since last purchase',
        'Find high CLV customers in specific locations',
        'Analyze average order value by customer segment',
    ];

    return (
        <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <h3>Ready to explore your data</h3>
            <p>Ask questions about your datasets, tables, or start analyzing customer segments</p>
            <div className="example-queries">
                {examples.map((example, index) => (
                    <button
                        key={index}
                        className="example-chip"
                        onClick={() => onExampleClick(example)}
                    >
                        {example}
                    </button>
                ))}
            </div>
        </div>
    );
}

// ============================================
// Data Table View Component
// ============================================

function DataTableView({ data, onExport, onCopy }) {
    if (!data || !data.rows || data.rows.length === 0) {
        return (
            <div className="empty-state">
                <p>No data to display</p>
            </div>
        );
    }

    const { headers, rows } = data;
    const rowCount = rows.length;

    const handleCopy = async () => {
        const tableText = [
            headers.join('\t'),
            ...rows.map(row => headers.map(h => row[h] || '').join('\t'))
        ].join('\n');
        
        const success = await copyToClipboard(tableText);
        if (success && onCopy) {
            onCopy();
        }
    };

    return (
        <div className="data-table-container">
            <div className="results-toolbar">
                <div className="toolbar-title">
                    Query Results ({rowCount} {rowCount === 1 ? 'row' : 'rows'})
                </div>
                <div className="toolbar-actions">
                    <button className="toolbar-btn" onClick={handleCopy}>
                        📋 Copy
                    </button>
                    <button className="toolbar-btn" onClick={() => exportToCSV(data)}>
                        ⬇️ CSV
                    </button>
                    <button className="toolbar-btn" onClick={() => exportToJSON(data)}>
                        📄 JSON
                    </button>
                </div>
            </div>
            <div className="data-table-wrapper">
                <table className="data-table">
                    <thead>
                        <tr>
                            {headers.map((header, index) => (
                                <th key={index}>{header}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {headers.map((header, colIndex) => (
                                    <td key={colIndex}>{row[header]}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// ============================================
// Chart Type Detection Logic
// ============================================

/**
 * Detect the best chart type based on data structure
 */
function detectChartType(data) {
    if (!data || !data.rows || data.rows.length === 0) return 'bar';
    
    const { headers, rows } = data;
    
    // Count numeric vs text columns
    let numericCols = 0;
    let textCols = 0;
    
    headers.forEach(header => {
        const firstValue = rows[0][header];
        if (!isNaN(parseFloat(firstValue)) && isFinite(firstValue)) {
            numericCols++;
        } else {
            textCols++;
        }
    });
    
    // Check for time-series data (dates in first column)
    const firstColValue = rows[0][headers[0]];
    const hasDateColumn = headers.some(h => 
        h.toLowerCase().includes('date') || 
        h.toLowerCase().includes('time') ||
        h.toLowerCase().includes('month') ||
        h.toLowerCase().includes('year')
    );
    
    // Detection logic
    if (hasDateColumn && numericCols > 0) {
        return 'line'; // Time series → Line chart
    } else if (rows.length <= 10 && numericCols === 1 && textCols === 1) {
        return 'pie'; // Few categories with one value → Pie chart
    } else if (numericCols >= 1 && textCols >= 1) {
        return 'bar'; // Categories with values → Bar chart
    } else {
        return 'bar'; // Default to bar chart
    }
}

/**
 * Prepare chart data from table data
 */
function prepareChartData(data, chartType) {
    if (!data || !data.rows || data.rows.length === 0) return null;
    
    const { headers, rows } = data;
    
    // Find label column (first text column)
    let labelCol = headers[0];
    for (let header of headers) {
        const firstValue = rows[0][header];
        if (isNaN(parseFloat(firstValue)) || !isFinite(firstValue)) {
            labelCol = header;
            break;
        }
    }
    
    // Find value columns (numeric columns)
    const valueColumns = headers.filter(header => {
        if (header === labelCol) return false;
        const firstValue = rows[0][header];
        return !isNaN(parseFloat(firstValue)) && isFinite(firstValue);
    });
    
    // Extract labels
    const labels = rows.map(row => row[labelCol] || '');
    
    // Material Design Purple Palette
    const colors = [
        'rgba(91, 95, 199, 0.8)',   // Primary purple
        'rgba(139, 143, 232, 0.8)', // Light purple
        'rgba(26, 115, 232, 0.8)',  // Blue
        'rgba(30, 142, 62, 0.8)',   // Green
        'rgba(249, 171, 0, 0.8)',   // Yellow
        'rgba(217, 48, 37, 0.8)',   // Red
        'rgba(147, 52, 233, 0.8)',  // Deep purple
    ];
    
    // Prepare datasets
    const datasets = valueColumns.map((col, index) => ({
        label: col,
        data: rows.map(row => parseFloat(row[col]) || 0),
        backgroundColor: chartType === 'pie' || chartType === 'doughnut' 
            ? colors 
            : colors[index % colors.length],
        borderColor: chartType === 'pie' || chartType === 'doughnut'
            ? colors.map(c => c.replace('0.8', '1'))
            : colors[index % colors.length].replace('0.8', '1'),
        borderWidth: 2,
        tension: 0.4, // Smooth lines for line charts
    }));
    
    return { labels, datasets };
}

// ============================================
// Chart View Component
// ============================================

function ChartView({ data }) {
    const [chartType, setChartType] = useState(() => detectChartType(data));
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);
    
    useEffect(() => {
        if (!data || !data.rows || data.rows.length === 0) return;
        
        const ctx = chartRef.current;
        if (!ctx) return;
        
        // Destroy previous chart instance
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }
        
        // Prepare data
        const chartData = prepareChartData(data, chartType);
        if (!chartData) return;
        
        // Chart configuration
        const config = {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                                size: 12,
                                weight: 500,
                            },
                            color: '#374151',
                            padding: 15,
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleFont: {
                            size: 13,
                            weight: 600,
                        },
                        bodyFont: {
                            size: 12,
                        },
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: true,
                    }
                },
                scales: chartType === 'pie' || chartType === 'doughnut' ? {} : {
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            font: {
                                size: 11,
                            },
                            color: '#6B7280',
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(229, 231, 235, 0.8)',
                        },
                        ticks: {
                            font: {
                                size: 11,
                            },
                            color: '#6B7280',
                        }
                    }
                }
            }
        };
        
        // Create new chart
        chartInstanceRef.current = new Chart(ctx, config);
        
        return () => {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
        };
    }, [data, chartType]);
    
    const handleExportChart = () => {
        if (chartInstanceRef.current) {
            const url = chartInstanceRef.current.toBase64Image();
            const a = document.createElement('a');
            a.href = url;
            a.download = `chart_${new Date().getTime()}.png`;
            a.click();
        }
    };
    
    if (!data || !data.rows || data.rows.length === 0) {
        return (
            <div className="chart-container">
                <div className="chart-placeholder">
                    <div className="chart-placeholder-icon">📊</div>
                    <h3>No Data to Visualize</h3>
                    <p>Run a query to see chart visualizations</p>
                </div>
            </div>
        );
    }
    
    return (
        <div className="chart-container">
            <div className="chart-toolbar">
                <div className="chart-toolbar-left">
                    <span className="chart-toolbar-title">📊 Chart Visualization</span>
                    <span className="chart-toolbar-subtitle">
                        {data.rows.length} data {data.rows.length === 1 ? 'point' : 'points'}
                    </span>
                </div>
                <div className="chart-toolbar-right">
                    <select 
                        className="chart-type-selector"
                        value={chartType}
                        onChange={(e) => setChartType(e.target.value)}
                    >
                        <option value="bar">📊 Bar Chart</option>
                        <option value="line">📈 Line Chart</option>
                        <option value="pie">🥧 Pie Chart</option>
                        <option value="doughnut">🍩 Doughnut Chart</option>
                    </select>
                    <button className="toolbar-btn" onClick={handleExportChart}>
                        📥 Export PNG
                    </button>
                </div>
            </div>
            <div className="chart-canvas-wrapper">
                <canvas ref={chartRef}></canvas>
            </div>
        </div>
    );
}

// ============================================
// SQL Query View Component
// ============================================

function SQLQueryView({ query }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        const success = await copyToClipboard(query || 'No query available');
        if (success) {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="sql-viewer">
            <div className="sql-viewer-header">
                <div className="sql-viewer-title">
                    <span>💻</span>
                    <span>Generated SQL Query</span>
                </div>
                <button className="copy-sql-btn" onClick={handleCopy}>
                    {copied ? '✓ Copied!' : '📋 Copy SQL'}
                </button>
            </div>
            <pre className="sql-code">
                {query || 'No SQL query available'}
            </pre>
        </div>
    );
}

// ============================================
// Results Pane Component
// ============================================

function ResultsPane({ activeTab, queryResults, sqlQuery, onExampleClick }) {
    switch(activeTab) {
        case 'overview':
            if (!queryResults) {
                return <OverviewEmptyState onExampleClick={onExampleClick} />;
            }
            // If we have results, still show overview for now
            return <OverviewEmptyState onExampleClick={onExampleClick} />;
            
        case 'table':
            return <DataTableView data={queryResults} />;
            
        case 'chart':
            return <ChartView data={queryResults} />;
            
        case 'sql':
            return <SQLQueryView query={sqlQuery} />;
            
        case 'metadata':
            return <TableMetadataView />;
            
        default:
            return <OverviewEmptyState onExampleClick={onExampleClick} />;
    }
}

// ============================================
// Main Chat Application
// ============================================

function ChatApp() {
    const [messages, setMessages] = useState([
        { 
            author: 'customer_segmentation_analyst', 
            content: "Hello! I'm the Customer Segmentation Explorer. How can I help you analyze your BigQuery data today?" 
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [status, setStatus] = useState('Connected');
    const [activeTab, setActiveTab] = useState('overview');
    const [queryResults, setQueryResults] = useState(null);
    const [sqlQuery, setSqlQuery] = useState(null);
    const [showResults, setShowResults] = useState(false);
    
    const ws = useRef(null);
    const messageListRef = useRef(null);

    // Establish WebSocket connection
    useEffect(() => {
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

            // Display content from responses
            if (data.content && (data.type === 'FinalResponseEvent' || data.type === 'ToolOutputEvent' || data.type === 'Event')) {
                const author = data.author === '_sub_agent_tool' ? 'bigquery_expert' : data.author;
                setMessages(prevMessages => [...prevMessages, { author: author, content: data.content }]);
                
                // Try to parse table data from the response
                if (data.content.includes('|') && data.content.split('\n').filter(line => line.includes('|')).length > 2) {
                    const parsedData = parseTableData(data.content);
                    if (parsedData) {
                        setQueryResults(parsedData);
                        setShowResults(true);
                        setActiveTab('table');
                    }
                }
                
                // Extract SQL query if present
                const sqlMatch = data.content.match(/```sql\n([\s\S]*?)```/);
                if (sqlMatch) {
                    setSqlQuery(sqlMatch[1].trim());
                }
                
                setStatus('Connected');
            } else if (data.type !== 'FinalResponseEvent') {
                // Show that the agent is "thinking"
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

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    // Auto-scroll to latest message
    useEffect(() => {
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

    const handleExampleClick = (example) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const userMessage = { author: 'user', content: example };
            setMessages(prevMessages => [...prevMessages, userMessage]);
            ws.current.send(example);
            setInputValue('');
            setStatus('Waiting for response...');
        }
    };

    const isConnected = status === 'Connected' || status === 'Idle';

    return (
        <div className="chat-container">
            {/* Header */}
            <div className="chat-header">
                <div className="header-left">
                    <h1>Customer Segmentation Explorer</h1>
                    <span className="dataset-badge">cdp_data</span>
                    <span className="status-dot" style={{ 
                        background: isConnected ? 'var(--accent-success)' : 'var(--accent-error)' 
                    }}></span>
                    <span className="status-text">{status}</span>
                </div>
            </div>

            {/* Left Pane - Chat */}
            <div className="chat-pane">
                <div className="message-list" ref={messageListRef}>
                    {messages.map((msg, index) => (
                        <ChatMessage key={index} message={msg} />
                    ))}
                </div>
                <form className="message-input-form" onSubmit={handleSendMessage}>
                    <input
                        type="text"
                        className="form-control"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask about datasets, tables, or start segmentation..."
                        disabled={!isConnected}
                    />
                    <button 
                        type="submit" 
                        className="btn btn-primary" 
                        disabled={!isConnected}
                    >
                        Send
                    </button>
                </form>
            </div>

            {/* Right Pane - Results */}
            <div className="results-pane">
                <TabNavigation 
                    activeTab={activeTab} 
                    onTabChange={setActiveTab}
                    hasResults={showResults}
                />
                <div className="results-content">
                    <ResultsPane 
                        activeTab={activeTab} 
                        queryResults={queryResults}
                        sqlQuery={sqlQuery}
                        onExampleClick={handleExampleClick}
                    />
                </div>
            </div>
        </div>
    );
}

// ============================================
// Render Application
// ============================================

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ChatApp />);
