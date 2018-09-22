"""The main robot 'driver' lives here."""
import click

import robot.servers.osc as osc_serve
import robot.servers.http as http_serve


class RobotDriver:
    def __init_(self):
        pass


@click.command()
@click.option('-m', '--server_mode', type=click.Choice(['osc', 'http']))
def run_robot(server_mode):
    driver = RobotDriver()

    if server_mode == "osc":
        osc_serve.run_server(driver)

    elif server_mode == "http":
        http_serve..run_server(driver)


if __name__ == "__main__":
    run_robot()
