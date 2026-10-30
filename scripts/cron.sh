#!/bin/sh
# Roda os mesmos jobs do CRONJOBS (morea_ds/settings.py), sem precisar do cron:
#   a cada hora cheia: app.data_processing.run
#   às 3h (UTC):       app.graphs.generateAllMotes24hRaw
# O settings.py aponta o job horário para "hourlyDataProcessing", que não existe; o certo é "run".

run_job() {
    python manage.py shell -c "$1" || echo "job falhou: $1"
}

while true; do
    sleep $((3600 - $(date +%s) % 3600))
    run_job "from app.data_processing import run; run()"
    if [ "$(date +%H)" = "03" ]; then
        run_job "from app.graphs import generateAllMotes24hRaw; generateAllMotes24hRaw()"
    fi
done
