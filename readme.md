## Setup

1. Run `docker-compose up -d influxdb`
2. Go into [InfluxDB](http://localhost:8086/) and login with credentials:
    - admin
    - admin-seminar3a
3. Left Bar -> 3rd icon -> API Tokens -> Generate Token
4. Left Bar -> 3rd icon -> Buckets -> Create Bucket:
    - arrays
    - static
5. Copy token and Paste on:
    - `main.py -> INFLUXDB_TOKEN`
    - `./grafana/provisioning/datasources/datasource.yml -> token`
6. Run `docker-compose up -d grafana`
7. Go into [Grafana](http://localhost:3000/) and login with credentials:
    - admin
    - admin
    - Skip new password step
8. Go to Dashboards.

> **Note:** FEUP Network or VPN required