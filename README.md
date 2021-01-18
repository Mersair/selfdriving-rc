### selfdriving-rc
# Self Driving RC Car System
*A self driving algorithm for self driving RC car that is intentionally free of ML and thus, training time. Web server and browser based controllers included.*

Components
 - Car Client: Responsible for communicating with the remote server API. Informs server of current camera frame, sensor data, and CPU latency. Receives commands to stop/start driving, and alter vehicle throttle. This also includes all neccesary AI to drive the car, primarily through OpenCV tools.
 - Server: Exposes two API's, which track state of currently online RC car(s), and acts as a mediator for car controls to the car, and historic driving data for web controller. Allows for a many to many relationship between cars and controllers.
 - Web Controller: Browser UI for monitoring car performance. May be used for simple controls pertaining to stopping/starting the car and changing speed. Connects to the Server's exposed API.

<sup>(?) Note: Networking scheme and API design may seem a bit odd. This project is specifically tailored to be used on our University's wireless network.</sup>
