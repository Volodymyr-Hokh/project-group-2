# Group Project (Group 2) :shipit:


README is available in the following languages:

<a href="https://github.com/Volodymyr-Hokh/project-group-2/blob/dev/README.md">
<img src="https://em-content.zobj.net/thumbs/120/apple/354/flag-ukraine_1f1fa-1f1e6.png" alt="UA" width="40" height="40"></a>
<a href="https://github.com/Volodymyr-Hokh/project-group-2/blob/dev/README.eng.md">
<img src="https://em-content.zobj.net/thumbs/120/apple/354/flag-united-states_1f1fa-1f1f8.png" alt="EN" width="40" height="40"></a>

## :purple_circle: **Overview**

**This is a group project of the PhotoShare application for REST API, with the main functionality implemented in FAST API.**

The application is covered by modular tests for more than 90%.

The deployment of the application is done using the Render cloud service.
The project has comprehensive Swagger documentation.

## :purple_circle: **Main Functionality**

The application has the following main functionality:

* *Authentication :blue_square:*
    * JWT tokens
    * Administrator, moderator, and regular user roles
    * FastApi decorators are used to check the token and user role.

* *Working with Photos :blue_square:*

    * The main functionality of working with photos is performed using HTTP requests (POST, DELETE, PUT, GET).
    * Unique tags for the entire application that can be added under a photo (up to 5 tags).
    * Users can perform basic actions with photos allowed by the Cloudinary service.
    * Links for viewing a photo as a URL and QR-code can be created and stored on the server.
    * Administrators can perform all CRUD operations with user photos.

* *Commenting :blue_square:*

    * Under each photo, there is a block with comments.
    * The creation and editing time of the comment is stored in the database.
    * Users can edit their comments but cannot delete them. Administrators and moderators can delete comments.


## :purple_circle: ** Installation and Project Launch** 

To work with the project, you need an `.env` file with environment variables.
Create it with the following content and *replace with your values*:

```dotenv
Copy code
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

Run the following commands in the project root:

* * Start the database
```bash
docker-compose up -d
```

* *Run tests:*  

```
python -m pytest tests/filename -v
```

## :purple_circle: Swagger and Sphinx Documentation

* [Swagger](https://photo-app-of9h.onrender.com/swagger)

* [Sphinx](https://photo-app-of9h.onrender.com/docs)

## :purple_circle: Project Authors

* Team Lead [Volodymyr](https://github.com/Volodymyr-Hokh)
* Scrum Master [Viktoriia](https://github.com/Nilinz)
* Developer [Danil](https://github.com/Pelmenoff)
* Developer [Vladyslav](https://github.com/Vlad96Kir)