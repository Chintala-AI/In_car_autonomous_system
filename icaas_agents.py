
from crewai import Agent
import re
import streamlit as st
from langchain_core.language_models.chat_models import BaseChatModel
from crewai import LLM
from tools.browser_tools import BrowserTools
from tools.calculator_tools import CalculatorTools
from tools.search_tools import SearchTools
from tools.getweather_tools import GetWeatherTools
from tools.searchweb_tools import SearchWebTools
import os
from dotenv import load_dotenv

class ICAASAgents():
    #AZUREOPEN_API_KEY=os.environ['AZUREOPEN_API_KEY']
    def __init__(self, manager_llm: BaseChatModel = None,llm: BaseChatModel = None):
        if llm is None:
            #self.llm = LLM(model="groq/deepseek-r1-distill-llama-70b")
            self.llm = LLM(
            model="azure/gpt-4o-mini",
            base_url="https://azautoinnovtor9133940569.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview",
            api_key=os.environ['AZUREOPEN_API_KEY']
            )  
        else:
            self.llm = llm
        if manager_llm is None:
            #self.llm = LLM(model="groq/deepseek-r1-distill-llama-70b")
            self.manager_llm = LLM(
            model="azure/gpt-4o",
            base_url="https://azautoinnovtor9133940569.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview",
            api_key=os.environ['AZUREOPEN_API_KEY']
            )  
        else:
            self.manager_llm = manager_llm   

        # Initialize tools once
        self.search_tool = SearchTools()
        self.browser_tool = BrowserTools()
        self.calculator_tool = CalculatorTools()
        self.searchweb_tool=SearchWebTools()
        self.getweather_tool=GetWeatherTools()

    def routeorchestrator(self):
        return Agent(
            role='Route Orchestrator',
            goal='Analyze user query and serve the response',
            backstory=""""
            You're an orchestrator of route planning for user journey. You take in user query analyze for source, destination and departure time and take help from prompt enhancer to augment the user query for the route planner agent.
            Reach out to prompt enhancer to get the best prompt for the route planner agent. Repeat the step until the best prompt is generated.
            Once you are satified with the user query from the prompt enhancer, you will pass the final prompt to the route planner agent for planning the best routes.
            You may have to repeat the steps again if user request for alternate suggestion.
            You take input from the user until you are satisfied with the details.
                    """,
            #tools=[self.search_tool, self.browser_tool],
            allow_delegation=True,
            llm=self.llm,           
            verbose=True
            
        )

    def promptenhancer(self):
        return Agent(
            role='Prompt Enhancer',
            goal='You serve with the best prompt to serve the user query by the orchestrator.',
            backstory="""You're an expert prompt enhancer with a deep understanding of the prompt engineering.
    You have a knack for identifying the most relevant information from the user query and augmenting it to create a more effective prompt for the route orchestrator agent.
    Analyse the user query and identify the most relevant information to include in the prompt.
    You should fetch the source, destination and departure time from the user query.
    You should also take into account the user preferences data like restaurants, cafes to stop by, and other places of interest.""",
            tools=[self.searchweb_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            context=[self.routeorchestrator()]
        )
    
    def routeplanner(self):
        return Agent(
            role='Smart Travel Route Planner Assistant',
            goal="""Plan optimal travel route and list of 3 maximum best possible routes to take from source to destination.""",
            backstory="""You're a seasoned travel route planner to guide travelers on their journeys.
    You help business traveler who will be attending a high-priority/medium/low priority meeting. Based on the importance of both cost-efficiency and battery management, planning the route with suitable EV charging stations is critical. Additional stops for refreshing meals and energizing coffee are optional but desirable for enhancing user experience.
    You have a knack for finding the most cost effective routes ensuring least possible battery consumption and estimated time to reach destination.
    You should recieve the best prompt from the route orchestrator agent and use it to plan the best routes.
    You use the context and may use user preferences data to suggest the various alternate routes. You have a deep understanding of the travel landscape and are always up-to-date with the latest traffice routes and weather conditions.
    Use the tools at your disposal to get the best possible routes:
    You first have to invoke the user calendar task to get the meeting location information.
    Plan the best routes based on the following information:
    1.**User preferences data like restaurants, cafes to stop by, and other places of interest.
    2.**Weather forecast information to suggest the best routes.
    2.**Traffic information to suggest the best routes.
    3.**Electric vehicle charging stations to suggest the best routes.
    4.**User calendar information to suggest the best routes.
    Assign highest weightage to the weather condition.Be precise in your output.""",
            tools=[self.getweather_tool,self.searchweb_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            planning=True,
            context=[self.routeorchestrator()]
        )
    def evaluator(self):
        return Agent(
            role='Route Reviewer',
            goal='Create a summary of the best route to take out of the list of alternatives shared by the route planner.',
            backstory="""Your job is to pick the best route to take and the reason for the same. You will suggest recommendations on minimizing battery consumption, estimated time to travel, finding the parking slots, and less waiting time.
    You should take into account the user preferences data like restaurants, cafes to stop by, and other places of interest.
    Using the context analyse the list of routes and pick the best one based on the following criteria and include the same in your final response:
    1. Battery consumption
    2. Estimated time to travel
    3. Finding the parking slots
    4. Less waiting time
    5. User preferences data like restaurants, cafes to stop by, and other places of interest.
    6. Weather condition
    7. Traffic condition
    8. Electric vehicle charging stations
    9. User calendar text file information
    10. Alternative routes to avoid traffic congestion
    11. Estimated time to reach the destination
    12. Estimated time to charge the vehicle
    13. Estimated time to reach the destination after charging
    14. Availability of charging slots
    15. Type of charging station (fast, slow, etc.)
    16. Estimated wait time
    17. Distance from the current location
    18. Name of the charging station
    19. Traffic congestion level (low, medium, high)
    20. Alternative routes to avoid traffic congestion. Be precise in your output.""",
            tools=[self.getweather_tool,self.searchweb_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            context=[self.routeorchestrator()]
        )
###########################################################################################
# Print agent process to Streamlit app container                                          #
# This portion of the code is adapted from @AbubakrChan; thank you!                       #
# https://github.com/AbubakrChan/crewai-UI-business-product-launch/blob/main/main.py#L210 #
###########################################################################################
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']
        self.color_index = 0

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # # Check if the text contains the specified phrase and apply color
        # if "Entering new CrewAgentExecutor chain" in cleaned_data:
        #     self.color_index = (self.color_index + 1) % len(self.colors)
        #     cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", 
        #                                       f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        # if "Route Orchestrator" in cleaned_data:
        #     cleaned_data = cleaned_data.replace("Route Orchestrator", 
        #                                       f":{self.colors[self.color_index]}[Route Orchestrator]")
        # if "Prompt Enhancer" in cleaned_data:
        #     cleaned_data = cleaned_data.replace("Prompt Enhancer", 
        #                                       f":{self.colors[self.color_index]}[Prompt Enhancer]")
        # if "Smart Travel Route Planner Assistant" in cleaned_data:
        #     cleaned_data = cleaned_data.replace("Smart Travel Route Planner Assistant", 
        #                                       f":{self.colors[self.color_index]}[Smart Travel Route Planner Assistant]")
        # if "Route Reviewer" in cleaned_data:
        #     cleaned_data = cleaned_data.replace("Smart Travel Route Planner Assistant", 
        #                                       f":{self.colors[self.color_index]}[Route Reviewer]")
        # if "Finished chain." in cleaned_data:
        #     cleaned_data = cleaned_data.replace("Finished chain.", 
        #                                       f":{self.colors[self.color_index]}[Finished chain.]")

        # self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

    def flush(self):
        """Flush the buffer to the expander"""
        if self.buffer:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

    def close(self):
        """Close the stream"""
        self.flush()
