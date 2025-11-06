"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useState } from "react";

export default function CDPAnalyticsPage() {
  const [themeColor] = useState("#000000"); // Black theme for enterprise

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <MainContent themeColor={themeColor} />
      <CopilotSidebar
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "CDP Analytics Assistant",
          initial: "**Welcome to your CDP Analytics Assistant!**\n\nHello, I can help you analyze your customer data. What can I do for you today?"
        }}
      />
    </main>
  );
}

// State of the agent - aligns with the backend agent's shared state
type AgentState = {
  query_results?: {
    type: string;
    query: string;
    rows: any[];
    metadata: any;
    timestamp?: string;
  };
}

function MainContent({ themeColor }: { themeColor: string }) {
  // 🪁 Shared State: Sync with the agent's query results
  const { state } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      query_results: undefined,
    },
  });

  const hasResults = state.query_results && state.query_results.rows && state.query_results.rows.length > 0;

  return (
    <div className="h-screen w-screen bg-white">
      <div className="h-full pl-12 pr-6 py-8 md:pl-16 md:pr-8 md:py-10 lg:pl-20 lg:pr-10 lg:py-12 overflow-auto">
        {/* Header */}
        <div className="mb-10 md:mb-12 pb-6 border-b border-gray-200">
          <h1 className="text-3xl md:text-4xl font-light text-black mb-2 tracking-tight">
            CDP Analytics Dashboard
          </h1>
          <p className="text-sm md:text-base text-gray-600 font-light">
            Your AI-powered customer data platform analytics workspace
          </p>
        </div>

        {/* Results Display */}
        {hasResults ? (
          <ResultsDisplay 
            results={state.query_results} 
            themeColor={themeColor}
          />
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="max-w-4xl">
      {/* Main Card */}
      <div className="border border-gray-200 p-8 md:p-12">
        <div className="max-w-2xl">
          {/* Title */}
          <h2 className="text-2xl md:text-3xl font-light text-black mb-4">
            Ready to Analyze Your Data
          </h2>
          
          {/* Subtitle */}
          <p className="text-base text-gray-600 mb-10 leading-relaxed font-light">
            Use the chat assistant on the right to query your customer data, 
            analyze segments, and discover insights in natural language.
          </p>

          {/* Example Queries */}
          <div className="border-l-2 border-black pl-6">
            <p className="font-medium text-black text-sm uppercase tracking-wide mb-4">Example Queries</p>
            <div className="space-y-3">
              <div className="text-sm text-gray-700 font-light">
                "Show me all customers"
              </div>
              <div className="text-sm text-gray-700 font-light">
                "What are our customer segments?"
              </div>
              <div className="text-sm text-gray-700 font-light">
                "Show revenue trends for the last 7 days"
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="border border-gray-200 p-6">
          <h3 className="font-medium text-black mb-2 text-sm uppercase tracking-wide">Customer Queries</h3>
          <p className="text-sm text-gray-600 font-light">Query and filter customer data with natural language</p>
        </div>
        <div className="border border-gray-200 p-6">
          <h3 className="font-medium text-black mb-2 text-sm uppercase tracking-wide">Analytics</h3>
          <p className="text-sm text-gray-600 font-light">Analyze segments and discover revenue trends</p>
        </div>
        <div className="border border-gray-200 p-6">
          <h3 className="font-medium text-black mb-2 text-sm uppercase tracking-wide">AI Insights</h3>
          <p className="text-sm text-gray-600 font-light">Get intelligent recommendations and insights</p>
        </div>
      </div>
    </div>
  );
}

function ResultsDisplay({ results, themeColor }: { 
  results: AgentState['query_results'], 
  themeColor: string 
}) {
  if (!results) return null;

  const { type, rows, metadata, query } = results;

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Metadata Header */}
      <div className="border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
          <div>
            <h2 className="text-2xl font-light text-black capitalize">
              {type?.replace(/_/g, ' ') || 'Query Results'}
            </h2>
            <p className="text-sm text-gray-600 mt-1 font-light">
              {rows.length} {rows.length === 1 ? 'row' : 'rows'} returned
            </p>
          </div>
          {metadata?.total_bytes_processed && (
            <div className="border border-gray-200 px-4 py-2">
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Data Processed</p>
              <p className="text-base font-light text-black">
                {formatBytes(metadata.total_bytes_processed)}
              </p>
            </div>
          )}
        </div>
        
        {query && (
          <details className="mt-4 group">
            <summary className="cursor-pointer text-sm text-black hover:text-gray-700 font-medium flex items-center gap-2 select-none uppercase tracking-wide">
              <span className="group-open:rotate-90 transition-transform">▶</span>
              View SQL Query
            </summary>
            <pre className="mt-3 p-4 bg-gray-50 text-xs overflow-x-auto border border-gray-200">
              <code className="text-gray-700 font-mono">{query}</code>
            </pre>
          </details>
        )}
      </div>

      {/* Data Table */}
      <div className="border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          {type === 'customers' && <CustomersTable rows={rows} />}
          {type === 'segments' && <SegmentsTable rows={rows} />}
          {type === 'revenue_trends' && <RevenueTrendsTable rows={rows} />}
          {!['customers', 'segments', 'revenue_trends'].includes(type || '') && (
            <GenericTable rows={rows} />
          )}
        </div>
      </div>
    </div>
  );
}

function CustomersTable({ rows }: { rows: any[] }) {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Customer ID
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Email
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Revenue
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Purchases
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Segment
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Last Purchase
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {rows.map((row, idx) => (
          <tr key={idx} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-light text-black">
              {row.customer_id}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-light">
              {row.email}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black font-light">
              ${formatNumber(row.total_revenue)}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black font-light">
              {row.purchase_count}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 inline-flex text-xs leading-5 font-medium border border-black text-black">
                {row.segment || 'N/A'}
              </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-light">
              {formatDate(row.last_purchase_date)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function SegmentsTable({ rows }: { rows: any[] }) {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Segment
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Customers
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Avg Revenue
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Total Revenue
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Avg Purchases
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {rows.map((row, idx) => (
          <tr key={idx} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">
              {row.segment}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
              {formatNumber(row.customer_count)}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
              ${formatNumber(row.avg_revenue)}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
              ${formatNumber(row.total_revenue)}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
              {formatNumber(row.avg_purchases, 1)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function RevenueTrendsTable({ rows }: { rows: any[] }) {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Date
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Daily Revenue
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Unique Customers
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Total Purchases
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
            Avg per Customer
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {rows.map((row, idx) => {
          const avgPerCustomer = row.unique_customers > 0 
            ? row.daily_revenue / row.unique_customers 
            : 0;
          
          return (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">
                {formatDate(row.date)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                ${formatNumber(row.daily_revenue)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                {formatNumber(row.unique_customers)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                {formatNumber(row.total_purchases)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                ${formatNumber(avgPerCustomer)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function GenericTable({ rows }: { rows: any[] }) {
  if (rows.length === 0) return <div className="p-8 text-center text-gray-600">No data to display</div>;
  
  const columns = Object.keys(rows[0]);
  
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          {columns.map((col) => (
            <th
              key={col}
              className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
            >
              {col.replace(/_/g, ' ')}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {rows.map((row, idx) => (
          <tr key={idx} className="hover:bg-gray-50">
            {columns.map((col) => (
              <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-black">
                {formatValue(row[col])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Utility functions
function formatNumber(value: any, decimals: number = 2): string {
  const num = parseFloat(value);
  if (isNaN(num)) return value;
  return num.toLocaleString('en-US', { 
    minimumFractionDigits: decimals, 
    maximumFractionDigits: decimals 
  });
}

function formatDate(value: any): string {
  if (!value) return 'N/A';
  try {
    const date = new Date(value);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  } catch {
    return String(value);
  }
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function formatValue(value: any): string {
  if (value === null || value === undefined) return 'N/A';
  if (typeof value === 'number') return formatNumber(value);
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
}
