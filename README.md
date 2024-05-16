[![DUB](https://img.shields.io/dub/l/vibe-d.svg)]()
[![PyPI](https://img.shields.io/pypi/v/nine.svg)]()
[![Build Status](https://dev.azure.com/dannyongesa/ussd%20python%20demo/_apis/build/status/Piusdan.USSD-Python-Demo?branchName=master)](https://dev.azure.com/dannyongesa/ussd%20python%20demo/_build/latest?definitionId=2&branchName=master)

# Setting Up a USSD Service for an LPG Company
#### A step-by-step guide

- Setting up the logic for USSD is easy with the [Africa's Talking API](docs.africastalking.com/ussd). This is a guide to how to use the code provided on this [repository](https://github.com/Masumadu/fastapi-ussd-application) to create a USSD that allows users to get registered and then access a menu of the following services:

| USSD APP Features                   |
|:------------------------------------|
| Make a deposit into one's account   |
| Request to check order status       |
| Check one's account balance details |
| Request to contact customer care    |

----

## INSTALLATION AND GUIDE

1. clone/download the project into the directory of your choice

1. Create a .env file on your root directory

        $ cp .env.example .env

Be sure to substitute the example variables with your credentials

#### Docker

- To install using docker, run

        $ docker-compose up

    This will start your application on port 8000

#### Using a virtual environment

1. Create a virtual environment

          $ python3 -m venv venv
          $ . venv/bin/activate

1. Install the project's dependancies

        $ poetry install --no-root

1. Initialise your database

        $ alembic upgrade head

1. Launch application

        $ uvicorn app.asgi:app --port 8000

1. Head to https://localhost:8000/ussd/docs

- You need to set up on the sandbox and [create](https://sandbox.africastalking.com/ussd/createchannel) a USSD channel that you will use to test by dialing into it via our [simulator](https://simulator.africastalking.com:1517/).

- Assuming that you are doing your development on a localhost, you have to expose your application living in the webroot of your localhost to the internet via a tunneling application like [Ngrok](https://ngrok.com/). Otherwise, if your server has a public IP, you are good to go! Your URL callback for this demo will become:
 http://<your ip address>/ussd/callback

- This application has been developed on an Ubuntu 20.04LTS. Courtesy of Ngrok, the url becomes: https://8e49-196-10-215-6.ngrok-free.app (instead of http://localhost).
(Create your own which will be different.)

- The webhook or callback to this application therefore becomes:
https://8e49-196-10-215-6.ngrok-free.app/ussd/callback.
To allow the application to talk to the Africa's Talking USSD gateway, this callback URL is placed in the dashboard, [under ussd callbacks here](https://account.africastalking.com/ussd/callback).

- Finally, this application works with a connection to postgres database.


| Field       |    Type     | Null | Key | Default |            Extra |
|-------------|:-----------:|-----:|----:|--------:|-----------------:|
| id          |   int(6)    |   NO |     |    NULL |                  |
| first_name  | varchar(30) |  YES |     |    NULL |                  |
| last_name   | varchar(20) |  YES |     |    NULL |                  |
| phone       | varchar(30) |  YES |     |    NULL |                  |
| address     | varchar(30) |  YES |     |    NULL |                  |
| is_verified |   boolean   |   NO |     |   False |                  |

- The application uses redis for session management. User sessions are stored as key value pairs in redis.


## Features on the Services List
This USSD application has the following user journey.

- The user dials the ussd code - something like `*384*303#`

- The application checks if the user is registered or not. If the user is registered, the services menu is served.

- In case the user is not registered, the application prompts the user for their name and city (with validations), before successfully registering users.

## Code walkthrough
- The applications entrypoint is at `app/api/api_v1/endpoints/ussd_views.py`
```python
    #1. This code only runs after a post request from AT
    @ussd_router.post("/callback")
    async def callback(request: Request):
    """Handles post call back from AT"""
```
Import all the necessary scripts to run this application

```python
    # 2. Import all necessary modules
    from app.services import RedisService
    from .account_controller import AccountController
    from .base_menu_controller import BaseMenu
    from .customer_care_controller import CustomerCareController
    from .deposit_controller import DepositController
    from .order_controller import OrderController
    from .registeration_controller import RegistrationController

```

Receive the HTTP POST from AT. `app/utils/util.py`

We will use a middleware that hooks on to the application request, to query and initialize session metadata stored in redis.

```python
    # 3. get data from ATs post payload
    session_id = form.get("sessionId", "")
    phone_number = form.get("phoneNumber")
    text = form.get("text")
```

The AT USSD gateway keeps chaining the user response. We want to grab the latest input from a string like 1*1*2
```python
    text_array = text.split("*") if text else [""]
    user_input = text_array[-1]
```

Interactions with the user can be managed using the received sessionId and a level management process that your application implements as follows.

- The USSD session has a set time limit(20-180 secs based on provider) under which the sessionId does not change. Using this sessionId, it is easy to navigate your user across the USSD menus by graduating their level(menu step) so that you dont serve them the same menu or lose track of where the user is.
- Query redis for the user's session level using the sessionID as the key. If this exists, the user is returning and they therefore have a stored level. Grab that level and serve that user the right menu. Otherwise, serve the user the home menu.
```python
	# 4. Query session metadata from redis or initialize a new session for this user if the session does not exist
        # get session
        session = self.get(session_id)
        if not session:
            session = {
                "phone": phone_number,
                "session_id": session_id,
                "previous_inputs": text_array,
                "current_input": user_input,
            }
            self.set(session_id, json.dumps(session))
        else:
            session = json.loads(session)
            session["previous_inputs"] = text_array
            session["current_input"] = user_input
            self.set(session_id, json.dumps(session))
        request.state.session_id = session_id
        request.state.phone = phone_number
        response = await call_next(request)
        return response
```

Before serving the menu, check if the incoming phone number request belongs to a registered user(sort of a login). If they are registered, they can access the menu, otherwise, they should first register.

`app/ussd/views.py`
```python
	# 5. Check if the user is in the db
        def start(self, session_id, user):
            if not user:
              return self.registration_controller.start(session_id=session_id)
            elif user and not user.is_verified:
              return self.registration_controller.start(
                  session_id=session_id, handler="_review"
              )
            return self.execute(session_id, user.first_name)
```

If the user is available and all their mandatory fields are complete, then the application switches between their responses to figure out which menu to serve. The first menu is usually a result of receiving a blank text -- the user just dialed in.
```python
    # 7. Serve the Services Menu
        def main_menu_option(self, session_id: str, option: str):
          menus = {
              "1": self.deposit_controller.start,
              "2": self.order_controller.start,
              "3": self.account_controller.start,
              "4": self.customer_care_controller.start,
          }
          selected_menu = menus.get(option)
          if not selected_menu:
              return self.ussd_end(session_id=session_id, menu_text="invalid input")
          return selected_menu(session_id=session_id)  # noqa

    def execute(self, session_id: str, user: str = None):
        session = self.get_session(session_id=session_id)
        if not session.get("current_input"):
            return self.main_menu(session, user)
        if session.get("handler") == self.default:
            session["base_option"] = session.get("current_input")
            session = self.update_session(session_id=session_id, obj_in=session)
        return self.main_menu_option(session_id, session.get("base_option"))

```
