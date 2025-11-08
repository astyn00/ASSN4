# 📊 GRAFANA DASHBOARDS GUIDE - ASSIGNMENT 4

Подробная инструкция по созданию трёх дашбордов в Grafana.

---

## 🚀 БЫСТРЫЙ СТАРТ

### Шаг 1: Запусти все сервисы

```bash
# В папке проекта
docker-compose up -d

# Проверь что всё запустилось
docker-compose ps

# Должно быть:
# prometheus        running   0.0.0.0:9090->9090/tcp
# grafana           running   0.0.0.0:3000->3000/tcp
# postgres_exporter running   0.0.0.0:9187->9187/tcp
# node_exporter     running   0.0.0.0:9100->9100/tcp
```

### Шаг 2: Открой Grafana

```
URL: http://localhost:3000
Username: admin
Password: admin
```

При первом входе попросит сменить пароль (можешь оставить admin/admin для теста)

### Шаг 3: Добавь Data Source

1. **Configuration (⚙️)** → **Data Sources** → **Add data source**
2. Выбери **Prometheus**
3. Заполни:
   - **Name:** Prometheus
   - **URL:** http://prometheus:9090
   - **Access:** Server (default)
4. Нажми **Save & Test** → должно быть ✅ "Data source is working"

---

## 📋 ОБЩИЕ ШАГИ ДЛЯ ВСЕХ ДАШБОРДОВ

### Создание нового дашборда:

1. **+ (Create)** → **Dashboard**
2. **Add new panel**
3. Внизу найди **Query** и вставь PromQL запрос
4. Справа настрой **Panel options:**
   - Title: Название графика
   - Description: Описание
5. Выбери **Visualization** (тип графика)
6. Нажми **Apply**

### Типы визуализаций для задания:

- **Time series** - линейный график (для динамики)
- **Gauge** - круглый индикатор (для текущих значений)
- **Stat** - большая цифра (для важных метрик)
- **Bar chart** - столбчатая диаграмма
- **Heatmap** - тепловая карта
- **Table** - таблица
- **Pie chart** - круговая диаграмма

**ВАЖНО:** Минимум 4 РАЗНЫХ типа на каждом дашборде!

---

## 🗄️ DASHBOARD 1: DATABASE MONITORING

### Создай дашборд:

1. **+ Create** → **Dashboard**
2. **Settings (⚙️)** → **General**
   - Name: **PostgreSQL Database Monitoring**
   - Tags: database, postgres, nba
3. **Save**

### Panel 1: Active Connections (Gauge)

```
Title: Active Database Connections
Query: pg_stat_activity_count{datname="nba_analytics"}
Visualization: Gauge
Thresholds:
  - Green: 0-50
  - Yellow: 51-100
  - Red: >100
```

### Panel 2: Database Size (Stat)

```
Title: Database Size (GB)
Query: pg_database_size_bytes{datname="nba_analytics"} / 1024 / 1024 / 1024
Visualization: Stat
Unit: GB
```

### Panel 3: Read Operations Rate (Time series)

```
Title: Read Operations per Second
Query: rate(pg_stat_database_blks_read{datname="nba_analytics"}[5m])
Visualization: Time series
```

### Panel 4: Write Operations Rate (Time series)

```
Title: Write Operations per Second
Query: rate(pg_stat_database_tup_inserted{datname="nba_analytics"}[5m]) + 
       rate(pg_stat_database_tup_updated{datname="nba_analytics"}[5m])
Visualization: Time series
```

### Panel 5: Cache Hit Ratio (Gauge)

```
Title: Cache Hit Ratio (%)
Query: (sum(rate(pg_stat_database_blks_hit{datname="nba_analytics"}[5m])) /
        (sum(rate(pg_stat_database_blks_hit{datname="nba_analytics"}[5m])) + 
         sum(rate(pg_stat_database_blks_read{datname="nba_analytics"}[5m])))) * 100
Visualization: Gauge
Thresholds:
  - Red: 0-80
  - Yellow: 81-95
  - Green: >95
```

### Panel 6: Transactions (Time series)

```
Title: Transactions (Commits + Rollbacks)
Query: rate(pg_stat_database_xact_commit{datname="nba_analytics"}[1m]) + 
       rate(pg_stat_database_xact_rollback{datname="nba_analytics"}[1m])
Visualization: Time series
```

### Panel 7: Database Uptime (Stat)

```
Title: Database Uptime (hours)
Query: (time() - pg_postmaster_start_time_seconds) / 3600
Visualization: Stat
Unit: hours
```

### Panel 8: Deadlocks (Bar chart)

```
Title: Deadlocks Count
Query: sum(rate(pg_stat_database_deadlocks{datname="nba_analytics"}[10m]))
Visualization: Bar chart
```

### Panel 9: Table Stats (Table)

```
Title: Average Table Rows by Schema
Query: avg(pg_stat_user_tables_n_live_tup) by (schemaname)
Visualization: Table
```

### Panel 10: Long Queries (Stat)

```
Title: Long Running Queries (>5s)
Query: count(pg_stat_activity_max_tx_duration{datname="nba_analytics"} > 5)
Visualization: Stat
Color: Red if > 0
```

### Добавь Dashboard Variable (глобальный фильтр):

1. **Dashboard settings (⚙️)** → **Variables** → **Add variable**
2. **Name:** database
3. **Type:** Query
4. **Query:** 
   ```
   label_values(pg_database_size_bytes, datname)
   ```
5. **Save**

Теперь можешь использовать `$database` в запросах вместо `"nba_analytics"`

### Создай Alert:

1. Открой панель "Active Connections"
2. **Alert** → **Create alert rule**
3. **Condition:** WHEN last() OF query() IS ABOVE 100
4. **For:** 5m
5. **Name:** Too Many Database Connections
6. **Save**

---

## 💻 DASHBOARD 2: SYSTEM MONITORING

### Создай дашборд:

1. **+ Create** → **Dashboard**
2. **Settings (⚙️)** → **General**
   - Name: **System Resource Monitoring**
   - Tags: system, node, resources
3. **Save**

### Panel 1: CPU Usage by Core (Time series)

```
Title: CPU Usage per Core (%)
Query: 100 - (avg by (cpu) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
Visualization: Time series
Legend: {{cpu}}
```

### Panel 2: Load Average (Time series)

```
Title: System Load Average
Queries:
  - node_load1 (Legend: 1 min)
  - node_load5 (Legend: 5 min)
  - node_load15 (Legend: 15 min)
Visualization: Time series
```

### Panel 3: Memory Usage (Gauge)

```
Title: RAM Usage (%)
Query: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
Visualization: Gauge
Thresholds:
  - Green: 0-70
  - Yellow: 71-85
  - Red: >85
```

### Panel 4: Total Memory (Stat)

```
Title: Total RAM (GB)
Query: node_memory_MemTotal_bytes / 1024 / 1024 / 1024
Visualization: Stat
Unit: GB
```

### Panel 5: Available Memory (Stat)

```
Title: Available RAM (GB)
Query: node_memory_MemAvailable_bytes / 1024 / 1024 / 1024
Visualization: Stat
Unit: GB
Color: Green
```

### Panel 6: Disk Free Space (Gauge)

```
Title: Free Disk Space (GB)
Query: node_filesystem_avail_bytes{mountpoint="/",fstype!="tmpfs"} / 1024 / 1024 / 1024
Visualization: Gauge
```

### Panel 7: Disk I/O (Time series)

```
Title: Disk I/O (MB/s)
Queries:
  - rate(node_disk_read_bytes_total[5m]) / 1024 / 1024 (Legend: Read)
  - rate(node_disk_written_bytes_total[5m]) / 1024 / 1024 (Legend: Write)
Visualization: Time series
```

### Panel 8: Network Traffic (Time series)

```
Title: Network Traffic (Mbit/s)
Queries:
  - rate(node_network_receive_bytes_total{device!="lo"}[1m]) * 8 / 1000000 (Legend: RX)
  - rate(node_network_transmit_bytes_total{device!="lo"}[1m]) * 8 / 1000000 (Legend: TX)
Visualization: Time series
```

### Panel 9: System Uptime (Stat)

```
Title: System Uptime (days)
Query: (time() - node_boot_time_seconds) / 86400
Visualization: Stat
Unit: days
```

### Panel 10: CPU Heatmap (Heatmap)

```
Title: CPU Usage Heatmap
Query: rate(node_cpu_seconds_total{mode!="idle"}[5m])
Visualization: Heatmap
```

### Dashboard Variable:

1. **Settings** → **Variables** → **Add variable**
2. **Name:** interval
3. **Type:** Interval
4. **Values:** 1m,5m,10m,30m,1h
5. Используй `[$interval]` в запросах вместо `[5m]`

### Alert:

```
Panel: RAM Usage
Condition: WHEN last() IS ABOVE 90
For: 5m
Name: High Memory Usage
```

---

## 🌤️ DASHBOARD 3: WEATHER MONITORING

### Создай дашборд:

1. **+ Create** → **Dashboard**
2. **Settings (⚙️)** → **General**
   - Name: **Weather Monitoring (OpenWeather API)**
   - Tags: weather, api, custom
3. **Save**

### Panel 1: Current Temperature (Gauge)

```
Title: Current Temperature (°C)
Query: weather_temperature_celsius{city="Astana"}
Visualization: Gauge
Thresholds:
  - Blue: <0
  - Green: 0-20
  - Yellow: 21-30
  - Red: >30
```

### Panel 2: Temperature Trend (Time series)

```
Title: Temperature Over Time
Queries:
  - weather_temperature_celsius{city="Astana"} (Legend: Actual)
  - weather_feels_like_celsius{city="Astana"} (Legend: Feels Like)
Visualization: Time series
```

### Panel 3: Humidity (Gauge)

```
Title: Humidity (%)
Query: weather_humidity_percent{city="Astana"}
Visualization: Gauge
```

### Panel 4: Atmospheric Pressure (Stat)

```
Title: Pressure (hPa)
Query: weather_pressure_hpa{city="Astana"}
Visualization: Stat
```

### Panel 5: Wind Speed (Gauge)

```
Title: Wind Speed (km/h)
Query: weather_wind_speed_mps{city="Astana"} * 3.6
Visualization: Gauge
```

### Panel 6: Cloudiness (Stat)

```
Title: Cloudiness (%)
Query: weather_clouds_percent{city="Astana"}
Visualization: Stat
```

### Panel 7: Visibility (Bar chart)

```
Title: Visibility (km)
Query: weather_visibility_meters{city="Astana"} / 1000
Visualization: Bar chart
```

### Panel 8: Temperature Statistics (Table)

```
Title: Temperature Stats (Last Hour)
Queries:
  - avg_over_time(weather_temperature_celsius{city="Astana"}[1h]) (Legend: Avg)
  - max_over_time(weather_temperature_celsius{city="Astana"}[1h]) (Legend: Max)
  - min_over_time(weather_temperature_celsius{city="Astana"}[1h]) (Legend: Min)
Visualization: Table
```

### Panel 9: API Request Success Rate (Pie chart)

```
Title: API Requests Status
Queries:
  - weather_api_requests_total{status="success"} (Legend: Success)
  - weather_api_requests_total{status="error"} (Legend: Error)
Visualization: Pie chart
```

### Panel 10: Sunrise/Sunset Times (Stat)

```
Title: Time to Sunset (hours)
Query: (weather_sunset_timestamp{city="Astana"} - time()) / 3600
Visualization: Stat
Unit: hours
```

### Panel 11: Temperature Change Rate (Time series)

```
Title: Temperature Change Rate
Query: rate(weather_temperature_celsius{city="Astana"}[10m])
Visualization: Time series
```

### Panel 12: Wind Direction (Stat with Compass)

```
Title: Wind Direction (°)
Query: weather_wind_direction_degrees{city="Astana"}
Visualization: Stat
Unit: degrees
```

### Dashboard Variable:

```
Name: city
Type: Query
Query: label_values(weather_temperature_celsius, city)
```

Используй `$city` в запросах

### Alert:

```
Panel: Temperature
Condition: WHEN last() IS ABOVE 35 OR BELOW -30
For: 10m
Name: Extreme Temperature Alert
```

---

## 📤 ЭКСПОРТ ДАШБОРДОВ

### Для каждого дашборда:

1. **Dashboard settings (⚙️)** → **JSON Model**
2. **Copy to Clipboard**
3. Сохрани в файл:
   - `dashboard1_database.json`
   - `dashboard2_system.json`
   - `dashboard3_weather.json`

Или:

1. **Share (🔗)** → **Export** → **Save to file**

---

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА

Перед защитой убедись:

- [ ] Все 3 дашборда созданы
- [ ] На каждом ≥10 панелей
- [ ] Минимум 4 разных типа визуализаций
- [ ] Все PromQL запросы работают
- [ ] Глобальные фильтры настроены
- [ ] Хотя бы 1 alert на каждом дашборде
- [ ] JSON файлы экспортированы
- [ ] Данные обновляются в реальном времени

---

**Дашборды готовы! Теперь можно защищаться!** 🎉