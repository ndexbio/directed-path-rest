import ConfigParser
import os

Config = ConfigParser.ConfigParser()

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

Config.read("config.ini")

#===================================
# Process the two way edge types
#===================================
two_way_edges  = Config.get("EdgeClasses", "TwoWayEdges").split(",")

#===================================
# Process the preference schedule
#===================================
preference_schedule_ini = {}
prefs = Config.options("PreferenceSchedule")
for option in prefs:
    try:
        if Config.get("PreferenceSchedule", option) != -1 and len(Config.get("PreferenceSchedule", option)) > 0:
            preference_schedule_ini[option] = Config.get("PreferenceSchedule", option).split(",")
        else:
            preference_schedule_ini[option] = []
    except:
        preference_schedule_ini[option] = []
