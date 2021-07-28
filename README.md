# Flask App

A RESTful API with JWT user authorization to be used for creating, taking and viewing surveys.

### Bonus feature implemented:
  - Image thumbnail generation endpoint

### Important Python Libraries Used

- Flask
- Pillow
- sqlite3
- JWT

### Installation
 Run ```pip install -r requirements.txt``` to install required dependencies.

### Methods used
- #### create()
    - Usage: /survey/create
    - Method: POST
    - Function: Used to create survey
    - Sample:
        ```json
        {
            "name": "College students survey",
            "questions": [
                {
                    "qid": 1,
                    "qbody": "Are you a CompSci Student?"
                },
                {
                    "qid": 2,
                    "qbody": "Do you own a bike?"
                }
            ]
        }
        ```
    - Respone: 
        ```json
        {
            "OK": "Survey 'College students survey' created"
        }
        ```
- #### take(survey_id)
    - Usage: /survey/take/<survey_id>
    - Method: POST
    - Function: Used to take a survey
    - Sample: assume /survey/take/1
        ```json
        {
            "qid": 1,
            "answer": "yes"
        }
        ```
    - Response:
        ```json
        {
            "OK": "Question 1 answered"
        }
        ```
- #### view()
    - Usage: /survey
    - Method: GET
    - Function: Used to view all surveys
    - Output: 
        ```json
        { "":
            [
                "Survey: College students survey",
                "Question: Are you a CompSci student?",
                "Answer: yes",
                "------------------",
                "Question: Do you own a bike?",
                "Answer: Not answered",
                "------------------"
            ]
        }
        ```
- #### login()
    - Usage: /login
    - Method: POST
    - Function: Used to login and get JWT
    - Sample:
        ```json
        {
            "username": "user",
            "password": "mypass"
        }
        ```
    - Response:
        ```json
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJwYXNzd29yZCI6Im15cGFzcyJ9.Tal2QcuQ_OST1KbZA12W6oyBs3ojksGiUozU-u0gxrs"
        }
        ```
- #### thumbnail(image_url)
    - Usage: /thumbnail/<impage_url>
    - Method: GET
    - Function: Downloads image from the url, resizes it to 50x50 pixel image, stores it locally
    - Output: creates image.extention(Original Image) and resized.extention(Resized Image) in current directory 
        ```json
        {
            "OK": "Image successfully resized"
        }
        ```
### Usage
- #### Make sure value of header Content-Type is application/json
- #### Store token value in 'custom-token-header'
Use postman (or similar application) and start with ```/login``` to generate a token
After copying token and adding it as a value of 'custom-token-header', use the application as described in this file