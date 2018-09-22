from flask import Flask, request, jsonify, g
from flask_restful import Resource, Api
import json


app = Flask(__name__)
api = Api(app)
robot_driver = None


class LEDs(Resource):
    def get(self, led_id):
        state = robot_driver.get_led_state(int(led_id))
        app.logger.info(f"Get the LED {led_id} state: {state}")
        return {"led_index": led_id, "state": state}

    def post(self, led_id):
        state = robot_driver.toggle_led_state(int(led_id))
        app.logger.info(f"Toggle the LED {led_id} state to: {state}")
        return {"led_index": led_id, "state": state}


class Buttons(Resource):
    def post(self, button_id):
        app.logger.info(f"Simulate the button {button_id} trigger")
        robot_driver.trigger_button_cb(int(button_id))

        return {"success": True}


class Knobs(Resource):
    def post(self, knob_id):
        try:
            request_data = json.loads(request.data)
            state = robot_driver.set_knob_state(int(knob_id),
                                                float(request_data['value']))
            app.logger.info(f"Set the Knob {knob_id} state to: {state}")
            return {"knob_id": knob_id, "state": state}
        except KeyError:
            return {"message": "Invalid response"}

    def get(self, knob_id):
        state = robot_driver.get_knob_state(int(knob_id))
        app.logger.info(f"Get the knob {knob_id} state: {state}")
        return {"knob_id": knob_id, "state": state}


class Servos(Resource):
    def post(self, servo_id):
        try:
            request_data = json.loads(request.data)
            position = float(request_data['position'])
            duration = request_data.get('duration')
            duration = float(duration) if duration else None

            if duration:
                robot_driver.set_servo_stepped(position, duration)
            else:
                robot_driver.set_servo_position(position)
        except KeyError:
            return {"message": "Invalid"}


api.add_resource(LEDs, "/leds/<led_id>")
api.add_resource(Buttons, "/buttons/<button_id>")
api.add_resource(Knobs, "/knobs/<knob_id>")
api.add_resource(Servos, "/servos/<servo_id>")


def run_server(driver):
    global robot_driver

    robot_driver = driver
    app.run(host="0.0.0.0", port=5432, debug=True)
