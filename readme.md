## Setup

1. Run `docker-compose up -d influxdb`
2. Go into [influxdb](http://localhost:8086/) and login with credentials:
    - admin
    - admin-seminar3a
3. Left Bar -> 3rd icon -> API Tokens -> Generate Token
4. Copy token and Paste on `telegraf.conf -> token`
5. Run rest of docker containers `docker-compose up -d telegraf grafana`

## Next Steps

1. Choose a language to code with MQTT -> Python
2. Create a client MQTT -> Connect to theirs MQTT Broker -> Subscribe topic.
3. Process Data:
    - Create new variables
    - Manage current values
4. Send it to another topic
    - e.g. /seminar3a/welding_data
    - copy this topic to `telegraf.conf -> topics`
5. Re-run Telegraf on Docker and data will be added to InfluxDB.
    - Need **VPN connection** to reach MQTT Broker.

## Grafana
Aula.