import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import io

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("RF Data Dashboard (Dynamic Radar Chart)",
                        className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Textarea(
                id='data-input',
                placeholder="Paste your tab-separated data here...",
                style={
                    'width': '100%',
                    'height': '200px',
                    'border': '1px solid #ccc',
                    'padding': '10px',
                    'borderRadius': '5px',
                    'fontSize': '16px'
                }
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Generate Radar Chart", id="generate-chart-btn",
                       color="primary", className="mt-3"),
        ], width=12, className="text-center")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='chart-output')
        ], width=12)
    ])
])

# Callback to generate radar chart
@app.callback(
    Output('chart-output', 'figure'),
    Input('generate-chart-btn', 'n_clicks'),
    State('data-input', 'value')
)
def update_chart(n_clicks, data):
    if n_clicks and data:
        try:
            # Read the tab-separated data into a DataFrame
            df = pd.read_csv(io.StringIO(data.strip()), sep='\t')

            # Check if there are at least two columns
            if df.shape[1] < 2:
                return go.Figure().add_annotation(text="Please provide data with at least two columns.")

            # Prepare the angles for the radar chart
            num_angles = len(df)
            angles = [f'{i*360/num_angles:.1f}°' for i in range(num_angles)]

            # Prepare data for the two columns
            angle_values_1 = df.iloc[:, 0].values
            angle_values_2 = df.iloc[:, 1].values

            # Loop back to the start to close the radar chart
            angle_values_1 = list(angle_values_1) + [angle_values_1[0]]
            angle_values_2 = list(angle_values_2) + [angle_values_2[0]]
            angles = angles + [angles[0]]  # Ensure the angles loop closes

            # Create the radar chart figure
            fig = go.Figure()

            # First trace (for "Front /90 deg (5V)")
            fig.add_trace(go.Scatterpolar(
                r=angle_values_1,
                theta=angles,
                fill='toself',
                name='Front /90 deg (5V)',
                line=dict(color='blue')
            ))

            # Second trace (for "Front /0 deg (5V)")
            fig.add_trace(go.Scatterpolar(
                r=angle_values_2,
                theta=angles,
                fill='toself',
                name='Front /0 deg (5V)',
                line=dict(color='red')
            ))

            # Update layout for better appearance
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(angle_values_1), max(angle_values_2))]
                    ),
                    angularaxis=dict(
                        tickmode='array',
                        tickvals=angles,
                        ticktext=angles
                    )
                ),
                showlegend=True,
                title="Radar Chart of RF Data"
            )

            return fig
        except pd.errors.ParserError:
            return go.Figure().add_annotation(text="Invalid data format. Please paste tab-separated values.")
        except Exception as e:
            return go.Figure().add_annotation(text=f"Error processing data: {e}")

    # Return an initial message if no button click
    return go.Figure().add_annotation(text="Paste data and click 'Generate Radar Chart'")

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
