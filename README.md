# Backend Challenge - Patient Registration

This is my submission to the provided challenge.

It uses FastAPI, SQLModel as ORM, a MySql database, and Celery (with Redis) for background tasks.

---

## Docker Development Environment

It consists of two docker images:
- mysql: for the database server
- fastapi: for the application

Initialize with:

```
docker compose up --build
```

The mysql image will boot first, and the fastapi image should boot once the mysql db is ready the receive connections.

If mysql takes too long to initialize it may be marked as unhealthy and shut down. I tried to be conservative with the timeout so it shouldn't happen, but if it does, it will probably be on the first boot (because all the database is being initialized), so after a reboot everything should be fine. If the problem persists more time can be provided by modifying `docker-compose.yml`, either by adding retries or by making the interval longer.

The api is bound to `localhost:8000`. The fastapi image holds all code in `/code` directory.

I left a VSCode debugger configuration (`.vscode/launcher.json`) to be able to use stops and step through the code running in the container, which proved very useful.

> [!WARNING]
> The file `init.sh` is used internally by the fastapi container to initialize all the services.
> It is **not** intended to initialize the dev environment (perhaps it should be placed elsewhere to avoid confusion).

---

## Testing

The api was manually tested with various valid and invalid inputs by using the helpful documentation page FastAPI puts on `localhost:8000/docs`.

I wanted to write some automatic tests but I ran out of time.

---

## Background Tasks

I couldn't make the BackgroundTasks feature of FastAPI work. Neither would it work by creating tasks manually with `asyncio`. In both cases the tasks would not execute after being created, they would wait until the FastAPI event loop stops (which happens, for example, when a file is saved and the server reloads).

After looking for a different solution, Celery did the job. I probably would be better to have Redis running on a third image, but I thought it would have been overkill for this challenge.

---

## Email

Sending email from a background task was simulated by sleeping the worker thread for a second. I would have liked to demonstrate usage of `smtplib`, but for it to work it would have required either running a custom email server or using some mail service.

I'd have liked to try to set up an email server. I planned to try it as a stretch goal, but in the end I did not have time for it.

---

## Image handling

Image reception is handled by reading in chunks, to avoid blocking the main thread.

For validation, `pillow` is used to verify that the file received is a valid image file. Currently this is done synchronously, perhaps it would be better to do so asynchronously.

While the file format and validity are verified, the file contents are not: that is, the app does not check if the image is of a real id. There are services for that, and depending on the needs of the project, this could be very important.
