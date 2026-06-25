# Django-File-Manager

This a file manager project created by using Django and template rendering approach

## Configurations

- Customized user and profile
- Uploading images and videos
- Validation for uploaded files (format & size)
- Creating new folders
- Using nested structure for your files and folders
- Search through your files and folders
- Deleting files and folders
- Up and running Celery & Redis
- Customized logging
- Customized caching based on Redis
- smtp4dev development mailing service

### Project Setup

create a `.env` file from `.env.example` and fill it with your own values,
then run below commands:

```sh
docker compose up -d
docker compose exec backend sh -c "python manage.py migrate"
```

This will set you up for using this project.

### Creating a super-user

```sh
docker compose exec backend sh -c "python manage.py createsuperuser"
```

By creating super-user you can login with the super-user credentials and also access the admin-panel.

### For running tests

```sh
docker compose exec backend sh -c "pytest ."
```

You test the functionality and performance of the project by using created tests and also adding your tests as well.
