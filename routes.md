# API Payloads with response -->API Documentation
# Routes
## Add user & Authentications All Actors
### URL: ```/users/signup/```
#### Method : POST
#### Body:
```json
{
    "full_name": "Rimsha Gohar",
    "email": "rimsha@example.com",
    "password": "123",
    "role": "student"
}

```
#### Response :

```json
{
    "message": "User registered successfully.",
    "username": "wasi_gohar10",
    "token": "0e5c80563f8044e370fa12eb3eddedcf8a213ef7",
    "role": "student"
}
```
## User Login
#### URL: ```/users/login/```
#### Method : POST
```json
{
    "email": "rimsha@example.com",
    "password": "123"
}

```
#### Response :
```json
{
    "message": "Login successful.",
    "token": "6c93a805d7f95478aff8548a671ec60d9872bb7a"
}
```
## Student CURD
## Get all  students
### Method : GET
### URL : ```students/student/profile```

## Get By ID student
### URL : ```students/student/profile/<int:id>/```
#### Response :
```json
{
    "id": 5,
    "first_name": "Rimsha",
    "last_name": "Gohar",
    "email": "rimsha@example.com",
    "role": "student"
}
```
## Update Student detail by student id
### URL: ```students/student/profile/<int:id>/```
##### Method: PUT
```json
{
  "old_password": "123",
  "first_name": "New First Name",
  "last_name": "New Last Name",
  "password": "1234"
}
```
## Delete Student by student id
### URL: ```students/student/profile/<int:id>/```
##### Method: DELETE

# Teachers : Routes
## Add Teacher Profile
### URL: ```teacher/instructor-profile/create/```
##### Method: POST
#### Body
```json
{
    "user_id" : "<user:id>",
    "bio": "An experienced educator with over 10 years of teaching experience.",
    "degrees": "PhD in Education, MSc in Mathematics",
    "teaching_experience": 10,
    "specialization": "Mathematics, Physics",
    "teaching_history": "Taught at XYZ University, ABC High School",
}
```


## Get all Teacher Profile with user ID
### URL: ```/teacher/all/profile/```
##### Method: GET
#### Body


## Get a specific Teacher Profile with user ID
### URL: ```/teacher/all/profile/<int:user_id>```
##### Method: GET
#### Body

## Update Teacher Profile
### URL: ```teacher/instructor-profile/create/```
##### Method: PUT
#### Body
```json
{
    "bio": "demo update update",
    "degrees": "PhD in Education, MSc in Mathematics help help",
    "teaching_experience": 22,
    "specialization": "Mathematics, Physics",
    "teaching_history": "Taught at BBC University, ABC High School"
}
```

## Upload Teacher Profile Image
### URL: ```teacher//upload-profile-picture/```
##### Method: POST
#### Body
```json
{
    "user_id": "int",
    "profile_picture":"file"
}
```