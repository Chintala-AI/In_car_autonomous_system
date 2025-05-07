from crewai import Task
from textwrap import dedent
from datetime import date
import streamlit as st
from tools.getweather_tools import GetWeatherTools
from tools.searchweb_tools import SearchWebTools

class ICAASTasks():
    def __init__(self):      
        # Initialize tools once
        self.GetWeatherDataTool = GetWeatherTools()
        self.SearchWebTool = SearchWebTools()
    # def __validate_inputs(self, origin, cities, interests, date_range):
    #     if not origin or not cities or not interests or not date_range:
    #         raise ValueError("All input parameters must be provided")
    #     return True

    def routeorchestrator_task(self, agent,userquery):
        #self.__validate_inputs(origin, cities, interests, range)
        return Task(description=dedent(f"""
            Coordinate with the prompt enhancer, route planner and evaluator to get the best route for the user query {userquery}.
               """),
            expected_output="""
            If user ask for change in plan then find out the source and destination information from the user if it is not specified.
            If user cancels the trip then no need to proceed further, you can stop the execution flow. If user asks for reevaluating the plan after stoppages or want to know beforehand then also check for the proper query given with source, destination and time of departure.If everything looks good then only 
            proceed and reach out to the prompt enhancer agent to get the best prompt for the route planner agent.
      Once you are satisfied with the user query, you will pass the final prompt to the route planner agent for planning the best routes.
      """,
      human_input=True,
            agent=agent)
    def prompteenhancer_task(self, agent):
        #self.__validate_inputs(origin, cities, interests, range)
        return Task(description=dedent(f"""
            Assist in prompt engineering for the route planner agent.
               """),
            expected_output="""
            Your job is to identify the most relevant information from the user query and augment it to create a more effective prompt for the route planner agent.
            You should also take into account the user preferences data like restaurants, cafes to stop by, and other places of interest.
      """,
            agent=agent)
    def routeplanner_task(self, agent):
        #self.__validate_inputs(origin, cities, interests, range)
        return Task(description=dedent(f"""
            Find top 5 alternative routes to take.
               """),
            expected_output="""
            Calculate the fastest, most economical route from source to destination
    Identify EV charging stations every 20 miles, prioritize between fast charging or slow charging stations and short queues, while considering your battery's range and charging state.
    Recommend restaurant stops featuring Thai or Mexican cuisine and cafés that offer black coffee close to charging stations or key breaks along I-5 South.
    Factor in weather and traffic forecasts, minimizing delays and optimizing travel time.
    Suggest entertainment playlists (pop songs) for a pleasant journey.
    Plan the best routes based on the following information:
    1. User preferences data like restaurants, cafes to stop by, and other places of interest.
    2. Weather forecast information to suggest the best routes.
    3. Traffic information to suggest the best routes.
    4. Electric vehicle charging stations to suggest the best routes.
    5. User calendar text file information to suggest the best routes.
    6. Assign highest weightage to the weather condition.
    7. Provide a list of top 5 alternative routes to take with the following information:
      1. Route name
      2. Estimated time to reach the destination
      3. Estimated battery consumption
      4. Estimated time to charge the vehicle
      5. Estimated time to reach the destination after charging
      6. Estimated wait time at the charging station  
    You will provide the following information:
    Detailed Route Plan:
    Identify the most efficient highway path (e.g., I-5 South).
    Specify estimated travel times and stop durations.
    Charging Points:
    Locations of EV charging stations (up to 12 stops; approximately every 20 miles).
    Wait time estimates and cost details for charging.
    Dining Suggestions:
    Recommended restaurants within budget.
    Cafés serving quality black coffee along the route accessible during breaks.
    Entertainment Features:
    Pop song playlists or radio station recommendations tailored to your preferences.
    Travel Optimization:
    Factor in real-time traffic, weather predictions, and time modifications where needed.
      """,
            agent=agent)
    def evaluator_task(self, agent):
        #self.__validate_inputs(origin, cities, interests, range)
        return Task(description=dedent(f"""
            Analyse the list of routes and pick the best one.
               """),
            expected_output="""
            Your job is to pick the best route to take and the reason for the same.
            You will suggest recommendations on minimizing battery consumption, estimated time to travel, finding the parking slots, and less waiting time.
            You should take into account the user preferences data like restaurants, cafes to stop by, and other places of interest.
            You should also take into account the weather condition, traffic condition, electric vehicle charging stations, user calendar information, and alternative routes to avoid traffic congestion.
            You should also provide a summary of the best route to take out of the list of alternatives shared by the route planner.
      """,
            agent=agent)
    
