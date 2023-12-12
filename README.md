# Груповий проект (група 2) :shipit:

## :purple_circle: **Огляд**

***Це груповий проект застосунку "*" для REST API, основний функціонал якого виконаний на FAST API.***

Застосунок покритий модульними тестами більш ніж на 90%.

Деплой застосунку виконаний за домогою хмарного сервісу - * "*" *
Проект має повну Swagger документацію.

## :purple_circle: **Основний функціонал**

Застосунок має такий основний функціонал:
* *Аутентифікація :blue_square:*
    * JWT токени
    * ролі адміністратора, модератора та звичайного користувача
    * для перевірки токена і ролі користувача використовуються декоратори FastApi

* *Робота зі світлинами :blue_square:*
    * Основний функціонал роботи зі світлинами виконується за допомогою HTTP реквестів (POST, DELETE, PUT, GET)
    * Унікальні для всього застосунку теги, які додаються під світлину (до 5 тегів)
    * Користувачі можуть виконувати базові дії зі світлинами, які дозволяє сервіс Cloudinary
    * Можна створювати посилання для перегляду світлини у вигляді URL та QR-code, які зберігаються на сервері
    * Адміністратори можуть робити всі CRUD операції зі світлинами користувачів

* *Коментування :blue_square:*
    * Під кожною світлиною, є блок з коментарями. 
    * Для коментарів зберігається час створення та час редагування коментаря в базі даних.
    * Користувач може редагувати свій коментар, але не видаляти. Адміністратори та модератори можуть видаляти коментарі


## :purple_circle: **Встановлення та запуск проекту** 

Для роботи проекта необхідний файл `.env` зі змінними оточення.
Створіть його з таким вмістом і *підставте свої значення*:

```dotenv
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTRGES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

SECRET_KEY=
ALGORITHM=

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=

REDIS_HOST=
REDIS=

CLOUDINARY_NAME = 
CLOUDINARY_API_KEY = 
CLOUDINARY_API_SECRET = 
```

Виконайте наступні команди в корені проекту:

* *Запуск бази даних*
```bash
docker-compose up -d
```


* *Запуск тестів:*  
```
python -m pytest tests/назва_файлу -v
```


##  :purple_circle: **Автори проекту** 

* Team Lead [Volodymyr](https://github.com/Volodymyr-Hokh)
* Scrum Master [Viktoriia](https://github.com/Nilinz)
* Developer [Danil](https://github.com/Pelmenoff)
* Developer [Vladyslav](https://github.com/Vlad96Kir)
