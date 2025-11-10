"""
Analytics Tools - Multi-source data integration, analysis, and visualization

This module provides comprehensive analytics capabilities:
- Database connections (PostgreSQL, MySQL, MongoDB, SQLite, Redis)
- API data fetching (REST, GraphQL)
- Data transformation and ETL
- Statistical analysis and predictive modeling
- Interactive chart creation (Plotly, D3.js)
- Dashboard generation (HTML, React)
- Report generation (PDF, Excel, HTML)

Author: Analytics Agent
Team: ENGINEERING_TEAM
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class AnalyticsTools:
    """
    Comprehensive analytics toolkit for multi-source data analysis
    """

    def __init__(self):
        self.connections = {}
        self.data_cache = {}

    # ==================== DATABASE CONNECTIONS ====================

    def connect_database(
        self,
        db_type: str,
        host: str = "localhost",
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Connect to various database types

        Args:
            db_type: Database type (postgresql, mysql, mongodb, sqlite, redis)
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            **kwargs: Additional connection parameters

        Returns:
            Database connection object
        """
        if db_type == "postgresql":
            try:
                import psycopg2
                port = port or 5432
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    **kwargs
                )
                self.connections[f"{db_type}_{database}"] = conn
                return conn
            except ImportError:
                return {"error": "psycopg2 not installed. Install: pip install psycopg2-binary"}

        elif db_type == "mysql":
            try:
                import mysql.connector
                port = port or 3306
                conn = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    **kwargs
                )
                self.connections[f"{db_type}_{database}"] = conn
                return conn
            except ImportError:
                return {"error": "mysql-connector-python not installed. Install: pip install mysql-connector-python"}

        elif db_type == "mongodb":
            try:
                from pymongo import MongoClient
                port = port or 27017
                client = MongoClient(host=host, port=port, username=username, password=password, **kwargs)
                db = client[database] if database else client
                self.connections[f"{db_type}_{database}"] = db
                return db
            except ImportError:
                return {"error": "pymongo not installed. Install: pip install pymongo"}

        elif db_type == "sqlite":
            try:
                import sqlite3
                conn = sqlite3.connect(database)  # database is file path for SQLite
                self.connections[f"{db_type}_{database}"] = conn
                return conn
            except Exception as e:
                return {"error": f"SQLite connection failed: {str(e)}"}

        elif db_type == "redis":
            try:
                import redis
                port = port or 6379
                r = redis.Redis(host=host, port=port, password=password, decode_responses=True, **kwargs)
                self.connections[f"{db_type}_{host}"] = r
                return r
            except ImportError:
                return {"error": "redis not installed. Install: pip install redis"}

        else:
            return {"error": f"Unsupported database type: {db_type}. Supported: postgresql, mysql, mongodb, sqlite, redis"}

    def query_database(
        self,
        connection: Any,
        query: str,
        params: Optional[tuple] = None
    ) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame

        Args:
            connection: Database connection object
            query: SQL query string
            params: Query parameters (for parameterized queries)

        Returns:
            pandas DataFrame with query results
        """
        try:
            # Check connection type
            if hasattr(connection, 'cursor'):  # PostgreSQL, MySQL, SQLite
                df = pd.read_sql_query(query, connection, params=params)
                return df
            elif 'pymongo' in str(type(connection)):  # MongoDB
                # For MongoDB, query is JSON string
                query_dict = json.loads(query) if isinstance(query, str) else query
                collection_name = query_dict.get('collection')
                find_query = query_dict.get('query', {})
                projection = query_dict.get('projection')

                if collection_name:
                    collection = connection[collection_name]
                    results = list(collection.find(find_query, projection))
                    df = pd.DataFrame(results)
                    return df
                else:
                    return {"error": "MongoDB query requires 'collection' field"}
            else:
                return {"error": "Invalid connection type"}
        except Exception as e:
            return {"error": f"Query execution failed: {str(e)}"}

    # ==================== API DATA FETCHING ====================

    def fetch_api_data(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        graphql_query: Optional[str] = None
    ) -> Union[pd.DataFrame, Dict, List]:
        """
        Fetch data from REST or GraphQL APIs

        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: HTTP headers (authorization, content-type, etc.)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            graphql_query: GraphQL query string (for GraphQL APIs)

        Returns:
            API response as DataFrame, dict, or list
        """
        try:
            import requests

            # GraphQL request
            if graphql_query:
                response = requests.post(
                    url,
                    json={"query": graphql_query},
                    headers=headers or {}
                )
            else:
                # REST API request
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data
                )

            response.raise_for_status()
            data = response.json()

            # Convert to DataFrame if data is list of dicts
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                # GraphQL response or nested data
                inner_data = data['data']
                if isinstance(inner_data, dict):
                    # Extract first list from GraphQL response
                    for key, value in inner_data.items():
                        if isinstance(value, list):
                            return pd.DataFrame(value)
                return inner_data
            else:
                return data

        except ImportError:
            return {"error": "requests library not installed. Install: pip install requests"}
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

    # ==================== FILE DATA LOADING ====================

    def load_data_from_file(
        self,
        file_path: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from various file formats

        Args:
            file_path: Path to data file
            **kwargs: Additional parameters for file reading (sheet_name, sep, etc.)

        Returns:
            pandas DataFrame
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                return pd.read_csv(file_path, **kwargs)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, **kwargs)
            elif file_ext == '.json':
                return pd.read_json(file_path, **kwargs)
            elif file_ext == '.parquet':
                return pd.read_parquet(file_path, **kwargs)
            elif file_ext in ['.tsv', '.txt']:
                return pd.read_csv(file_path, sep='\t', **kwargs)
            elif file_ext == '.xml':
                return pd.read_xml(file_path, **kwargs)
            else:
                return {"error": f"Unsupported file format: {file_ext}"}
        except Exception as e:
            return {"error": f"Failed to load file: {str(e)}"}

    def fetch_google_sheet_data(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> pd.DataFrame:
        """
        Fetch data from Google Sheets (requires Google Workspace MCP)

        Args:
            spreadsheet_id: Google Sheets ID
            range_name: Range to read (e.g., "Sheet1!A1:Z1000")

        Returns:
            pandas DataFrame
        """
        # This will be called through MCP, so we document the pattern
        return {
            "instruction": "Use mcp__google-workspace__read_sheet_values",
            "params": {
                "spreadsheet_id": spreadsheet_id,
                "range": range_name
            }
        }

    # ==================== DATA TRANSFORMATION ====================

    def transform_data(
        self,
        data: Union[pd.DataFrame, List[pd.DataFrame]],
        operations: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Apply transformations to data

        Args:
            data: DataFrame or list of DataFrames
            operations: List of transformation operations

        Returns:
            Transformed DataFrame
        """
        # Merge multiple DataFrames if provided as list
        if isinstance(data, list):
            df = data[0]
            for i, other_df in enumerate(data[1:]):
                merge_op = next((op for op in operations if op.get('type') == 'merge'), None)
                if merge_op:
                    df = df.merge(
                        other_df,
                        on=merge_op.get('on'),
                        how=merge_op.get('how', 'inner')
                    )
        else:
            df = data.copy()

        for operation in operations:
            op_type = operation.get('type')

            if op_type == 'remove_nulls':
                columns = operation.get('columns')
                if columns:
                    df = df.dropna(subset=columns)
                else:
                    df = df.dropna()

            elif op_type == 'convert_types':
                type_map = operation.get('columns', {})
                for col, dtype in type_map.items():
                    if dtype == 'datetime':
                        df[col] = pd.to_datetime(df[col])
                    else:
                        df[col] = df[col].astype(dtype)

            elif op_type == 'deduplicate':
                subset = operation.get('subset')
                df = df.drop_duplicates(subset=subset)

            elif op_type == 'calculate_column':
                name = operation.get('name')
                formula = operation.get('formula')
                # Safe eval for simple formulas
                df[name] = df.eval(formula)

            elif op_type == 'filter':
                condition = operation.get('condition')
                df = df.query(condition)

            elif op_type == 'aggregate':
                group_by = operation.get('group_by')
                agg_dict = operation.get('agg', {})
                df = df.groupby(group_by).agg(agg_dict).reset_index()

            elif op_type == 'sort':
                by = operation.get('by')
                ascending = operation.get('ascending', True)
                df = df.sort_values(by=by, ascending=ascending)

            elif op_type == 'rename':
                columns = operation.get('columns', {})
                df = df.rename(columns=columns)

        return df

    # ==================== STATISTICAL ANALYSIS ====================

    def analyze_data(
        self,
        data: pd.DataFrame,
        analysis_type: str,
        target_column: Optional[str] = None,
        group_by: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform statistical analysis on data

        Args:
            data: DataFrame to analyze
            analysis_type: Type of analysis (descriptive, correlation, regression, time_series, cohort)
            target_column: Column to analyze
            group_by: Column to group by
            **kwargs: Additional parameters

        Returns:
            Analysis results dictionary
        """
        if analysis_type == "descriptive":
            if target_column:
                series = data[target_column]
                results = {
                    "column": target_column,
                    "count": int(len(series)),
                    "mean": float(series.mean()) if pd.api.types.is_numeric_dtype(series) else None,
                    "median": float(series.median()) if pd.api.types.is_numeric_dtype(series) else None,
                    "std_dev": float(series.std()) if pd.api.types.is_numeric_dtype(series) else None,
                    "min": float(series.min()) if pd.api.types.is_numeric_dtype(series) else None,
                    "max": float(series.max()) if pd.api.types.is_numeric_dtype(series) else None,
                    "percentiles": {
                        "25th": float(series.quantile(0.25)) if pd.api.types.is_numeric_dtype(series) else None,
                        "50th": float(series.quantile(0.50)) if pd.api.types.is_numeric_dtype(series) else None,
                        "75th": float(series.quantile(0.75)) if pd.api.types.is_numeric_dtype(series) else None,
                    }
                }

                if group_by:
                    grouped = data.groupby(group_by)[target_column]
                    results["by_group"] = {
                        str(name): {
                            "mean": float(group.mean()) if pd.api.types.is_numeric_dtype(group) else None,
                            "count": int(len(group))
                        }
                        for name, group in grouped
                    }

                return results
            else:
                return data.describe().to_dict()

        elif analysis_type == "correlation":
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            corr_matrix = data[numeric_cols].corr()
            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": self._find_strong_correlations(corr_matrix)
            }

        elif analysis_type == "time_series":
            if target_column and 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.sort_values('date')

                return {
                    "trend": self._calculate_trend(data['date'], data[target_column]),
                    "seasonality": self._detect_seasonality(data, target_column),
                    "statistics": {
                        "mean": float(data[target_column].mean()),
                        "std": float(data[target_column].std()),
                        "growth_rate": self._calculate_growth_rate(data[target_column])
                    }
                }

        return {"error": f"Analysis type '{analysis_type}' not fully implemented. Use descriptive, correlation, or time_series."}

    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """Find pairs with strong correlation"""
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > threshold:
                    strong_corrs.append({
                        "variable1": corr_matrix.columns[i],
                        "variable2": corr_matrix.columns[j],
                        "correlation": float(corr_value)
                    })
        return strong_corrs

    def _calculate_trend(self, dates: pd.Series, values: pd.Series) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    def _detect_seasonality(self, data: pd.DataFrame, column: str) -> str:
        """Detect seasonality pattern"""
        # Simple seasonality detection
        if 'date' in data.columns:
            data['month'] = pd.to_datetime(data['date']).dt.month
            monthly_std = data.groupby('month')[column].std().mean()
            overall_std = data[column].std()

            if monthly_std > overall_std * 0.5:
                return "seasonal_pattern_detected"
        return "no_clear_seasonality"

    def _calculate_growth_rate(self, series: pd.Series) -> float:
        """Calculate growth rate"""
        if len(series) < 2:
            return 0.0
        first_value = series.iloc[0]
        last_value = series.iloc[-1]
        if first_value == 0:
            return 0.0
        return float((last_value - first_value) / first_value)

    def analyze_ab_test(
        self,
        control_data: pd.DataFrame,
        treatment_data: pd.DataFrame,
        metric: str,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Analyze A/B test results with statistical significance

        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            metric: Metric column to compare
            confidence_level: Confidence level (default 0.95 for 95%)

        Returns:
            A/B test results with significance
        """
        try:
            from scipy import stats

            control_values = control_data[metric]
            treatment_values = treatment_data[metric]

            control_mean = control_values.mean()
            treatment_mean = treatment_values.mean()

            # Perform t-test
            t_stat, p_value = stats.ttest_ind(control_values, treatment_values)

            # Calculate lift
            lift = (treatment_mean - control_mean) / control_mean if control_mean != 0 else 0

            # Determine significance
            alpha = 1 - confidence_level
            is_significant = p_value < alpha

            # Confidence interval
            se = stats.sem(treatment_values - control_values)
            ci = stats.t.interval(confidence_level, len(treatment_values)-1, loc=treatment_mean-control_mean, scale=se)

            return {
                "control_mean": float(control_mean),
                "treatment_mean": float(treatment_mean),
                "lift": float(lift),
                "lift_percentage": float(lift * 100),
                "p_value": float(p_value),
                "significant": is_significant,
                "confidence_level": confidence_level,
                "confidence_interval": [float(ci[0]), float(ci[1])],
                "sample_size_control": len(control_values),
                "sample_size_treatment": len(treatment_values),
                "recommendation": f"Deploy {'treatment' if is_significant and lift > 0 else 'control'}"
            }
        except ImportError:
            return {"error": "scipy not installed. Install: pip install scipy"}
        except Exception as e:
            return {"error": f"A/B test analysis failed: {str(e)}"}

    # ==================== CHART CREATION ====================

    def create_chart(
        self,
        data: pd.DataFrame,
        chart_type: str,
        x: str,
        y: Optional[str] = None,
        color: Optional[str] = None,
        title: str = "",
        style: str = "plotly",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create interactive charts using Plotly or other libraries

        Args:
            data: DataFrame with chart data
            chart_type: Type of chart (line, bar, scatter, pie, histogram, box, heatmap, funnel)
            x: X-axis column
            y: Y-axis column
            color: Color grouping column
            title: Chart title
            style: Chart library (plotly, chartjs, d3js)
            **kwargs: Additional chart parameters

        Returns:
            Chart configuration dictionary or HTML string
        """
        try:
            if style == "plotly":
                import plotly.express as px
                import plotly.graph_objects as go

                # Create chart based on type
                if chart_type == "line":
                    fig = px.line(data, x=x, y=y, color=color, title=title, **kwargs)
                elif chart_type == "bar":
                    fig = px.bar(data, x=x, y=y, color=color, title=title, **kwargs)
                elif chart_type == "scatter":
                    fig = px.scatter(data, x=x, y=y, color=color, title=title, **kwargs)
                elif chart_type == "pie":
                    fig = px.pie(data, names=x, values=y, title=title, **kwargs)
                elif chart_type == "histogram":
                    fig = px.histogram(data, x=x, y=y, color=color, title=title, **kwargs)
                elif chart_type == "box":
                    fig = px.box(data, x=x, y=y, color=color, title=title, **kwargs)
                elif chart_type == "heatmap":
                    # Create correlation heatmap
                    numeric_data = data.select_dtypes(include=[np.number])
                    corr = numeric_data.corr()
                    fig = px.imshow(corr, text_auto=True, title=title or "Correlation Heatmap")
                elif chart_type == "funnel":
                    fig = go.Figure(go.Funnel(
                        y=data[x],
                        x=data[y],
                        textinfo="value+percent total"
                    ))
                    fig.update_layout(title=title)
                else:
                    return {"error": f"Unsupported chart type: {chart_type}"}

                # Return HTML
                html = fig.to_html(include_plotlyjs='cdn', full_html=True)
                return {
                    "type": "plotly",
                    "html": html,
                    "config": fig.to_dict()
                }

            else:
                return {"error": f"Chart style '{style}' not implemented. Use 'plotly'."}

        except ImportError:
            return {"error": "plotly not installed. Install: pip install plotly"}
        except Exception as e:
            return {"error": f"Chart creation failed: {str(e)}"}

    # ==================== DASHBOARD CREATION ====================

    def create_dashboard(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        layout: str = "grid",
        theme: str = "light",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create interactive dashboard with multiple visualizations

        Args:
            title: Dashboard title
            sections: List of dashboard sections (charts, tables, metrics)
            layout: Layout style (grid, tabbed, sidebar)
            theme: Theme (light, dark, custom)
            **kwargs: Additional dashboard parameters

        Returns:
            Dashboard HTML string
        """
        # Build HTML dashboard
        html_parts = [
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: {'#1a1a1a' if theme == 'dark' else '#f5f5f5'};
                        color: {'#ffffff' if theme == 'dark' else '#333333'};
                    }}
                    .dashboard-header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .dashboard-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                        gap: 20px;
                    }}
                    .section {{
                        background: {'#2a2a2a' if theme == 'dark' else '#ffffff'};
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .section-title {{
                        font-size: 18px;
                        font-weight: 600;
                        margin-bottom: 15px;
                    }}
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                    }}
                    .metric-card {{
                        background: {'#333' if theme == 'dark' else '#f9f9f9'};
                        padding: 15px;
                        border-radius: 6px;
                        text-align: center;
                    }}
                    .metric-value {{
                        font-size: 32px;
                        font-weight: 700;
                        margin: 10px 0;
                    }}
                    .metric-name {{
                        font-size: 14px;
                        color: {'#aaa' if theme == 'dark' else '#666'};
                    }}
                    .metric-change {{
                        font-size: 14px;
                        font-weight: 600;
                    }}
                    .metric-change.positive {{ color: #10b981; }}
                    .metric-change.negative {{ color: #ef4444; }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid {'#444' if theme == 'dark' else '#eee'};
                    }}
                    th {{
                        font-weight: 600;
                        background: {'#333' if theme == 'dark' else '#f9f9f9'};
                    }}
                </style>
            </head>
            <body>
                <div class="dashboard-header">
                    <h1>{title}</h1>
                    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="dashboard-grid">
            """
        ]

        # Add sections
        for section in sections:
            section_type = section.get('type')
            section_title = section.get('title', '')

            html_parts.append(f'<div class="section">')
            if section_title:
                html_parts.append(f'<h2 class="section-title">{section_title}</h2>')

            if section_type == "metrics_cards":
                metrics = section.get('metrics', [])
                html_parts.append('<div class="metrics-grid">')
                for metric in metrics:
                    change_class = "positive" if metric.get('change', '').startswith('+') else "negative"
                    html_parts.append(f"""
                        <div class="metric-card">
                            <div class="metric-name">{metric.get('name', '')}</div>
                            <div class="metric-value">{metric.get('value', '')}</div>
                            <div class="metric-change {change_class}">{metric.get('change', '')}</div>
                        </div>
                    """)
                html_parts.append('</div>')

            elif section_type == "chart":
                chart_data = section.get('chart', {})
                if isinstance(chart_data, dict) and 'html' in chart_data:
                    # Extract just the chart div, not full HTML
                    chart_html = chart_data['html']
                    # Find the plotly div
                    if '<div' in chart_html:
                        start = chart_html.find('<div')
                        end = chart_html.find('</div>', start) + 6
                        html_parts.append(chart_html[start:end])

                        # Extract script
                        script_start = chart_html.find('<script')
                        if script_start != -1:
                            script_end = chart_html.find('</script>', script_start) + 9
                            html_parts.append(chart_html[script_start:script_end])

            elif section_type == "table":
                table_data = section.get('data')
                if isinstance(table_data, pd.DataFrame):
                    html_parts.append(table_data.to_html(classes='data-table', index=False))

            html_parts.append('</div>')

        html_parts.append("""
                </div>
            </body>
            </html>
        """)

        html_content = '\n'.join(html_parts)

        return {
            "type": "dashboard",
            "html": html_content,
            "title": title,
            "sections_count": len(sections)
        }

    # ==================== HELPER METHODS ====================

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load config: {str(e)}"}

    def save_to_file(self, content: str, file_path: str) -> Dict[str, str]:
        """Save content to file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            return {"success": True, "file_path": file_path}
        except Exception as e:
            return {"error": f"Failed to save file: {str(e)}"}


# ==================== MODULE-LEVEL FUNCTIONS ====================

# Create global instance
_analytics = AnalyticsTools()

# Export functions
connect_database = _analytics.connect_database
query_database = _analytics.query_database
fetch_api_data = _analytics.fetch_api_data
load_data_from_file = _analytics.load_data_from_file
fetch_google_sheet_data = _analytics.fetch_google_sheet_data
transform_data = _analytics.transform_data
analyze_data = _analytics.analyze_data
analyze_ab_test = _analytics.analyze_ab_test
create_chart = _analytics.create_chart
create_dashboard = _analytics.create_dashboard
load_config = _analytics.load_config


if __name__ == "__main__":
    # Example usage
    print("Analytics Tools Module Loaded")
    print("\nAvailable functions:")
    print("- connect_database()")
    print("- query_database()")
    print("- fetch_api_data()")
    print("- load_data_from_file()")
    print("- transform_data()")
    print("- analyze_data()")
    print("- analyze_ab_test()")
    print("- create_chart()")
    print("- create_dashboard()")
