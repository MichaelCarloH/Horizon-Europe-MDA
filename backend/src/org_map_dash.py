import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.express as px

# Load data
df = pd.read_csv('/Users/keithatienza/Desktop/Academics/Modern Data Analytics/Horizon-Europe-MDA/data/processed/org_by_research.csv')

# Prepare topic list
all_topics = sorted(df['topic'].dropna().unique())

app = dash.Dash(__name__)
app.title = 'European Research Organizations by Topic'

# Custom CSS for Nunito font
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                font-family: 'Nunito', sans-serif;
            }
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h3 {
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.H1('European Research Organizations by Topic', className='app-title'),
    html.Div([
        html.Div([
            html.Label('Select topic(s):', style={'fontWeight': '600', 'marginBottom': '8px'}),
            dcc.Dropdown(
                id='topic-dropdown',
                options=[{'label': t, 'value': t} for t in all_topics],
                multi=True,
                value=['machine learning'] if 'machine learning' in all_topics else None,
                placeholder='Select topic(s)',
                style={'width': '100%'}
            ),
        ], style={'width': '70%', 'padding': '0 10px'}),
        
        html.Div([
            html.Label('Top N organizations:', style={'fontWeight': '600', 'marginBottom': '8px'}),
            dcc.Input(
                id='top-n',
                type='number',
                min=1,
                max=100,
                value=25,
                style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}
            ),
        ], style={'width': '30%', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'marginBottom': '30px', 'width': '100%'}),
    html.Div([
        dcc.Graph(id='org-map', style={'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})
    ], style={'marginBottom': '30px'}),
    
    html.H3('Organization Table', style={'marginBottom': '15px'}),
    html.Div([
        dash_table.DataTable(
            id='org-table',
            columns=[
                {'name': 'Organization', 'id': 'organizationName'},
                {'name': 'Country', 'id': 'country'},
                {'name': 'Number of Projects', 'id': 'numofProjects'},
                {'name': 'Total EC Contribution', 'id': 'totalecContribution', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
            ],
            page_size=25,
            style_table={'overflowX': 'auto', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px 15px',
                'fontFamily': 'Nunito, sans-serif'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'borderBottom': '2px solid #dee2e6',
                'fontFamily': 'Nunito, sans-serif',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f9f9f9'
                }
            ],
            sort_action='native',
            filter_action='native',
        )
    ])
], className='main-container')

@app.callback(
    [Output('org-map', 'figure'), Output('org-table', 'data')],
    [Input('topic-dropdown', 'value'), Input('top-n', 'value')]
)
def update_output(selected_topics, top_n):
    dff = df.copy()
    if selected_topics:
        # Find orgs that have all selected topics
        orgs_with_all = (
            dff[dff['topic'].isin(selected_topics)]
            .groupby(['organisationID', 'organizationName', 'country', 'latitude', 'longitude'])
            .agg({
                'topic': lambda x: set(x),
                'numofProjects': 'sum',
                'totalecContribution': 'sum'
            })
            .reset_index()
        )
        orgs_with_all = orgs_with_all[orgs_with_all['topic'].apply(lambda x: set(selected_topics).issubset(x))]
        orgs_with_all = orgs_with_all.sort_values('totalecContribution', ascending=False).head(top_n)
    else:
        orgs_with_all = (
            dff.groupby(['organisationID', 'organizationName', 'country', 'latitude', 'longitude'])
            .agg({
                'numofProjects': 'sum',
                'totalecContribution': 'sum'
            })
            .reset_index()
            .sort_values('totalecContribution', ascending=False)
            .head(top_n)
        )
    # Add a small jitter to latitude and longitude to reduce overlapping
    import numpy as np
    
    # Create a copy with jittered coordinates for visualization purposes only
    orgs_display = orgs_with_all.copy()
    
    # Apply jitter only if multiple points are close to each other
    # Define a function to add jitter to coordinates
    def add_jitter(data, lat_col='latitude', lon_col='longitude'):
        # Group by coordinates to find duplicates or very close points
        # Round to 2 decimal places to consider points very close to each other
        rounded = data.copy()
        rounded['lat_round'] = rounded[lat_col].round(2)
        rounded['lon_round'] = rounded[lon_col].round(2)
        
        # Count occurrences of rounded coordinates
        coord_counts = rounded.groupby(['lat_round', 'lon_round']).size().reset_index(name='count')
        
        # Create a dictionary of counts for each rounded coordinate pair
        count_dict = {(row['lat_round'], row['lon_round']): row['count'] 
                      for _, row in coord_counts.iterrows()}
        
        # Add jitter only to points that overlap
        for idx, row in data.iterrows():
            lat_round = round(row[lat_col], 2)
            lon_round = round(row[lon_col], 2)
            count = count_dict.get((lat_round, lon_round), 0)
            
            if count > 1:
                # Scale jitter based on count and better constants
                jitter_scale = min(0.03, 0.005 * count)
                data.at[idx, lat_col] = row[lat_col] + np.random.uniform(-jitter_scale, jitter_scale)
                data.at[idx, lon_col] = row[lon_col] + np.random.uniform(-jitter_scale, jitter_scale)
        
        return data
    
    orgs_display = add_jitter(orgs_display)
    
    # Bubble map - using px.scatter_map instead of deprecated px.scatter_mapbox
    # Increased size_max by 20% from 40 to 48
    fig = px.scatter_map(
        orgs_display,  # Using jittered data
        lat='latitude',
        lon='longitude',
        size='totalecContribution',
        color='country',
        hover_name='organizationName',
        hover_data={
            'country': True, 
            'numofProjects': True, 
            'totalecContribution': True, 
            'latitude': False, 
            'longitude': False
        },
        size_max=48,  # Increased from 40 to 48 (20% larger)
        zoom=3,
        center={'lat': 54, 'lon': 15},
        map_style='carto-positron',  # Changed from mapbox_style to map_style
        height=600,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    # Customize layout - updated mapbox to map
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        map={'style': "carto-positron"},  # Changed from mapbox to map
        font_family="Nunito, sans-serif",
        legend_title_text='Country',
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Nunito, sans-serif"
        )
    )
    # Table data
    table_data = orgs_with_all[['organizationName', 'country', 'numofProjects', 'totalecContribution']].to_dict('records')
    return fig, table_data

if __name__ == '__main__':
    app.run(debug=True)
