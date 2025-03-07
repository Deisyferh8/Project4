import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#Print text
st.header('Marked of used cars')
st.write('filter the data below to see the ads by manufacturer')


#Display Dataframe 
df = pd.read_csv('vehicles_us.csv')


#Change the date type
df['date_posted'] = pd.to_datetime(df['date_posted'], format='%Y-%m-%d')

#Changing the 'price' column type
df['price'].astype('Int64', errors='ignore')

df['cylinders'].round(0)


# Fill missing values for 'odometer' column with group mean
df['odometer'] = df.groupby('model')['odometer'].transform(lambda x: x.fillna(x.mean()))

# Fill any remaining missing values for 'odometer' column with the overall mean
df['odometer'].fillna(df['odometer'].mean(), inplace=True)

#creating a new column 'avg_miles' wich will be used to calculate the values to fill the missing values in the 'model_year' column
df['avg_miles'] = df['odometer'] / (df['date_posted'].dt.year - df['model_year'] + 1)
df.head()

#obtaining the average of the 'avg_miles' column to used as a general value in the calculation of the function to fill the missing values in the 'model_year' column
avg_miles = df[~df['avg_miles'].isna()]['avg_miles'].mean()
np.ceil(avg_miles)

# Fill missing values for 'model_year' column with apply function.
def fill_year(row):
    #print(row)
    if pd.isna(row['model_year']):
        if ~pd.isna(row['odometer']):
            used_years = np.ceil(row['odometer'] / avg_miles)
            model_year = row['date_posted'].year - used_years
            return model_year
        else:
            return row['model_year']
    else:
        return row['model_year']

df['model_year'] = df.apply(fill_year, axis=1)



# Fill missing values for 'odometer' column with group mean
df['cylinders'] = df.groupby('model')['cylinders'].transform(lambda x: x.fillna(x.mean()))


# Fill missing values for 'paint_color' column with group mean
df['paint_color'] = df.groupby('model')['paint_color'].transform(lambda x: x.fillna(x.mode()[0]))


# Fill missing values in 'is_4wd' column with 0
df['is_4wd'] = df['is_4wd'].fillna(0)

# Fill missing values for the 'avg_miles' column just created with its mean()
df['avg_miles'] = df['avg_miles'].fillna(15535)




#create a new column manufacturer by getting the first word from the model column
df['manufacturer'] = df['model'].apply(lambda x: x.split()[0])

#looking for the unique() values that we can find in the 'manufacturer' column in order to create the select box
manufacturer_choice = df['manufacturer'].unique()

# creating a select box from the 'manufacturer' column
selected_manu = st.selectbox('select a manufacturer', manufacturer_choice)

#obteining the min and max values of the model_year to create a range slider 
min_year, max_year = int(df['model_year'].min()), int(df['model_year'].max())

#Creating the range slider
year_range = st.slider("Choose the years", value=(min_year, max_year), min_value = min_year, max_value = max_year)

#Showing the min and max value of the years in the slider just created
actual_range = list(range(year_range[0], year_range[1]+1))

#creating the filter of the select box
df_filtered = df[ (df.manufacturer == selected_manu) & df.model_year.isin(list(actual_range)) ]
df_filtered



st.header('Price analysis')
st.write("""
###### Let's analyse what influences price the most. We will check how distribution of price varies depending on transmission, cylinders, type, paint_color, is_4wd, condition
""")

#Choices of the box selection that the users are going to have
list_for_hist = ['transmission','cylinders', 'type', 'fuel']

#Creating box selection
selected_type = st.selectbox('split for price distribution', list_for_hist)

#Ploting a histogram of the distribution of the price vs the significant caracteristics of the vehicle
fig1= px.histogram(df, x='price', color= selected_type)
fig1.update_layout(title= "<b> Split of price by {}</b>".format(selected_type), xaxis=dict( range=[0, 50000]))
st.plotly_chart(fig1)




#Creating a column 'age' 
df['age'] = df['date_posted'].dt.year - df['model_year']

#Making the function to create the feature for the scaterplot based the 'age' column just created
def age_category(x):
    if x<5: return '<5'
    elif x>=5 and x<10: return '5-10'
    elif x>=10 and x<20: return '10-20'
    else: return '>20'

#using the .apply() method to run the previous function to the 'age' column just created
df['age_category'] = df['age'].apply(age_category)


#Choices of the box selection that the users are going to have
list_for_scatter = ['odometer', 'paint_color', 'is_4wd', 'condition']

#Creating box selection
choice_for_scatter = st.selectbox('Price dependency on', list_for_scatter)

#Making a scatterplot to show the distribution of the price vs other significant caracteristics of the vehicle
fig2= px.scatter(df, x='price', y= choice_for_scatter, color = "age_category", hover_data=['model_year'])
fig2.update_layout(title= "<b> Price vs {}</b>".format(choice_for_scatter))
st.plotly_chart(fig2)



#Choices of the box selection that the users are going to have
list_for_box = ['manufacturer', 'condition', 'model_year','age']

#Creating box selection
choice_for_box = st.selectbox('Price dependency on', list_for_box)

# Making a Box plot for price by other significant caracteristics of the vehicle
fig3= px.box(df, x=choice_for_box, y= 'price', title='Price by Manufacturer')
fig3.update_layout(title= "<b> Price vs {}</b>".format(choice_for_box))
st.plotly_chart(fig3)




st.header('Vehicle types by manufacturer')
st.write('To see the distribution of vehicle types by the manufacturer (e.g. how many Ford sedans vs. trucks are in this dataset')
# create a plotly histogram figure
fig4 = px.histogram(df, x='manufacturer', color='type', title="Distribution of vehicle types by the manufacturer")
# display the figure with streamlit
st.write(fig4)




st.header('Compare price distribution between manufacturers')
# get a list of car manufacturers
manufac_list = sorted(df['manufacturer'].unique())
# get user's inputs from a dropdown menu
manufacturer_1 = st.selectbox(
                              label='Select manufacturer 1', # title of the select box
                              options=manufac_list, # options listed in the select box
                              index=manufac_list.index('chevrolet') # default pre-selected option
                              )
# repeat for the second dropdown menu
manufacturer_2 = st.selectbox(
                              label='Select manufacturer 2',
                              options=manufac_list, 
                              index=manufac_list.index('hyundai')
                              )
# filter the dataframe 
mask_filter = (df['manufacturer'] == manufacturer_1) | (df['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]

# add a checkbox if a user wants to normalize the histogram
normalize = st.checkbox('Normalize histogram', value=True)
if normalize:
    histnorm = 'percent'
else:
    histnorm = None

# create a plotly histogram figure
fig5 = px.histogram(df_filtered,
                      title='Price vs Manufacturer',                  
                      x='price',
                      nbins=30,
                      color='manufacturer',
                      histnorm=histnorm,
                      barmode='overlay')
#display the figure with streamlit
st.write(fig5)
                     
