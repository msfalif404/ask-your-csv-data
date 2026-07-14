import pandas as pd
import operator
from src.models.query import DataQuerySchema

OPERATOR_MAP = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le
}

def _safe_convert_numeric(value, column_dtype):
    if column_dtype in ['int64', 'float64']:
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
    return value

def _apply_filters(dataframe: pd.DataFrame, filters: list) -> pd.DataFrame:
    if not filters:
        return dataframe
        
    filtered_df = dataframe.copy()
    for filter_condition in filters:
        col = filter_condition.column
        if col not in filtered_df.columns:
            continue
            
        val = _safe_convert_numeric(filter_condition.value, filtered_df[col].dtype)
        op = filter_condition.operator
        
        if op in OPERATOR_MAP:
            filtered_df = filtered_df[OPERATOR_MAP[op](filtered_df[col], val)]
        elif op == "in":
            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(val), case=False, na=False)]
            
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
            selected_columns += [g for g in schema.group_by if g in dataframe.columns and g not in selected_columns]
        return dataframe[selected_columns]
        
    if schema.group_by:
        valid_groups = [g for g in schema.group_by if g in dataframe.columns]
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
    return _apply_sort_and_limit(processed_df, schema)
