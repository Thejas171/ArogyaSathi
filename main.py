import streamlit as st
import google.generativeai as genai
import json
import time
apikey = "AIzaSyAsIQovdMuqHGToY-j_yLTFTKI7mykpS8o"
import pandas as pd

genai.configure(api_key=apikey)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def getRange(string):
    low=""
    high=""
    count1=0
    count2=0
    for i in string.split("-")[0]:
        if i.isdigit():
            low+=i
            count1+=1
        if count1==2:
            break
    for j in string.split("-")[1]:
        if j.isdigit():
            high+=j
            count2+=1
            if count2==2:
                break
    return int(low),int(high)




def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response


st.set_page_config(page_title="Arogya Sathi",layout='wide')
st.header("Hey There I am Arogya Sathi.")
st.subheader("Generate customized meal plan")

col1,col2 = st.columns(2)

with col1:
    gender = st.selectbox('Gender', ('Male', 'Female'))
    weight = st.number_input('Weight (kg):', min_value=30, value=80)
with col2:
    age = st.number_input('Age', min_value=18, max_value=120, step=1, value=30)
    height = st.number_input('Height (cm)', min_value=1, max_value=250, step=1, value=170)

Dietary_Preferences = st.selectbox('Dietary Preferences',("Vegetarian","Non Vegeterian","Mixed (Veg and Non-Veg)"))
aim = st.selectbox('Aim', ('Lose', 'Gain', 'Maintain'))



user_data = f""" 
                - I am a {gender}"
                - My weight is {weight} kg"
                - I am {age} years old"
                - My height is {height} cm"
                - My aim is to {aim} weight"
                - I Prefer {Dietary_Preferences}"
"""

output_format = """ 
                    "range":"Range of ideal weight. Format - 'Min-Max'",
                    "target":"Target weight",
                    "difference":"Weight i need to loose or gain",
                    "bmi":"my BMI",
                    "meal_plan":"Meal plan for 7 days. Each day should include only the following fields - Breakfast, Lunch , Dinner. They should not contain anything else except these. There should only 7 Objects, one for each day. No Nesting in each day."
                    "total_days":"Total days to reach target weight",
                    "weight_per_week":"Weight to loose or gain per week",
"""


prompt = user_data + (" given the information You are professional diet planner. Generate the ,following output in output format as follows. Generating all the values is compulsory"
                      " Give only json format nothing else ") + output_format



if st.button("Generate Meal Plan"):
    try:
        with st.spinner('Creating Meal plan'):

            text_area_placeholder = st.empty()
            meal_plan = get_gemini_response(prompt)
            generated_text = ""
            for chunk in meal_plan:
                generated_text += chunk.text

            meal_plan = generated_text

            if meal_plan.startswith("```json"):
                meal_plan = meal_plan.replace("```json\n", "", 1)  # Remove the first occurrence
            if meal_plan.endswith("```"):
                meal_plan = meal_plan.rsplit("```", 1)[0]  # Remove the trailing part

            # st.write(meal_plan)
            meal_plan_json = eval(meal_plan)
            # st.write(meal_plan_json)

            st.title("Meal Plan")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Range")
                st.write(meal_plan_json["range"])
                st.subheader("Target")
                st.write(meal_plan_json["target"])

            low,high = getRange(str(meal_plan_json["range"]))
            st.write(low,high)
            # Gain Case
            if high<weight and aim=='Gain':
                st.info("You Have to Loose Weight Not Gain")
                time.sleep(5)
                st.rerun()
            #Lose Case
            if low>weight and aim=="Lose":
                st.info("You Have to gain weight not Loose")
                time.sleep(5)
                st.rerun()

            with col2:
                st.subheader("BMI")
                st.write(meal_plan_json["bmi"])
                st.subheader("Days")
                st.write(meal_plan_json["total_days"])

            with col3:
                st.subheader(f"{aim}")
                st.write(meal_plan_json["difference"])
                st.subheader("Per week")
                st.write(meal_plan_json["weight_per_week"])

            st.subheader("Meal plan for 7 days")
            # st.write(meal_plan_json["meal_plan"])

            df = pd.DataFrame(meal_plan_json["meal_plan"])

            # st.header("Interactive table with DataFrame (st.dataframe)")
            st.dataframe(df)

    except:
       st.info("Some eror Occ")
       st.rerun()
