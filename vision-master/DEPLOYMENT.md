# 🚀 Deployment em Produção - AgroVision AI

Guia completo para colocar AgroVision AI em produção.

---

## 📋 Pré-requisitos

- Servidor Linux (recomendado Ubuntu 22.04 LTS)
- Docker e Docker Compose instalados
- Domínio configurado (ex: agrovision.seu-dominio.com)
- SSL/TLS (gerado via Let's Encrypt)
- Mínimo 4GB RAM, 2 CPU cores
- Câmera IP ou stream público autorizado

---

## 🐳 Option 1: Docker Compose (Recomendado)

### 1. Clonar/Preparar Projeto

```bash
cd /opt/agrovision
git clone seu-repositorio . # ou copiar arquivos

# Ou já extrair do ZIP
unzip agrovision_ia.zip -d /opt/agrovision
```

### 2. Criar Arquivos de Configuração

**.env.production:**
```bash
cat > .env.production << EOF
OLLAMA_URL=http://ollama:11434/api/chat
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=120
OLLAMA_KEEP_ALIVE=30m
AGENT_EVENT_LIMIT=12
CAMERA_SOURCE=https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8
CAMERA_RECONNECT_SECONDS=5
EOF
```

### 3. Gerar Certificados SSL

```bash
# Criar diretório para SSL
mkdir -p ssl

# Usando Let's Encrypt com certbot
sudo apt-get install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone \
  -d agrovision.seu-dominio.com \
  --email seu-email@example.com

# Copiar para pasta do projeto
sudo cp /etc/letsencrypt/live/agrovision.seu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/agrovision.seu-dominio.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*
```

### 4. Rodar Docker Compose

```bash
# Verificar arquivo
cat docker-compose.yml

# Iniciar serviços
docker-compose up -d

# Monitorar logs
docker-compose logs -f agrovision
docker-compose logs -f ollama

# Verificar status
docker-compose ps
```

### 5. Verificar Saúde

```bash
# Health check
curl http://localhost:8000/health

# No navegador
https://agrovision.seu-dominio.com
```

### 6. Atualizar DNS

Apontar domínio para IP do servidor em seu registrador de domínios.

---

## 🔄 Atualizações e Manutenção

### Atualizar Código

```bash
cd /opt/agrovision

# Pull código novo
git pull origin main

# Reconstruir imagem
docker-compose build

# Reiniciar serviços
docker-compose up -d
```

### Visualizar Logs

```bash
# Logs em tempo real
docker-compose logs -f agrovision

# Últimas 100 linhas
docker-compose logs --tail=100 agrovision

# Salvar logs
docker-compose logs agrovision > logs.txt
```

### Limpar Cache/Dados

```bash
# Remove containers (mantém volumes)
docker-compose down

# Remove tudo (incluindo dados!)
docker-compose down -v

# Limpar imagens não usadas
docker image prune -a

# Limpar volumes não usados
docker volume prune
```

---

## 📊 Monitoramento

### Recursos de Container

```bash
# CPU e memória em tempo real
docker stats

# Histórico detalhado
docker container stats --no-stream
```

### Banco de Dados

```bash
# Acessar container
docker exec -it agrovision-app bash

# Inspecionar BD
sqlite3 detections.db
> SELECT COUNT(*) FROM events;
> SELECT * FROM events ORDER BY event_time DESC LIMIT 5;

# Limpar eventos antigos
# DELETE FROM events WHERE event_time < datetime('now', '-30 days');
```

### Verificar Espaço em Disco

```bash
df -h
du -sh /opt/agrovision
```

---

## 🔐 Segurança

### 1. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Senhas e Credenciais

**Nunca** commit `.env` com senhas reais no Git:

```bash
# Adicionar ao .gitignore
echo ".env.production" >> .gitignore
echo "ssl/" >> .gitignore
```

### 3. HTTPS/SSL Automático

Certificados Let's Encrypt expiram em 90 dias:

```bash
# Renovação automática (cron)
sudo certbot renew --quiet

# Ou manual
sudo certbot renew

# Copiar novo certificado
sudo cp /etc/letsencrypt/live/agrovision.seu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/agrovision.seu-dominio.com/privkey.pem ssl/key.pem
```

### 4. Rate Limiting

Já configurado em `nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=chat:10m rate=5r/s;
```

### 5. Backup Regular

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/agrovision"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Backup do banco
docker exec agrovision-app tar czf - detections.db | \
  gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup das imagens capturadas
docker exec agrovision-app tar czf - static/captures | \
  gzip > $BACKUP_DIR/captures_$DATE.tar.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

Agendar com cron:

```bash
# Executar backup todos os dias às 02:00
crontab -e
# Adicionar: 0 2 * * * /opt/agrovision/backup.sh
```

---

## 🐛 Troubleshooting em Produção

### Container não inicia

```bash
docker-compose logs agrovision
# Ver mensagem de erro

# Verificar dependências
docker-compose up --abort-on-container-exit

# Recriar container
docker-compose up -d --force-recreate agrovision
```

### Ollama não responde

```bash
# Verificar se está rodando
docker ps | grep ollama

# Ver logs
docker-compose logs ollama

# Reiniciar
docker-compose restart ollama

# Verificar conexão
docker exec agrovision-app curl http://ollama:11434/api/tags
```

### Falta de memória

```bash
# Ver consumo atual
docker stats

# Aumentar limite em docker-compose.yml
# services:
#   agrovision:
#     mem_limit: 4g
#     mem_reservation: 2g

docker-compose up -d
```

### SSL/HTTPS com erro

```bash
# Verificar certificado
openssl x509 -in ssl/cert.pem -text -noout

# Testar SSL
curl -vI https://agrovision.seu-dominio.com

# Renovar manualmente
sudo certbot renew --force-renewal
```

---

## 📈 Performance em Produção

### 1. Aumentar Replicas

```yaml
# docker-compose.yml
services:
  agrovision:
    deploy:
      replicas: 3
```

Com Nginx balanceando carga automaticamente.

### 2. Cache Redis (Opcional)

```bash
docker run -d --name redis \
  -p 6379:6379 \
  redis:alpine
```

### 3. CDN para Static Files

Servir `/static` por CloudFront ou similar:

```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 4. Compressão Gzip

Já ativada em `nginx.conf`.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/agrovision
            git pull origin main
            docker-compose build
            docker-compose up -d
```

---

## 📊 Métricas Recomendadas

Monitor com Prometheus + Grafana:

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

---

## ✅ Checklist de Deployment

- [ ] Domínio apontando para servidor
- [ ] SSL/TLS configurado e válido
- [ ] Docker Compose rodando
- [ ] Ollama respondendo
- [ ] YOLO detectando
- [ ] Banco de dados criado
- [ ] Backup automatizado
- [ ] Logs centralizados
- [ ] Monitoramento ativo
- [ ] Rate limiting configurado
- [ ] Firewall restritivo
- [ ] Senha admin alterada

---

## 🚨 Emergency Procedures

### Restorerom Backup

```bash
# Parar aplicação
docker-compose down

# Restaurar BD
docker exec agrovision-app tar xzf /backups/db_YYYY-MM-DD.sql.gz

# Reiniciar
docker-compose up -d
```

### Rollback Versão

```bash
git checkout v1.0.0
docker-compose build
docker-compose up -d
```

### Modo Manutenção

```nginx
# nginx.conf
location / {
    return 503;
}

location = /50x.html {
    root /usr/share/nginx/html;
}
```

---

Seu AgroVision AI está pronto para produção! 🎉

