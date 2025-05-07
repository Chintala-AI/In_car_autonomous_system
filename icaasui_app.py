__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from crewai import Crew, LLM
from crewai import Process
from trip_agents import TripAgents, StreamToExpander
from trip_tasks import TripTasks
from icaas_agents import ICAASAgents, StreamToExpander
from icaas_tasks import ICAASTasks
import streamlit as st
import datetime
import sys
from langchain_openai import OpenAI
import os
from dotenv import load_dotenv
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

load_dotenv()
text_source = TextFileKnowledgeSource(
    file_paths=["charging_station_data.txt", "parking_slot_data.txt","user_calendar.txt","user_car_data.txt","user_preference.txt"]
)
st.set_page_config(page_icon="✈️", layout="wide")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


class TravelCrew:
    load_dotenv()
    # AZUREOPEN_API_KEY=os.environ['AZUREOPEN_API_KEY']
    def __init__(self, userquery):
        self.userquery = userquery
        # self.origin = origin
        # self.interests = interests
        # Convert date_range to string format for better handling
        # self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        self.llm = LLM(
            model="azure/gpt-4o-mini",
            base_url="https://azautoinnovtor9133940569.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview",
            api_key=os.environ['AZUREOPEN_API_KEY']
            ) 
        self.manager_llm = LLM(
            model="azure/gpt-4o",
            base_url="https://azautoinnovtor9133940569.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview",
            api_key=os.environ['AZUREOPEN_API_KEY']
            ) 
        # self.llm = OpenAI(
        #     temperature=0.7,
        #     model_name="gpt-4",
        # )

    def run(self):
        try:
            agents = ICAASAgents(manager_llm=self.manager_llm,llm=self.llm)
            tasks = ICAASTasks()

            routeorchestrator = agents.routeorchestrator()
            promptenhancer = agents.promptenhancer()
            routeplanner = agents.routeplanner()            
            evaluator = agents.evaluator()           

            routeorchestrator_task = tasks.routeorchestrator_task(routeorchestrator,self.userquery)
            prompteenhancer_task = tasks.prompteenhancer_task(promptenhancer)
            routeplanner_task = tasks.routeplanner_task(routeplanner)
            evaluator_task = tasks.evaluator_task(evaluator)

            crew = Crew(
                agents=[
                    routeorchestrator,promptenhancer,routeplanner,evaluator
                ],
                tasks=[routeorchestrator_task,prompteenhancer_task,routeplanner_task,evaluator_task],
                verbose=True,
                process=Process.hierarchical,                
                #manager_agent="routeorchestrator",
                manager_llm=self.manager_llm,
                memory=True,
                knowledge_sources=[text_source], # Add your knowledge sources here
                # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
            )
            # userquery=input("Please enter your query: ")
            # inputs = {       
            #     'userquery': userquery,
            # }
            result = crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


if __name__ == "__main__":
    icon("🏖️ ICAASAgent")

    st.subheader("Let AI agents plan your trip!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    # next_year = today.year + 1
    # jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            userquery = st.text_input(
                "Enter your trip query", placeholder="")  
            submitted = st.form_submit_button("Submit")

        st.divider()

        # Credits to joaomdmoura/CrewAI for the code: https://github.com/joaomdmoura/crewAI
        st.sidebar.markdown(
        """
        Credits to [**@joaomdmoura**](https://twitter.com/joaomdmoura)
        for creating **crewAI** 🚀
        """,
            unsafe_allow_html=True
        )

        st.sidebar.info("Click the logo to visit GitHub repo", icon="👇")
        st.sidebar.markdown(
            """
        <a href="https://github.com/bsujcg79/In_Car_Autonomous_Assistant_System" target="_blank">
            ICAAS Planner
        </a>
        """,
            unsafe_allow_html=True
        )


if submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            travel_crew = TravelCrew(userquery)
            result = travel_crew.run()
        status.update(label="✅ Trip Plan Ready!",
                      state="complete", expanded=False)

    st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.markdown(result)
