# Wallapop Telegram Bot


---

## Configuración

1. **Clonar el repositorio:**
```
git clone https://github.com/polaupa/wallapop-scrap.git
cd wallapop-scrap
```

2. **Crear fichero .env y configurar los campos:**

```
cp .env.example .env
```
Ejemplo:
```
TELEGRAM_TOKEN=TOKEN DE TU BOT DE TELEGRAM
MIN_PRICE=10 # En Euro
MAX_PRICE=30 # En Euro
ITEM=Mando Nintendo Switch # Nombre de tu búsqueda
REFRESH_TIME=120 # Tiempo entre notificaciones (en segundos)
```

Para crear tu bot de Telegram y obtener el token puedes mirar la [documentación de Telegram oficial](https://core.telegram.org/bots/tutorial)

3. **Despliegue con Docker:**
```
docker-compose up --build -d
```

Si se quiere hacer algún cambio en el fichero `.env`, solo hay que desplegar de nuevo el contenedor con el mismo comando.

4. **Arrancar el bot:**

En el chat del bot que has creado, hay que escribir `/start` para empezar a recibir las notificaciones.

5. **Parar el bot:**
```
docker kill wallapop-wallapop-1
docker rm wallapop-wallapop-1
```

---

## License

MIT
