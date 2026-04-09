### Docker
docker exec -it saas_backend_db psql -U backenduser -d saas_backend
\dt

### Alembic 
alembic revision --autogenerate -m "add uuid defaults"
alembic upgrade head