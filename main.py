#!/usr/bin/env python

import anyconfig
import click
import logging
import pathlib
import time

import robot.outputs.display as robot_display
import robot.outputs.sound as robot_sound
import robot.servers.http as http_serve
import robot.runners as robot_runners
import robot.driver as robot_driver

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = (pathlib.Path(__file__).parent.parent / "config" /
                  "config.yaml")


def run(driver: robot_driver.RobotDriver) -> None:
    logger.info("Running Driver Server")
    runner = robot_runners.RobotScriptRunner(driver)
    try:
        runner.run()
    except KeyboardInterrupt:
        logger.info("Stopping Driver (user cancelled)")


def run_http_server(driver: robot_driver.RobotDriver) -> None:
    http_serve.run_server(driver)


def run_test_mode(driver: robot_driver.RobotDriver) -> None:
    logger.info("Starting Run Loop")

    runner = robot_runners.TestModeRunner(driver)
    runner.run()


def run_async_test(driver: robot_driver.RobotDriver) -> None:
    logger.info("Starting Run Loop")

    runner = robot_runners.TestAsyncRunner(driver)
    runner.run()


def run_led_test(driver: robot_driver.RobotDriver) -> None:
    # Boostrap test
    while True:
        time.sleep(0.5)
        driver.toggle_all_leds()


def run_text_test(driver: robot_driver.RobotDriver) -> None:
    display = driver.display
    if not display:
        print('No display configured.')
        return

    try:
        while True:
            text = click.prompt("Text to display (q to quit)")
            if text != 'q':
                display.draw_text(text)
            else:
                break

    except KeyboardInterrupt:
        pass


def run_servo_test(driver: robot_driver.RobotDriver) -> None:
    logger.info("Servo Test")
    for s in driver.servos:
        s.set_position_norm(0.0)
        time.sleep(0.5)
        s.set_position_norm(1.0)
        time.sleep(0.5)
        s.set_position_norm(0.0)


def run_sound_test(driver: robot_driver.RobotDriver) -> None:
    logger.info("Running sound test")
    robot_sound.run_test()


def run_display_test(driver: robot_driver.RobotDriver) -> None:
    logger.info("Running display test")
    robot_display.run_test()


driver_modes = {
    'osc': None,
    'http': run_http_server,
    'run': run,
    'ledtest': run_led_test,
    'screentest': run_display_test,
    'soundtest': run_sound_test,
    'drawtext': run_text_test,
    'servotest': run_servo_test,
    'test': run_test_mode,
    'asynctest': run_async_test,
}


@click.command()
@click.argument('server_mode', type=click.Choice(driver_modes.keys()),
                default='run')
@click.option('-c', '--config', type=click.Path(exists=True),
              default=DEFAULT_CONFIG)
@click.option('-v', '--verbose', count=True)
def run_robot(server_mode: str, config: str, verbose: int) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    robot_config = anyconfig.load(config, ac_parser="yaml")

    mode_fn = driver_modes[server_mode]
    if not mode_fn:
        print(f'No driver configured for specified mode: {server_mode}')
        return

    with robot_driver.RobotDriver(robot_config) as driver:
        mode_fn(driver)


if __name__ == "__main__":
    run_robot()
