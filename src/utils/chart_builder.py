import pandas as pd
import plotly.express as px
from src.models.visualization import VisualizationSchema

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
