import pandas as pd
import plotly.express as px
from src.models.query import DataQuerySchema
from src.models.visualization import VisualizationSchema

def _apply_filters(df: pd.DataFrame, filters: list) -> pd.DataFrame:
    if not filters:
        return df
        
    temp_df = df.copy()
    for f in filters:
        col = f.column
        val = f.value
        op = f.operator
        
        if col not in temp_df.columns:
            continue
            
        if temp_df[col].dtype in ['int64', 'float64']:
            try:
                val = float(val)
            except ValueError:
                pass
        
        if op == "==":
            temp_df = temp_df[temp_df[col] == val]
        elif op == "!=":
            temp_df = temp_df[temp_df[col] != val]
        elif op == ">":
            temp_df = temp_df[temp_df[col] > val]
        elif op == "<":
            temp_df = temp_df[temp_df[col] < val]
        elif op == ">=":
            temp_df = temp_df[temp_df[col] >= val]
        elif op == "<=":
            temp_df = temp_df[temp_df[col] <= val]
        elif op == "in":
            temp_df = temp_df[temp_df[col].astype(str).str.contains(str(val), case=False, na=False)]
            
    return temp_df

def _apply_aggregation(df: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    if not schema.metrics:
        return df
        
    valid_metrics = [m for m in schema.metrics if m in df.columns]
    if not valid_metrics:
        return df
        
    if schema.aggregation == "none":
        cols = valid_metrics.copy()
        if schema.group_by:
            cols += [g for g in schema.group_by if g in df.columns and g not in cols]
        return df[cols]
        
    if schema.group_by:
        valid_groups = [g for g in schema.group_by if g in df.columns]
        if valid_groups:
            return df.groupby(valid_groups)[valid_metrics].agg(schema.aggregation).reset_index()
            
    return df[valid_metrics].agg(schema.aggregation).to_frame().T

def _apply_sort_and_limit(df: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    temp_df = df.copy()
    
    if schema.sort and schema.sort.column in temp_df.columns:
        temp_df = temp_df.sort_values(by=schema.sort.column, ascending=schema.sort.ascending)
        
    if schema.limit:
        temp_df = temp_df.head(schema.limit)
        
    return temp_df

def execute_query(df: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    temp_df = _apply_filters(df, schema.filters)
    temp_df = _apply_aggregation(temp_df, schema)
    temp_df = _apply_sort_and_limit(temp_df, schema)
    return temp_df

def render_visualization(df_result: pd.DataFrame, schema: VisualizationSchema):
    if schema.x_axis not in df_result.columns or schema.y_axis not in df_result.columns:
        return None
        
    color_col = schema.color if schema.color in df_result.columns else None
    fig = None
    
    chart_builders = {
        "bar": px.bar,
        "line": px.line,
        "scatter": px.scatter,
        "histogram": px.histogram,
        "box": px.box
    }

    try:
        if schema.chart_type == "pie":
            fig = px.pie(df_result, names=schema.x_axis, values=schema.y_axis, title=schema.title)
        elif schema.chart_type in chart_builders:
            builder = chart_builders[schema.chart_type]
            fig = builder(df_result, x=schema.x_axis, y=schema.y_axis, color=color_col, title=schema.title)

        if fig:
            fig.update_layout(
                xaxis_title=schema.x_axis_title or schema.x_axis,
                yaxis_title=schema.y_axis_title or schema.y_axis
            )
    except Exception as e:
        print(f"Error rendering chart: {str(e)}")
        
    return fig
