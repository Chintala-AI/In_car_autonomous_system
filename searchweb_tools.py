from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import tool
import requests
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv
 
        
class SearchWebToolInput(BaseModel):
    """Input schema for SearchWebTool."""
    argument: dict = Field(..., description="It contains user query.")

class SearchWebTools(BaseTool):
    name: str = "TAVILY SEARCH TOOL"
    description: str = (
        "Search web to get the result of the query."
    )
    args_schema: Type[BaseModel] = SearchWebToolInput

    def _run(self, argument: dict) -> list:
        # Implementation goes here
        
        load_dotenv('.env')
        
        TAVILY_API_KEY = os.environ['TAVILY_API_KEY']
        tavily_search = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=2, search_depth='advanced', max_tokens=1000)
        results = tavily_search.invoke(argument)        
        return results      
# @tool
# def get_weather(query: str) -> list:
#     """Search weatherapi to get the current weather."""
#     endpoint = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query}"
#     response = requests.get(endpoint)
#     data = response.json()

#     if data.get("location"):
#         return data
#     else:
#         return "Weather Data Not Found"

# @tool
# def search_web(query: str) -> list:
#     """Search the web for a query."""
#     tavily_search = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=2, search_depth='advanced', max_tokens=1000)
#     results = tavily_search.invoke(query)
#     return results

# @tool
# def get_parking_slot_data(query: str) -> str:
#     """Find out the parking slot data."""
#     with open("parking_slot_data.txt", "r") as file:
#         data = file.read()
#         print(data)    
#     return data
# @tool
# def get_chargingstation_data(query: str) -> str:
#     """Find out the specific information about the charging station ."""
#     with open("charging_station_data.txt", "r") as file:
#         data = file.read()
#         print(data)    
#     return data
# @tool
# def get_user_calendar_data(query: str) -> str:
#     """Find out the user calendar information ."""
#     with open("user_calendar.txt", "r") as file:
#         data = file.read()
#         print(data)    
#     return data
# @tool
# def get_user_preference_data(query: str) -> str:
#     """Find out the user preference information ."""
#     with open("user_preference.txt", "r") as file:
#         data = file.read()
#         print(data)    
#     return data
# @tool
# def get_user_car_data(query: str) -> str:
#     """Find out the user car information ."""
#     with open("user_car.txt", "r") as file:
#         data = file.read()
#         print(data)    
#     return data


        
