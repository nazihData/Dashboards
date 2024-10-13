import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import base64
import io
from io import StringIO, BytesIO
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
# import streamlit_authenticator as stauth

st.set_page_config(page_title="Buildings", layout="wide")


package_path = "C:/Users/ahmed.nazih/Desktop/streamlit_authenticator-0.4.1"
sys.path.append(package_path)

#%% --- Authenticator
#
# Dummy credentials - replace with a more secure approach for production
USER_CREDENTIALS = {
    "208309": "Hr123456",
    "207999": "admin123",
    "205284": "a1234567"

}


usermap = {'207999': 'Ahmed Nazih', '208309': 'Abdallah', '205284': 'Hayam'}

# Function to authenticate users
def authenticate(username, password):
    if USER_CREDENTIALS.get(username) == password:
        return True
    else:
        return False

# Main app function
def main():
    st.title("CBE Dashboards")
    
    # Check if the user is already logged in
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # If not authenticated, show login form
    if not st.session_state['authenticated']:
        login_section()
    else:
        app_content()

# Login section
def login_section():
    st.subheader("Login")
    global username
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state['authenticated'] = True
            st.success("Login successful!")
            st.experimental_rerun()  # Refresh to show app content
        else:
            st.error("Invalid username or password. Please try again.")

# Main content to display after login
def app_content():
    st.sidebar.title("Menu")
    
    # Provide a logout button in the sidebar
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.experimental_rerun()

    # Display actual app content after login
    username = st.text_input("Username")
    full_name = usermap.get(username, username)  # Default to username if not found
    st.write(f"Welcome {full_name} to the secured app!")
    st.write("You are successfully logged in.")

    #%% ---
    # Streamlit page configuration
    # Function to encode image to base64
    def get_image_base64(image_path):
        image = Image.open(image_path)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    # Image path and base64 encoding
    image_path = "D:/Self-Service Launching/letterhead/new header.PNG"
    img_str = get_image_base64(image_path)

    # Center and display header image
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{img_str}" alt="Header Image" />
        </div>
        """,
        unsafe_allow_html=True
    )
    # Title and subtitle
    st.markdown("<h1 style='text-align: center; font-size: 45px;'>Employees distribution across buildings</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>October 7, 2024</h2>", unsafe_allow_html=True)


    uploaded_file = st.file_uploader("Upload Cleaned Data", type=["xlsx"])
    # File paths
    # excel_file = "C:/Users/ahmed.nazih/Desktop/serry/cleaned.xlsx"

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, sheet_name='Sheet1')
            info = pd.read_excel(uploaded_file, sheet_name='Sheet2')

    # df = pd.read_excel(excel_file, sheet_name='Sheet1').rename(columns=lambda x: x.strip())

    # info = pd.read_excel(excel_file, sheet_name='Sheet2').rename(columns=lambda x: x.strip())
            info['Sector'] = info['Sector'].fillna(info['Central'])
            
            #%% Employee Distribution and Summary
            # Total transactions per building: Group by Building Name and calculate how many employees are associated with each building.
            
            building_gp = df.groupby(by=['Building Name'], as_index=False)['Counts'].sum()
            building_gp_sorted = building_gp.sort_values(by='Counts', ascending=False)
            
            # Employee count per building: Group by Building Name and calculate how many employees are associated with each building.
            building_emp_gp = df.groupby(by=['Building Name'], as_index=False)['Number'].count()
            building_emp_gp_sorted = building_emp_gp.sort_values(by='Number', ascending=False)
            
            # Sort the transaction data by 'Counts' (from 'building_gp_sorted') and merge with employee count data
            esti_trans = building_emp_gp_sorted.merge(building_gp_sorted, on='Building Name')
            
            # Calculate Transactions per Employee
            esti_trans['Transactions per employee'] = round((esti_trans['Counts'] / esti_trans['Number']))
            
            #%%--------------------------# FIGURE (1)
            # Create a subplot with two y-axes
            fig = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,  # Share x-axis between both charts
                # subplot_titles=["Employee Count per Building and Transactions per Employee"],
                row_heights=[0.7],
                vertical_spacing=0.1,
                specs=[[{"secondary_y": True}]]  # Use secondary_y for the line chart
            )
            
            # Add bar chart for employee count per building
            bar_chart = go.Bar(
                x=building_emp_gp_sorted['Building Name'],
                y=building_emp_gp_sorted['Number'],
                name="Employee Count",
                text=building_emp_gp_sorted['Number'],
                texttemplate='%{text:,}',  # Format the text with comma separation for thousands
                textposition='outside',
                marker_color='blue',
                textfont=dict(size=14, color='black', family="Arial", weight='bold')  # Bold text on bars
            )
            
            # Add the bar chart to the figure
            fig.add_trace(bar_chart, row=1, col=1, secondary_y=False)
            
            # Add line chart for transactions per employee
            line_chart = go.Scatter(
                x=esti_trans['Building Name'],
                y=esti_trans['Transactions per employee'],
                mode='lines+markers+text',
                name="Transactions per Employee",
                line=dict(color='red'),
                marker=dict(symbol='circle', size=8),
                text=esti_trans['Transactions per employee'],  # Add text values to the line
                textposition='top center',  # Position the text above the markers
                textfont=dict(size=14, color='black', family="Arial", weight='bold')  # Bold text on line markers
            )
            
            # Add the line chart to the figure
            fig.add_trace(line_chart, row=1, col=1, secondary_y=True)
            
            # Update layout for better visibility
            fig.update_layout(
                title="<b>Count of Employees per Building and Average Count of Transactions per Employee</b>",
                title_font=dict(size=22, color='black', family="Calibri", weight='bold'),  # Bold title
                xaxis_title="",  # Hide x-axis title
                yaxis_title="",  # Hide y-axis title
                xaxis=dict(
                    tickfont=dict(size=14, color='black', family="Calibri", weight='bold'),  # Bold x-axis ticks
                    tickangle=90  # Rotate x-axis tick labels by 90 degrees
                ),
                yaxis=dict(
                    tickfont=dict(size=14, color='black', family="Calibri", weight='bold'),  # Bold y-axis ticks
                    showticklabels=False  # Hide y-axis tick labels
            
                ),
                legend=dict(font=dict(size=16, family="Calibri", weight='bold')),
                height=750
            )
            
            # Update secondary y-axis for transactions per employee
            fig.update_yaxes(
                title_text="",
                title_font=dict(size=18, color='black', family="Calibri", weight='bold'),  # Bold y-axis title
                tickfont=dict(size=14, color='black', family="Calibri", weight='bold'),
                secondary_y=True
            )
            
            # Show the combined chart
            st.plotly_chart(fig)
            
            #%%--------------------------# FIGURE (2)
            
            col1, col2 = st.columns(2, gap='large')
            
            # Create bar chart
            building_bar = px.bar(
                building_gp_sorted,
                x='Building Name',
                y='Counts',
                width=700,
                height=750,
                orientation='v',
                text=building_gp_sorted['Counts'],
                # color=building_gp_sorted['Building Name'],
                title='<b>Transactions per Building</b>',
            )
            
            # Format the text to display in thousands with commas
            building_bar.update_traces(
                texttemplate='%{text:,}',  # Format the text with comma separation for thousands
                textposition='outside',   # Position the text outside the bars
            )
            
            
            # Update chart traces and layout
            building_bar.update_traces(textfont_size=20, textfont_color='black')
            
            # Update layout to hide y-axis data and remove legend title
            building_bar.update_layout(
                xaxis_title="",
                xaxis_title_font=dict(size=22, color='black'),
                xaxis=dict(
                    tickfont=dict(size=20, color='black'),tickangle=90
                ),
                yaxis=dict(
                    tickfont=dict(size=20, color='black'),
                    showticklabels=False,  # Hide y-axis labels
                    showline=False,        # Hide y-axis line
                    showgrid=False,         # Hide y-axis grid lines
                    type='log'
                ),
                yaxis_title="<b></b>",
                yaxis_title_font=dict(size=18, color='black'),
                legend=dict(
                    font=dict(size=20),
                    x=0.40,
                    y=1.15,
                    xanchor='center',
                    yanchor='top',
                    orientation='h',
                    title_text=None,      # Hide legend title
                    traceorder='normal',
                    itemsizing='constant'
                ), showlegend=False  # Hide the legend
            
            )
            
            with col1:
                st.plotly_chart(building_bar)
            
            #%% Position Group
            df['Position Group'] = df['Position Group'].str.strip()
            position = df.groupby(by=['Position Group'], as_index = False)['Number'].nunique()
            
            custom_order = {'Executive': 1, 'Top Management': 2, 'Supervisory': 3, 'Non Supervisory': 4, 'Support Staff': 5}
            position['custom_order'] = position['Position Group'].map(custom_order)
            position.sort_values(by='custom_order', inplace=True)
            
            # Create bar chart
            position_bar = px.bar(
                position,
                x='Position Group',
                y='Number',
                width=700,
                height=750,
                orientation='v',
                text=position['Number'],
                color='Position Group',
                # color=building_gp_sorted['Building Name'],
                title='<b>Employees Count per position in this study</b>',
            )
            
            # Format the text to display in thousands with commas
            position_bar.update_traces(
                texttemplate='%{text:,}',  # Format the text with comma separation for thousands
                textposition='outside',   # Position the text outside the bars
            )
            
            
            # Update chart traces and layout
            position_bar.update_traces(textfont_size=20, textfont_color='black')
            
            # Update layout to hide y-axis data and remove legend title
            position_bar.update_layout(
                xaxis_title="",
                xaxis_title_font=dict(size=22, color='black'),
                xaxis=dict(
                    tickfont=dict(size=20, color='black'),tickangle=90
                ),
                yaxis=dict(
                    tickfont=dict(size=20, color='black'),
                    showticklabels=False,  # Hide y-axis labels
                    showline=False,        # Hide y-axis line
                    showgrid=False,         # Hide y-axis grid lines
                    type='log'
                ),
                yaxis_title="<b></b>",
                yaxis_title_font=dict(size=18, color='black'),
                legend=dict(
                    font=dict(size=20),
                    x=0.40,
                    y=1.15,
                    xanchor='center',
                    yanchor='top',
                    orientation='h',
                    title_text=None,      # Hide legend title
                    traceorder='normal',
                    itemsizing='constant'
                ), showlegend=False  # Hide the legend
            
            )
            
            with col2:
                st.plotly_chart(position_bar)
            #%% Employees transactions in multiple buildings
            multi_emp = df.groupby(by=['Number', 'Sector'], as_index=False)['Counts'].count()
            multi_identification = multi_emp[multi_emp['Counts'] > 1]
            
            # Sectors that have employees with more than one identification in more than one sector
            multi_sector = multi_identification.groupby(by=['Sector'], as_index=False)['Number'].count()
            multi_sector = multi_sector.sort_values(by='Number', ascending=False)
            
            emp_count = info.groupby(by=['Sector'], as_index=False)['Number'].count()
            
            # Calculate percentage of multi_sector['Number'] compared to emp_count['Number']
            multi_sector = multi_sector.merge(emp_count, on='Sector', suffixes=('_multi', '_total'))
            multi_sector['Percentage'] = (multi_sector['Number_multi'] / multi_sector['Number_total']) * 100
            
            
            # Create bar chart for 'Number_multi'
            fig = px.bar(
                multi_sector,
                x='Sector',
                y='Number_multi',
                width=1300,
                height=850,
                orientation='v',
                text=multi_sector['Number_multi'],
                color=multi_sector['Sector'],
                title='<b>Count of employees that can access more than one building per sector</b>'
            )
            
            # Disable the legend for the bar chart (so individual sectors are not shown)
            fig.update_traces(showlegend=False, selector=dict(type='bar'))
            
            # Add a line chart for the 'Percentage' with "%" symbol and rounded values
            fig.add_trace(
                go.Scatter(
                    x=multi_sector['Sector'],
                    y=multi_sector['Percentage'],
                    mode='lines+markers+text',
                    name='Percentage',  # Display 'Percentage' in the legend
                    yaxis='y2',
                    marker=dict(color='red'),
                    line=dict(width=3),
                    text=[f"{round(p)}%" for p in multi_sector['Percentage']],  # Round to nearest whole number and add "%"
                    textposition='top center'  # Valid text position for scatter traces
                )
            )
            
            # Format the text to display in thousands with commas for the bar chart
            fig.update_traces(
                texttemplate='%{text:,}',  # Format the text with comma separation for thousands
                textposition='outside',    # Position the text outside the bars for the bar chart
                selector=dict(type='bar')  # Apply this only to the bar chart traces
            )
            
            # Update chart traces and layout
            fig.update_traces(textfont_size=20, textfont_color='black')
            
            # Update layout similar to 'building_bar'
            fig.update_layout(
                xaxis_title="",
                xaxis_title_font=dict(size=22, color='black'),
                xaxis=dict(
                    tickfont=dict(size=20, color='black'),
                    showticklabels=True,tickangle=90
                ),
                yaxis=dict(
                    tickfont=dict(size=20, color='black'),
                    showticklabels=False,  # Hide y-axis labels
                    showline=False,        # Hide y-axis line
                    showgrid=False,         # Hide y-axis grid lines
                    title=''
                ),
                yaxis2=dict(
                    title='',
                    overlaying='y',
                    side='right',
                    tickfont=dict(size=20, color='red'),
                    showline=False,
                    showgrid=False,
                    showticklabels=False
                ),
                yaxis_title_font=dict(size=18, color='blue'),
                legend=dict(
                    font=dict(size=20),
                    x=0.70,
                    y=1.1,
                    xanchor='center',
                    yanchor='top',
                    orientation='h',
                    title_text=None,  # Hide legend title
                    traceorder='normal',
                    itemsizing='constant'
                ),
                showlegend=True  # Show legend only for the line chart ("Percentage")
            )
            
            # Add a manual legend entry for "Sectors" (since we hid the sector legends)
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color='blue'),
                name='Sectors'  # This manually adds "Sector" to the legend
            ))
            
            st.plotly_chart(fig)
            
            
            #%% Employees by sector: Group by Sector and get the count of employees in each sector.
            df['Sector'] = df['Sector'].fillna(df['Central'])
            sec_gp = df.groupby(by=['Sector', 'Building Name'], as_index=False)['Counts'].count()
            
            # Create an enhanced Treemap
            fig = px.treemap(
                sec_gp, 
                path=['Building Name', 'Sector'],  # Define the hierarchy
                values='Counts',  # Set the value for each segment
                title='<b>Treemap of Count by Building and Sector</b>',
                color='Building Name',  # Color the segments by 'Counts'
                color_continuous_scale='blues',  # Use the Viridis color scale for better contrast
                height=750,
                width=900,  # Increase width for better readability of labels
                hover_data={'Building Name': True, 'Sector': True, 'Counts': True}  # Show additional data on hover
            )
            
            # Add text labels with values from the 'Counts' column and display Sector
            fig.update_traces(
                texttemplate='%{label}<br>%{value:,}',  # Show both the sector (label) and the count value
                textinfo="label+value",  # Show both label and value in each section
            )
            
            # Customize layout for better readability and visibility
            fig.update_layout(
                title_font=dict(size=24, color='black'),  # Increase title font size
                font=dict(size=16, color='black'),  # Set font size and color for better visibility
                margin=dict(t=80, b=50, l=50, r=50),  # Adjust margins for more space around the chart
                coloraxis_colorbar=dict(
                    title='Counts',  # Set the title for the color scale legend
                    tickvals=[sec_gp['Counts'].min(), sec_gp['Counts'].max()],
                    ticktext=[f"{int(sec_gp['Counts'].min()):,}", f"{int(sec_gp['Counts'].max()):,}"]
                ),
                hoverlabel=dict(
                    bgcolor="white", 
                    font_size=16,
                    font_family="Calibri"
                )
            )
            
            col21, col22 = st.columns(2, gap='large')
            
            # Show the enhanced Treemap
            with col21:
                st.plotly_chart(fig)
            
            
            
            
            # Create an enhanced Sunburst chart
            fig = px.sunburst(
                sec_gp, 
                path=['Building Name', 'Sector'],  # Specify the hierarchy of the data
                values='Counts',  # Set the value for each slice
                title='<b>Sunburst Chart of Counts by Building and Sector</b>',
                color='Counts',  # Color by Counts to show magnitude differences
                color_continuous_scale='blues',  # Use a more distinct color scale
                height=750,
                width=900,  # Make the chart wider for better visibility
                hover_name='Building Name',  # Display Building Name on hover
                hover_data={'Sector': True, 'Counts': True},  # Show additional info on hover
            )
            
            # Customize the layout for better visibility
            fig.update_layout(
                title_font=dict(size=24, color='black'),  # Increase title font size
                font=dict(size=14, color='black'),  # Set font size and color for readability
                margin=dict(t=80, b=50, l=50, r=50),  # Adjust margins to make room for title
                sunburstcolorway=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],  # Custom color way for more distinct sectors
                legend_title=dict(text='Counts', font=dict(size=18, color='black')),  # Customize legend title
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                    font_family="Calibri"
                ),
            )
            
            
            # Show the enhanced Sunburst chart
            with col22:
                st.plotly_chart(fig)
            
            
            #%% Employees transactions in multiple buildings
            multi_emp = df.groupby(by=['Number', 'Sector'], as_index=False)['Counts'].count()
            multi_identification = multi_emp[multi_emp['Counts']>1]
            
            # sectors that have employee with more than one identification in more than one
            multi_sector = multi_identification.groupby(by=['Sector'], as_index=False)['Number'].count()
            multi_sector = multi_sector.sort_values(by='Number', ascending=False)
            
            emp_count = info.groupby(by=['Sector'], as_index=False)['Number'].count()
            
            
            
            
            #%% Create a heatmap to visualize discrepancies between 'Total count' and 'Counts'
            # Filter rows where 'Total count' and 'Counts' are not equal
            col31, col32 = st.columns(2, gap='large')
            # Group by relevant columns and sum 'Counts'
            grouped_counts = df.groupby(by=['Number', 'Name', 'Sector', 'Position Group', 'Total count'], as_index=False)['Counts'].sum()
            
            # Filter rows where 'Total count' and 'Counts' do not match (discrepancies)
            discrepancies_df = grouped_counts[grouped_counts['Total count'] != grouped_counts['Counts']]
            
            # Calculate absolute differences between 'Total count' and 'Counts'
            discrepancies_df['Difference'] = abs(discrepancies_df['Total count'] - discrepancies_df['Counts'])
            
            # Pivot the data for heatmap - Use 'Position Group' as rows and 'Sector' as columns
            heatmap_data = discrepancies_df.pivot_table(index='Position Group', columns='Sector', values='Difference', aggfunc='sum')
            
            # Create the heatmap
            fig = px.imshow(
                heatmap_data,  # Pivoted data for the heatmap
                title='<b>Heatmap of Transactions Discrepancies by Position Group and Sector</b>',
                labels={'color': 'Difference'},
                color_continuous_scale='RdBu',  # Red-blue color scale to show discrepancies
                height=600,
                width=800
            )
            
            with col31:
            # Display the heatmap in Streamlit
                st.plotly_chart(fig)
            
            # Calculate the sum of 'Total count' and 'Counts' grouped by 'Sector'
            
            # Calculate the sum of 'Total count' and 'Counts' grouped by 'Sector'
            total_sum = discrepancies_df.groupby(by='Sector', as_index=False)['Total count'].sum()
            total_transactions = discrepancies_df.groupby(by='Sector', as_index=False)['Counts'].sum()
            
            # Merge the two DataFrames on 'Sector'
            disc_data = total_transactions.merge(total_sum, on='Sector', how='left')
            
            disc_data = disc_data.rename(columns = {'Total count':'Days count', 'Counts':'Transactions count'})
            # Calculate overall totals for all sectors
            overall_total_count = disc_data['Days count'].sum()
            overall_total_transactions = disc_data['Transactions count'].sum()
            
            
            grouped_counts = df.groupby(by=['Number', 'Name', 'Sector', 'Building Name', 'Total count'], as_index=False)['Counts'].sum()
            
            # Filter rows where 'Total count' and 'Counts' do not match (discrepancies)
            discrepancies_df = grouped_counts[grouped_counts['Total count'] != grouped_counts['Counts']]
            
            # Calculate absolute differences between 'Total count' and 'Counts'
            discrepancies_df['Difference'] = abs(discrepancies_df['Total count'] - discrepancies_df['Counts'])
            
            # Pivot the data for heatmap - Use 'Position Group' as rows and 'Sector' as columns
            heatmap_data = discrepancies_df.pivot_table(index='Building Name', columns='Sector', values='Difference', aggfunc='sum')
            
            # Create the heatmap
            fig = px.imshow(
                heatmap_data,  # Pivoted data for the heatmap
                title='<b>Heatmap of Transactions Discrepancies by Building and Sector</b>',
                labels={'color': 'Difference'},
                color_continuous_scale='RdBu',  # Red-blue color scale to show discrepancies
                height=600,
                width=800
            )
            
            with col32:
            # Display the heatmap in Streamlit
                st.plotly_chart(fig)
            
            #%%
            
            # Create a bar chart showing 'Total count' and 'Counts' for each sector
            fig = px.bar(
                disc_data,
                x='Sector',  # X-axis representing sectors
                y=['Days count', 'Transactions count'],  # Values for Total count and Counts
                title='<b>Total Count of Days comparing to Total Count of Transactions</b>',
                barmode='group',  # Side-by-side bars for easy comparison
                labels={'value': 'Transactions count', 'Sector': 'Sector'},  # Customize axis labels
                height=800,
                width=1200,
                template = 'seaborn',
            
            )
            
            # Add text values to the bars with different text colors for each series
            for i, color in enumerate(['blue', 'green']):  # 'blue' for Total count, 'green' for Counts
                fig.update_traces(
                    selector=dict(name=['Days count', 'Transactions count'][i]),  # Select the respective trace
                    texttemplate='%{value:,.0f}',  # Add the value on each bar
                    textposition='outside',  # Position the text outside the bars
                    textfont=dict(color=color)  # Set different text colors for each trace
                )
            
            # Add annotations for the total sum of 'Total count' and 'Counts'
            fig.add_annotation(
                text=f"Total Count of Days: {overall_total_count:,}",  # Display the total sum of 'Total count'
                xref="paper", yref="paper",
                x=0.95, y=1.1, showarrow=False, font=dict(size=14, color="black"), align="right"
            )
            
            fig.add_annotation(
                text=f"Total Count of Transactions: {overall_total_transactions:,}",  # Display the total sum of 'Counts'
                xref="paper", yref="paper",
                x=0.95, y=1.05, showarrow=False, font=dict(size=14, color="black"), align="right"
            )
            
            # Update layout to hide x and y-axis titles
            fig.update_layout(
                title_font=dict(size=24, color='black'),
                font=dict(size=14, color='black'),
                showlegend=True,  # Show legend to distinguish between Total count and Counts
                xaxis_title=None,  # Hide the x-axis title
                yaxis_title=None,  # Hide the y-axis title
            )
            
            # Hide y-axis ticks/labels and rotate x-axis ticks
            fig.update_xaxes(tickangle=90)  # Rotate x-axis ticks by 90 degrees
            fig.update_yaxes(showticklabels=False)  # Hide y-axis tick labels
            
            
            # Display the bar chart in Streamlit
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"An error occurred: {e}")




if __name__ == "__main__":
    main()
