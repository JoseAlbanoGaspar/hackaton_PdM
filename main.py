import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json


# MQTT Configuration
MQTT_BROKER = "10.227.115.16"
MQTT_PORT = 1883
MQTT_TOPIC = "welding_line/welding_machine"
MQTT_CLIENT_ID = "mqtt_influx_client"

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
# Token that you need to Generate on InfluxDB UI
INFLUXDB_TOKEN = "pYf_19N_SqZty_lfdworrdSekc31iCdzFiRvER2AFVL7xLnFHEWPjkRA4nkMpUEMoUK2YC7Bwtrc8o8MxmtkkQ=="
INFLUXDB_ORG = "seminar3a"
INFLUXDB_BUCKET = "static"

STATIC_KEYS = ["timeStart", "timeEnd", "environmentT", "motorBearingT", "spindleBearingT", "counter", "sdIntensity"]
ARRAY_KEYS = ["times", "angularVelocity", "force", "displacement"]


def filter_data(keys_to_extract, data):
    return {key: data[key] for key in keys_to_extract if key in data}

def write_influx(point, bucket):
    try:
        with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=bucket, record=point)
            #print(f"Data written to InfluxDB bucket '{bucket}': {point.to_line_protocol()}")
    except Exception as e:
        print(f"Failed to write point to InfluxDB: {e}")


def deal_with_static_data(data):
    # Write to InfluxDB
    point = Point("mqtt_data")
    for key, value in data.items():
        if isinstance(value, (int, float)):
            point = point.field(key, value)
    write_influx(point, 'static')
    print("Static data stored successfully")

def deal_with_vectorial_data(data):
    """
    Process vectorial data and store each key in its respective bucket.
    Each element in the list is stored as a unique point with its timestamp.
    """
    # Ensure the 'times' key exists for timestamps
    if 'times' not in data or not isinstance(data['times'], list):
        print("Error: 'times' key is missing or not a list in vectorial data.")
        return

    # Extract timestamps
    timestamps = data['times']

    # Check consistency of list lengths
    for key in ARRAY_KEYS:
        if key != 'times' and key in data and len(data[key]) != len(timestamps):
            print(f"Error: Length mismatch between 'times' and '{key}' in vectorial data.")
            return

    forces = data['force']
    angular_vel = data['angularVelocity']
    displacements = data['displacement']
    for i in range(len(forces)):
        # Create a point with the value and timestamp
        point = Point("arrays")
        point.field("angularVelocity", float(angular_vel[i]))
        point.field("displacement", float(displacements[i]))
        point.field("force", float(forces[i]))

        write_influx(point, "arrays")        

    print("Vectorial data processed and written to InfluxDB.")

def deal_with_extra_features(data):
    force = data['force']
    angular_vel = data['angularVelocity']
    #computing the first and last indexes in the array != from zero
    n = len(force)
    start_force = next((i for i in range(n) if force[i] != 0), None)
    end_force = next((i for i in range(n - 1, -1, -1) if force[i] != 0), None)
    
    start_ang = next((i for i in range(n) if angular_vel[i] != 0), None)
    end_ang = next((i for i in range(n - 1, -1, -1) if angular_vel[i] != 0), None)

    #computing new variables
    welding_time = data['times'][end_force] - data['times'][start_force]
    data['welding_time_force'] = welding_time

    welding_time_ang = data['times'][end_ang] - data['times'][start_ang]
    data['welding_time_ang'] = welding_time_ang

    diff_force_ang = data['times'][start_force] - data['times'][start_ang]
    data['diff_force_ang'] = diff_force_ang

    # add all static data
    deal_with_static_data(data)

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the MQTT broker."""
    try:
        message_payload = msg.payload.decode("utf-8")
        # print(f"Received message from {msg.topic}: {message_payload}")
        
        # Parse and format the payload as needed
        # Assuming payload is in JSON format (adjust parsing for your case)
        data = json.loads(message_payload)

        deal_with_extra_features(data)
        deal_with_vectorial_data(data)

    except Exception as e:
        print(f"Failed to process message: {e}")

def main():
    # Initialize MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

        # Blocking loop to process network traffic
        client.loop_forever()

    except KeyboardInterrupt:
        print("Disconnecting from MQTT broker...")
        client.disconnect()

if __name__ == "__main__":
    main()
