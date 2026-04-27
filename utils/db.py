from pymongo import MongoClient

# -------------------------------------------
# CONNECT TO MONGODB
# -------------------------------------------

# Create MongoDB client
# "localhost:27017" means:
# - MongoDB is running on your local machine
# - Default MongoDB port = 27017
client = MongoClient("mongodb://localhost:27017/")


# -------------------------------------------
# CREATE / ACCESS DATABASE
# -------------------------------------------

# If database does not exist → MongoDB will create it automatically
db = client["academic_research_analyzer"]


# -------------------------------------------
# CREATE / ACCESS COLLECTIONS (TABLES)
# -------------------------------------------

# Collection to store detailed analysis results
analysis_collection = db["analysis_results"]

# Collection to store summary logs (used in dashboard)
dashboard_collection = db["analysis_log"]

# Collection to store user feedback
feedback_collection = db["user_feedback"]