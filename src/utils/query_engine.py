import pandas as pd
import plotly.express as px
import operator
from src.models.query import DataQuerySchema
from src.models.visualization import VisualizationSchema

OPERATOR_MAP = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le
}

def _apply_filters(dataframe: pd.DataFrame, filters: list) -> pd.DataFrame:
    if not filters:
        return dataframe
        
    filtered_df = dataframe.copy()
    for filter_condition in filters:
        column_name = filter_condition.column
        filter_value = filter_condition.value
        operator_type = filter_condition.operator
        
        if column_name not in filtered_df.columns:
            continue
            
        if filtered_df[column_name].dtype in ['int64', 'float64']:
            try:
                filter_value = float(filter_value)
            except ValueError:
                pass
        
        if operator_type in OPERATOR_MAP:
            op_func = OPERATOR_MAP[operator_type]
            filtered_df = filtered_df[op_func(filtered_df[column_name], filter_value)]
        elif operator_type == "in":
            filtered_df = filtered_df[filtered_df[column_name].astype(str).str.contains(str(filter_value), case=False, na=False)]
            
    return filtered_df

def _apply_aggregation(dataframe: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    if not schema.metrics:
        return dataframe
        
    valid_metrics = [metric for metric in schema.metrics if metric in dataframe.columns]
    if not valid_metrics:
        return dataframe
        
    if schema.aggregation == "none":
        selected_columns = valid_metrics.copy()
        if schema.group_by:
            selected_columns += [group for group in schema.group_by if group in dataframe.columns and group not in selected_columns]
        return dataframe[selected_columns]
        
    if schema.group_by:
        valid_groups = [group for group in schema.group_by if group in dataframe.columns]
        if valid_groups:
            return dataframe.groupby(valid_groups)[valid_metrics].agg(schema.aggregation).reset_index()
            
    return dataframe[valid_metrics].agg(schema.aggregation).to_frame().T

def _apply_sort_and_limit(dataframe: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    sorted_df = dataframe.copy()
    
    if schema.sort and schema.sort.column in sorted_df.columns:
        sorted_df = sorted_df.sort_values(by=schema.sort.column, ascending=schema.sort.ascending)
        
    if schema.limit:
        sorted_df = sorted_df.head(schema.limit)
        
    return sorted_df

def execute_query(dataframe: pd.DataFrame, schema: DataQuerySchema) -> pd.DataFrame:
    processed_df = _apply_filters(dataframe, schema.filters)
    processed_df = _apply_aggregation(processed_df, schema)
    processed_df = _apply_sort_and_limit(processed_df, schema)
    return processed_df

def _build_plotly_figure(dataframe: pd.DataFrame, schema: VisualizationSchema):
    color_column = schema.color if schema.color in dataframe.columns else None
    
    chart_builders = {
        "bar": px.bar,
        "line": px.line,
        "scatter": px.scatter,
        "histogram": px.histogram,
        "box": px.box
    }

    if schema.chart_type == "pie":
        return px.pie(dataframe, names=schema.x_axis, values=schema.y_axis, title=schema.title)
        
    if schema.chart_type in chart_builders:
        builder = chart_builders[schema.chart_type]
        return builder(dataframe, x=schema.x_axis, y=schema.y_axis, color=color_column, title=schema.title)
        
    return None

def render_visualization(dataframe: pd.DataFrame, schema: VisualizationSchema):
    if schema.x_axis not in dataframe.columns or schema.y_axis not in dataframe.columns:
        return None
        
    try:
        figure = _build_plotly_figure(dataframe, schema)
        if figure:
            figure.update_layout(
                xaxis_title=schema.x_axis_title or schema.x_axis,
                yaxis_title=schema.y_axis_title or schema.y_axis
            )
        return figure
    except Exception as error:
        print(f"Error rendering chart: {str(error)}")
        return None
