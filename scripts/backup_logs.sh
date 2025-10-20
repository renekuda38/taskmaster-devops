#!/bin/bash

#######################################
# Backup & Log Rotation Script
# Author: René Kuda
# Date: 2025-10-19
######################################

LOGS_DIR="var/log/myapp"				# logy aplikacii
BACKUPS_DIR="backups"	      				# backupy logov
BACKUPING_LOGS_FILE="logs/backup.log"    		# logy backup procesu
RETENTION_DAYS=7             				# po akom case sa maju stare zalohy logov vymazat

TIME_STAMP=$(date +"%Y%m%d_%H%M%S")			# cas vytvorenia backup archivu
BACKUP_ARCHIVE_NAME="logs_backup_${TIME_STAMP}.tar.gz"	# meno archivu s backupnutymi logmi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

function log_message()
{
	local message="$1"
	local time_stamp=$(date +"%Y-%m-%d %H:%M:%S")
	local backuping_logs_dir="$(dirname "${BACKUPING_LOGS_FILE}")"
	if [[ ! -d "${backuping_logs_dir}" ]]; then
		if ! mkdir -p "${backuping_logs_dir}" 2>/dev/null; then
			echo "directory ${backuping_logs_dir} cannot be created" >&2
			exit 1 
		fi
		# inforamative that /log dir has been createds
		echo "INFO - diretory ${backuping_logs_dir} has been created"	
	fi
	echo "${time_stamp} -> ${message}" | tee -a "${BACKUPING_LOGS_FILE}"
}

function log_error()
{
	local error_message="${1}"
	echo -e "${RED}[ERROR]${NC} ${error_message}" >&2
	log_message "ERROR: ${error_message}"
	exit 1
}

# test
log_message "=== Backup process started ==="

# Tu začni písať kontroly...

# 1. Kontrola log adresára
if [[ ! -d "$LOGS_DIR" ]]; then
	log_error "directory ${LOGS_DIR} does not exists, nothing to backup"
fi

# 2. Počet log súborov
logs_count=$(find "${LOGS_DIR}" -name "*.log" -type f | wc -l)

if [[ "${logs_count}" -eq 0  ]]; then
	log_error "there is no files in ${LOGS_DIR}"
fi

log_message "found ${logs_count} log file(s) to backup"

# 3. Vytvorenie backup adresára
if [[ ! -d "${BACKUPS_DIR}" ]]; then
	mkdir -p "${BACKUPS_DIR}"
	log_message "directory ${BACKUPS_DIR} has been created"
fi


available_space="$(df "${BACKUPS_DIR}" | tail -1 | awk '{print $4}')"

log_size="$(du -sk "${LOGS_DIR}" | cut -f1)"

required_space=$(("${log_size}" * 2))

if [[ "${required_space}" -gt "${available_space}" ]]; then
	log_error "no enough disk space! available: ${available_space}, required: ${required_space}"
fi

log_message "disk space check passed. available: ${available_space}, required: ${required_space}"


if tar -czf "${BACKUPS_DIR}/${BACKUP_ARCHIVE_NAME}" -C "${LOGS_DIR}" .; then
	archive_size="$(du -h "${BACKUPS_DIR}/${BACKUP_ARCHIVE_NAME}" | cut -f1)"
	log_message "archive created successfully. ${BACKUP_ARCHIVE_NAME} (size: ${archive_size})"
else
	log_error "failed to create an archive"
fi

log_message "Cleaning up backups older than $RETENTION_DAYS days..."

# Inicializuj počítadlo
deleted_count=0

# While loop s find príkazom
# - Pre každý nájdený súbor:
#   - Skontroluj či existuje
#   - Vymaž ho
#   - Zaloguj ktorý bol vymazaný (basename)
#   - Zvýš počítadlo

while IFS= read -r old_backup; do
	if [[ -f "${old_backup}" ]]; then
		rm -rf "${old_backup}"
		log_message "deleted old backup: $(basename "${old_backup}")"
		((deleted_count++))
	fi
done < <(find "${BACKUPS_DIR}" -name "logs_backup_*.tar.gz" -type f -mtime +"${RETENTION_DAYS}")

if [[ ${deleted_count} -eq 0 ]]; then
	log_message "No old backups to delete"
else
	log_message "deleted ${deleted_count} old backup(s)"
fi

log_message "Cleaning up original log files..."

# Vymaž všetky .log súbory z $LOGS_DIR
# - Použi rm s správnymi prepínačmi
# - Presmeruj chyby do /dev/null (2>/dev/null)
# - Skontroluj exit code
# - Ak OK → zaloguj úspech
# - Ak nie → zaloguj warning (nie error! už máme archív)

if rm -f "${LOGS_DIR}/*.log" 2>/dev/null; then
	log_message "Original log files deleted successfully"
else
	log_message "Warning - some log files could not be deleted"
fi

log_message "=== Backup process completed successfully ==="
log_message "--- ARCHIVE NAME: ${BACKUP_ARCHIVE_NAME} ---"
log_message "--- total files in backup directory: $(ls -1 ${BACKUPS_DIR}/*.tar.gz 2>/dev/null | wc -l)"

exit 0
