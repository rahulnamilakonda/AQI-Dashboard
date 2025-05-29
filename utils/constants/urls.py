# Get countries with country (id, code, parameters ie(pm10, pm25, o3 etc))
GET_COUNTRIES = "https://api.openaq.org/v3/countries"

# Gets location_id, country details(id, code, parameters) & sensors data
GET_LOCATIONS = "https://api.openaq.org/v3/locations"

# To get historical data we use measurements.
GET_MEASUREMENTS_BY_SENSOR_ID_DAYS = (
    "https://api.openaq.org/v3/sensors/{sensors_id}/days"
)

GET_MEASUREMENTS_BY_SENSOR_ID_MONTHS = (
    "https://api.openaq.org/v3/sensors/{sensors_id}/days/monthly"
)

GET_MEASUREMENTS_BY_SENSOR_ID_YEARS = (
    "https://api.openaq.org/v3/sensors/{sensors_id}/years"
)

# Real Time AQI for city.
# /feed/:city/?token=:token
WQAPI_REAL_TIME_CITY = "https://api.waqi.info/feed/{city}/"

# Based on ip
WQAPI_REAL_TIME_IP = "https://api.waqi.info/feed/here/"

# Real Time AQI for lats and longs.
# /feed/geo::lat;:lng/?token=:token
WQAPI_REAL_TIME_CORDS = "https://api.waqi.info/feed/geo:{lat};{long}/"

# Real Time AQI for lats and longs Range.
# /map/bounds?token=:token&latlng=:latlng
WQAPI_REAL_TIME_CORDS_RANGE = "https://api.waqi.info/map/bounds"
