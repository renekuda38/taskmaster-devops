# ==========================================
# STAGE 1: BUILD STAGE (build prostredie)
# ==========================================
FROM python:3.11-alpine AS builder

# Nastavíme working directory
WORKDIR /app

# Skopírujeme requirements.txt
COPY requirements.txt .

# Nainštalujeme dependencies do default lokácie
# Pip automaticky nainštaluje do /usr/local/lib/python3.11/site-packages/
RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# STAGE 2: RUNTIME STAGE (finálny image)
# ==========================================
FROM python:3.11-alpine

# Vytvoríme non-root usera (security best practice)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Nastavíme working directory
WORKDIR /app

# Skopírujeme nainštalované dependencies z build stage
# --from=builder znamená "z predchádzajúceho stage"
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Skopírujeme Python aplikáciu
COPY github_api_client.py .

# Zmeníme vlastníctvo súborov na non-root usera
RUN chown -R appuser:appgroup /app

# Prepneme na non-root usera
USER appuser

# Spustíme aplikáciu
CMD ["python", "github_api_client.py"]
