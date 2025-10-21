#! /bin/bash
#
#
# skript: monitoring systemu
#
# autor: rene martin kuda
#
# datum: 20.9.2025
#
##############################


OUTPUT_FILE="monitoring/health_check.json"
TIMESTAMP="$(date +"%Y-%m-%dT%H:%M:%S")"
HOSTNAME="$(hostname)"


for empty_cpu_idle in {1..10}; 
do
	cpu_idle="$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | sed 's/id,//')"
	if [[ -n "${cpu_idle}" ]]; then
		break
	fi
done

if [[ -z "${cpu_idle}" ]]; then
	echo "cannot get CPU IDLE % info"
        exit 1
fi

cpu_usage="$(echo "100 - $cpu_idle" | bc)"

# Test výpis
echo "Timestamp: $TIMESTAMP"
echo "Hostname: $HOSTNAME"
echo "CPU idle: ${cpu_idle}%"
echo "CPU usage: ${cpu_usage}%"

# Memory usage
mem_total=$(free -m | grep "Mem:" | awk '{print $2}')
mem_used=$(free -m | grep "Mem:" | awk '{print $3}')

# Vypočítaj percentá
mem_usage=$(echo "scale=2; ${mem_used} / ${mem_total} * 100" | bc)

# Výpis
echo "Memory: ${mem_used}MB / ${mem_total}MB (${mem_usage}%)"

declare -A disk_usage

# Loop cez všetky /dev/ filesystémy
while read -r line; do
    mountpoint=$(echo "$line" | awk '{print $6}')
    usage=$(echo "$line" | awk '{print $5}' | sed 's/%//')

    disk_usage[$mountpoint]=$usage
done < <(df -h | grep "^/dev/")

# Vypíš
for mount in "${!disk_usage[@]}"; do
	echo "Disk usage $mount: ${disk_usage[$mount]}%"
done

SERVICES=("sshd" "nginx")

declare -A service_status

for service in "${SERVICES[@]}"; do
	if systemctl is-active "${service}" &>/dev/null; then
		service_status[$service]="running"
	else
		service_status[$service]="stopped"
	fi
done

for service in "${!service_status[@]}"; do
	echo "Service ${service} ${service_status[${service}]}"
done

health_status="ok"

if (( $(echo "${mem_usage} > 90" | bc -l)  )); then
        health_status="critical"
elif (( $(echo "${mem_usage} > 70" | bc -l)  )); then
        [[ "${health_status}" != "critical" ]] && health_status="warning"
fi

if (( $(echo "${cpu_usage} > 90" | bc -l)  )); then
        health_status="critical"
elif (( $(echo "${cpu_usage} > 70" | bc -l)  )); then
        [[ "${health_status}" != "critical" ]] && health_status="warning"
fi

for mount in "${!disk_usage[@]}"; do
        usage="${disk_usage[$mount]}"
        if (( $(echo "${usage} > 90" | bc -l)  )); then
                health_status="critical"
        elif (( $(echo "${usage} > 80" | bc -l)  )); then
                [[ "${health_status}" != "critical" ]] && health_status="warning"
        fi
done

if [[ "${service_status[sshd]}" == "stopped" ]]; then
        health_status="critical"
fi


echo "Health check completed"
echo "Health status: ${health_status}"


PROJECT_DIR="/home/rene/taskmaster-devops"
OUTPUT_FILE="$PROJECT_DIR/monitoring/health_check.json"


cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$HOSTNAME",
  "cpu_usage": $cpu_usage,
  "memory_usage": $mem_usage,
  "disk_usage": {
EOF

disk_count="${#disk_usage[@]}"
current=0

for mount in "${!disk_usage[@]}"; do
	current=$((current + 1))
	usage="${disk_usage[$mount]}"

	if [[ "${current}" -eq "${disk_count}"  ]]; then
		echo "    \"$mount\": $usage" >> "$OUTPUT_FILE"
		echo "  }," >> "${OUTPUT_FILE}"
	else
		echo "    \"$mount\": $usage," >> "$OUTPUT_FILE"
	fi
done

echo "  \"services\": {" >> $OUTPUT_FILE

services_count="${#service_status[@]}"
current=0
for service in "${!service_status[@]}"; do
	current=$((current + 1))
	health="${service_status[$service]}"

	if [[ "${current}" -eq "${services_count}" ]]; then
		echo "    \"$service\": \"$health\"" >> $OUTPUT_FILE
		echo "  }," >> "${OUTPUT_FILE}"
	else
		echo "    \"$service\": \"$health\"," >> $OUTPUT_FILE
	fi
done

echo "  \"status\": \"${health_status}\"" >> $OUTPUT_FILE
echo "}" >> $OUTPUT_FILE
