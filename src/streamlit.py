import streamlit as st
import pandas as pd
import pydeck as pdk

# Functions
XGBOOST = 'XGBoost'

if __name__ == '__main__':

    @st.cache
    def convert_df(df):

        return df.to_csv().encode('utf-8')


    # Web structure


    st.markdown(
        "<img alt='FCC' src='https://profesoresim2019.upc.edu/wp/wp-content/uploads/2018/09/logo_UPC.png' width='57px' height='57px' style='text-align: center; float: left'></img>"
        "<img alt='T2C' src='https://pnptc-media.s3.amazonaws.com/images/Accenture_Logo.001.2e16d0ba.fill-1200x800.jpg' width='180px' height='120px' style='text-align: center; float: right'></img>"
        "<style>.block-container{ max-width: 55rem;}</style>", unsafe_allow_html=True)

    # with st.sidebar:
    #     # Can be used wherever a "file-like" object is accepted:
    #     uploaded_file = st.file_uploader("Carga un nuevo CSV", type=["csv","xlsx"])
    #     file_separator = st.radio('Which is the CSV column separator?', options=[';',','])
    #     df_uploaded_file = pd.DataFrame()
    #     if uploaded_file is not None:
    #         df_uploaded_file = pd.read_csv(uploaded_file, sep=file_separator)

    tab1, tab2 = st.tabs(["Resultados", "Mapa"])

    with tab1:
        st.header("We have a few questiones for you, señor!")

        # SHOW UPLOAD
        # if not df_uploaded_file.empty:
        #     st.write(df_uploaded_file)
        #     desired_columns = st.multiselect('Select desired columns', options=df_uploaded_file.columns)
        #     date_column = st.radio('Which is the date variable', options=desired_columns)
        #     objective_column = st.radio('Which is the objective variable', options=desired_columns)

        # BUTTON
        results = None

        with st.form(key='my_form'):

            st.subheader("Please tell us about the order you expect.")

            order_id = st.text_input('Which ID does the order have?', placeholder="366c7a3d298f")
            origin_port = st.text_input('At which port do the order imports arrive?', placeholder="Athens")
            third_party = st.text_input('Which third party is responsible for warehousing, distribution and fulfillment services?', placeholder="v_001")
            customs_procedure = st.text_input('What is the type of customs procedure to be used in the imports legal process?', placeholder="CRF")
            logistic_hub = st.text_input('Which logistic hub is responsible for the order?', placeholder="Lille")
            customer = st.text_input('Where is the customer located?', placeholder="Vienna")
            product_id = st.text_input('What is the unique ID of the product?', placeholder="1692723")
            units = st.text_input('How many units are ordered?', placeholder="583")
            weight = st.text_input('How much does the order weigh?', placeholder="2876")
            material_handling = st.text_input('How safe is the product to handle and how easy is it to break? Provide the class, please.', placeholder="1")
            submit_button = st.form_submit_button(label='Submit')

        # create a JSON object that includes all the information
        order = {
            "order_id": order_id,
            "origin_port": origin_port,
            "third_party": third_party,
            "customs_procedure": customs_procedure,
            "logistic_hub": logistic_hub,
            "customer": customer,
            "product_id": product_id,
            "units": units,
            "weight": weight,
            "material_handling": material_handling
        }

        # for testing purposes

        if origin_port == "":
            origin_port = "Athens"
            customer = "Athens"
            logistic_hub = "Athens"

        # load data from data/datathon_SC_ACN_22/cities_data.csv into a dataframe
        df = pd.read_csv('data/datathon_SC_ACN_22/cities_data.csv', delimiter=';')

        # origin_port = "Athens"
        # customer = "Zaragoza"
        # from df retrieve city_from_coord and city_to_coord where city_from_name is origin_port and city_to_name is customer
        city_from_coord = df[df['city_from_name'] == origin_port]['city_from_coord'].values[0]
        city_to_coord = df[df['city_to_name'] == customer]['city_to_coord'].values[0]
        logistic_hub_coord = df[df['city_from_name'] == logistic_hub]['city_from_coord'].values[0]

        city_from_coord_lat = float(city_from_coord[1:-1].split(',')[0])
        city_from_coord_lon = float(city_from_coord[1:-1].split(',')[1])
        city_to_coord_lat = float(city_to_coord[1:-1].split(',')[0])
        city_to_coord_lon = float(city_to_coord[1:-1].split(',')[1])
        logistic_hub_coord_lat = float(logistic_hub_coord[1:-1].split(',')[0])
        logistic_hub_coord_lon = float(logistic_hub_coord[1:-1].split(',')[1])

        # insert the values of city_from_coord_lat and city_from_coord_lon into a dataframe with the columns "lat" and "lon"
        df = pd.DataFrame({'lat': [city_from_coord_lat, city_to_coord_lat, logistic_hub_coord_lat], 'lon': [city_from_coord_lon, city_to_coord_lon, logistic_hub_coord_lon]})

        # create a dataframe df2 with the columns "from" and "to" store coordinate pairs with the key "coordinates"
        df2 = pd.DataFrame({'from': [[city_from_coord_lon, city_from_coord_lat],[logistic_hub_coord_lon, logistic_hub_coord_lat]], 'to': [[logistic_hub_coord_lon, logistic_hub_coord_lat],[city_to_coord_lon, city_to_coord_lat]]})
        # df2 = pd.DataFrame({'from': ["51.2254018, 6.7763137"]}, {'to': ["41.6521342, -0.8809428"]})

        # create a dataframe df_ports with the columns "lat" and "lon" store the coordinates of the ports
        df_ports = pd.DataFrame({'lat': [37.9839412, 51.9244424, 41.3828939], 'lon': [23.7283052, 4.47775, 2.1774322]})

        map_data = df[["lon", "lat"]]
        
        st.pydeck_chart(pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=47.5,
                longitude=15,
                zoom=3.2,
                pitch=20,
            ),
            layers=[
                pdk.Layer(
                'ArcLayer',
                data=df2,
                get_stroke_width=40,
                get_source_position='from',
                get_target_position='to',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 5000],
                pickable=True,
                extruded=True,
                auto_highlight=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=20000,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df_ports,
                    get_position='[lon, lat]',
                    get_color='[255,0,0,255]',
                    get_radius=20000,
                ),
            ],
        ))
        if order_id == "Deutsch":
            results = "Richtig!" # this is where you would put the map and the result between 0 and 1

        # SHOW RESULTS
        if results:
            # results = f_xgboost(input=df_uploaded_file)
            st.write(results)

        # DOWNLOAD RESULTS
        # csv = convert_df(df_uploaded_file)
        # st.download_button(
        #     label="Descarga los resultados",
        #     data=csv,
        #     file_name='resultados.csv',
        #     mime='text/csv',
        # )

    # http://localhost:8501/
