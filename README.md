# account_backend
Приложение для управления счетами пользователей (DRF)

Для деплоя наберите sudo ./start_deploy.sh

Api содерждит точки:
/admin
/api/accounts/  (CRUD) - идентификация по uuid
/api/add/       (PUT)
/api/status/    (GET)
/api/ping       (GET)
/api/substract/ (PUT)
api/hold/       (PUT)  - для вычитания холдов

Удаление холдов выполяется через запуск скрипта cron_job.py в кроне контейнера. 
Эту задачу можно было в реальном окружении решить через расширение крон в Postgres, (если используем Postgres),
либо через cronjob в Kubernets.


