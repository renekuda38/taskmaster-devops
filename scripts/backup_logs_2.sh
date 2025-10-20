#!/bin/bash

#######################################
# Backup & Log Rotation Script
# Author: René Kuďa
# Date: 2025-10-16
#######################################

# Nastavenie premenných
LOG_DIR="var/log/myapp"           # Adresár s logmi
BACKUP_DIR="backups"              # Kam sa uložia zálohy
LOG_FILE="logs/backup.log"        # Log súbor backup procesu
RETENTION_DAYS=7                  # Koľko dní sa držia staré zálohy

# Timestamp pre názov archívu
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="logs_backup_${TIMESTAMP}.tar.gz"

# Farby pre výpis (optional, ale pekné)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#######################################
# Funkcia: Logovanie
# Args: $1 - správa na zalogování
#######################################
log_message() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" | tee -a "$LOG_FILE"
}

#######################################
# Funkcia: Error logovanie a exit
# Args: $1 - chybová správa
#######################################
log_error() {
    local error_msg="$1"
    echo -e "${RED}[ERROR]${NC} $error_msg" >&2
    log_message "ERROR: $error_msg"
    exit 1
}

#######################################
# MAIN SCRIPT START
#######################################
log_message "=== Backup process started ==="

#######################################
# Kontrola existencie adresárov
#######################################

# Kontrola či existuje log adresár
if [[ ! -d "$LOG_DIR" ]]; then
    log_error "Log directory $LOG_DIR does not exist!"
fi

# Kontrola či sú v log adresári nejaké .log súbory
log_count=$(find "$LOG_DIR" -name "*.log" -type f | wc -l)
if [[ $log_count -eq 0 ]]; then
    log_error "No .log files found in $LOG_DIR"
fi

log_message "Found $log_count log file(s) to backup"

# Vytvor backup adresár, ak neexistuje
if [[ ! -d "$BACKUP_DIR" ]]; then
    mkdir -p "$BACKUP_DIR"
    log_message "Created backup directory: $BACKUP_DIR"
fi

# Vytvor adresár pre logy backup procesu, ak neexistuje
if [[ ! -d "$(dirname "$LOG_FILE")" ]]; then
    mkdir -p "$(dirname "$LOG_FILE")"
    log_message "Created log directory: $(dirname "$LOG_FILE")"
fi

#######################################
# Kontrola dostupného miesta na disku
#######################################

# Zisti dostupné miesto v backup adresári (v KB), do ktoreho archivoujeme logy, ktore sa ukladali do priecinku $    LOG_DIR
available_space=$(df "$BACKUP_DIR" | tail -1 | awk '{print $4}')

# Zisti veľkosť všetkých log súborov (v KB) - su to logy, ktore chceme archivovat
log_size=$(du -sk "$LOG_DIR" | cut -f1)

# Potrebujeme aspoň 2x viac miesta než majú logy (kvôli kompresii a bufferu)
required_space=$((log_size * 2))

if [[ $available_space -lt $required_space ]]; then
    log_error "Not enough disk space! Available: ${available_space}KB, Required: ${required_space}KB"
fi

log_message "Disk space check passed. Available: ${available_space}KB, Logs size: ${log_size}KB"

#######################################
# Archivovanie logov
#######################################

log_message "Creating archive: $BACKUP_NAME"

# Vytvor tar.gz archív zo všetkých .log súborov
if tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$LOG_DIR" *.log; then
    archive_size=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
    log_message "Archive created successfully: $BACKUP_NAME (size: $archive_size)"
else
    log_error "Failed to create archive!"
fi

#######################################
# Vymazanie starých záloh
#######################################

log_message "Cleaning up backups older than $RETENTION_DAYS days..."

# Nájdi a vymaž súbory staršie ako X dní
deleted_count=0
while IFS= read -r old_backup; do
    if [[ -f "$old_backup" ]]; then
        rm -f "$old_backup"
        log_message "Deleted old backup: $(basename "$old_backup")"
        ((deleted_count++))
    fi
done < <(find "$BACKUP_DIR" -name "logs_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS)

if [[ $deleted_count -eq 0 ]]; then
    log_message "No old backups to delete"
else
    log_message "Deleted $deleted_count old backup(s)"
fi

#######################################
# Vymazanie pôvodných log súborov
#######################################

log_message "Cleaning up original log files..."

# Vymaž všetky .log súbory z log adresára
if rm -f "$LOG_DIR"/*.log 2>/dev/null; then
    log_message "Original log files deleted successfully"
else
    log_message "Warning: Some log files could not be deleted"
fi

#######################################
# Finálny report
#######################################

log_message "=== Backup process completed successfully ==="
log_message "Archive: $BACKUP_DIR/$BACKUP_NAME"
log_message "Total backups in directory: $(ls -1 $BACKUP_DIR/*.tar.gz 2>/dev/null | wc -l)"

# Exit s úspešným kódom
exit 0
