import numpy as np
import pytest

import robot.sensors.adc as robot_adc


@pytest.fixture
def patched_spi(monkeypatch):
    def mockreturn(*args):
        return np.random.randint(0, 1024)

    monkeypatch.setattr(robot_adc, 'read_adc_spi_pin', mockreturn)


@pytest.fixture
def mock_adcpoller(patched_spi):
    adc = robot_adc.ADCPoller(1, 2, 3, 4)
    adc.setup()
    return adc


class TestADCPoller:
    def test_create_adcpoller_basic(self):
        adc = robot_adc.ADCPoller(1, 2, 3, 4)
        assert adc is not None
        assert isinstance(adc, robot_adc.ADCPoller)
        assert adc.spi_clk == 1
        assert adc.spi_miso == 2
        assert adc.spi_mosi == 3
        assert adc.spi_cs == 4

    def test_adc_poll(self, mock_adcpoller):
        assert np.all(mock_adcpoller.poll() > 0)

    def test_lambda_callback(self, mock_adcpoller):
        counter = 0

        def inc_counter(x):
            nonlocal counter
            counter += 1

        cbs = [robot_adc.LambdaCallback(inc_counter)]
        mock_adcpoller.set_callbacks(cbs)

        for i in range(10):
            mock_adcpoller.poll()

        assert counter == 10

