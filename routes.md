# API Payloads with response -->API Documentation

# Routes

## User Routes:

### Add user & Authentications All Actors

#### URL: ```/users/signup/```

#### Body:

```json
{
    "full_name": "Rimsha Gohar",
    "email": "rimsha@example.com",
    "password": "123",
    "role": "student"
}

```

#### Returns:

```json
{
    "message": "User registered successfully.",
    "username": "wasi_gohar10",
    "token": "0e5c80563f8044e370fa12eb3eddedcf8a213ef7",
    "role": "student"
}
```
#### URL: ```/users/login/```
User Login
```json
{
    "email": "rimsha@example.com",
    "password": "123"
}

```
```json
{
    "message": "Login successful.",
    "token": "6c93a805d7f95478aff8548a671ec60d9872bb7a"
}