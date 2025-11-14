# Gemini Model Instructions for the Customer Segmentation Agent

This document provides instructions for a Gemini model to understand and interact with the Customer Segmentation Agent application, which is built using the Google Agent Development Kit (ADK).

## 1. Application Overview

The application is a multi-agent system designed to perform customer segmentation analysis using data stored in Google BigQuery. The primary goal is to analyze customer transaction data to identify distinct customer segments based on their Recency, Frequency, and Monetary (RFM) scores.

## 2. Multi-Agent Architecture

The system is composed of two specialized agents working in a hierarchical structure:

*   **`customer_segmentation_analyst` (Main Agent)**: This is the orchestrator agent. It manages the overall workflow, from initial data exploration to the final segmentation analysis and reporting. It delegates all database-related tasks to its sub-agent.

*   **`bigquery_expert` (Sub-Agent)**: This agent is a specialist in interacting with Google BigQuery. It is equipped with a set of tools to perform tasks such as listing datasets, viewing table schemas, and executing SQL queries. It acts on the instructions of the main agent to fetch the necessary data.

## 3. Agent Workflow

The `customer_segmentation_analyst` follows a predefined plan to achieve its goal:

1.  **Explore Data**: It begins by instructing the `bigquery_expert` to list available datasets and tables to locate the customer transaction data.
2.  **Understand Schema**: Once the `customer_transactions` table is identified, it requests the table's schema to understand its structure (e.g., column names and data types).
3.  **Formulate RFM Query**: Based on the schema, it constructs a BigQuery SQL query to calculate the RFM scores for each customer.
    *   **Recency**: Days since the last transaction.
    *   **Frequency**: Total number of transactions.
    *   **Monetary**: Total value of all transactions.
4.  **Execute Query**: It passes the SQL query to the `bigquery_expert` for execution.
5.  **Analyze Results**: After receiving the query results, it analyzes the RFM scores to classify customers into segments (e.g., "High-Value," "At-Risk," "New Customers").
6.  **Report Findings**: Finally, it generates a summary of the customer segments, presenting the results of the analysis.

## 4. BigQuery Tools

The `bigquery_expert` agent is equipped with the following tools defined in `bigquery_tools.py`:

*   `list_datasets()`: Lists all datasets in the configured BigQuery project.
*   `list_tables(dataset_id: str)`: Lists all tables within a specified dataset.
*   `get_table_schema(dataset_id: str, table_id: str)`: Returns the schema for a specified table.
*   `run_query(query: str)`: Executes a SQL query in BigQuery and returns the results as a string-formatted table.

## 5. Setup and Execution Guide

To run this agent, follow these steps:

1.  **Authentication**: Ensure you have authenticated with the Google Cloud CLI.
    ```bash
    gcloud auth application-default login
    ```
2.  **Environment Configuration**:
    *   Create a `.env` file in the root directory.
    *   Add your Google Cloud Project ID to the file:
        ```
        BIGQUERY_PROJECT=your-gcp-project-id
        ```
3.  **BigQuery Data Setup**:
    *   In your BigQuery project, create a new dataset (e.g., `customer_data`).
    *   Open the `sample_data.sql` file.
    *   Replace the placeholder `your_dataset` with the name of the dataset you just created.
    *   Run the SQL script in the BigQuery console to create and populate the `customer_transactions` table.
4.  **Run the Application**:
    *   Execute the main script from your terminal:
        ```bash
        python main.py
        ```

The agent will then start the segmentation process, and you will see its progress and final report in the console.
