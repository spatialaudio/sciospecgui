import struct
from typing import Union
from workingvariables import ScioSpecMeasurementSetup
import numpy as np


def set_measurement_config(serial, ssms: ScioSpecMeasurementSetup) -> None:
    """
    set_measurement_config sets the ScioSpec device configuration depending on the ssms configuration dataclass.

    Parameters
    ----------
    serial : _type_
        serial connection
    ssms : ScioSpecMeasurementSetup
        dataclass with the measurement setup settings.
    """

    def clTbt_sp(val: Union[int, float]) -> list:
        """
        clTbt_sp converts an integer or float value to a list of single precision bytes.

        Parameters
        ----------
        val : Union[int, float]
            Value that has to be converted

        Returns
        -------
        list
            list with single precision byte respresentation
        """
        return [int(bt) for bt in struct.pack(">f", val)]

    def clTbt_dp(val: float) -> list:
        """
        clTbt_dp converts an integer or float value to a list of double precision bytes.

        Parameters
        ----------
        val : float
            value that has to be converted

        Returns
        -------
        list
            list with double precision byte respresentation
        """
        return [int(ele) for ele in struct.pack(">d", val)]

    # Set measurement setup:
    serial.write(bytearray([0xB0, 0x01, 0x01, 0xB0]))
    # Set burst count: "B0 03 02 00 03 B0" = 3
    serial.write(bytearray([0xB0, 0x03, 0x02, 0x00, ssms.burst_count, 0xB0]))

    # Excitation amplitude double precision
    # A_min = 100nA
    # A_max = 10mA
    if ssms.amplitude > 0.001:
        print(f"Divide {ssms.amplitude}/1000. Out of available range")
        ssms.amplitude = ssms.amplitude / 1000
    serial.write(
        bytearray(list(np.concatenate([[176, 9, 5], clTbt_dp(ssms.amplitude), [176]])))
    )

    # ADC range settings: [+/-1, +/-5, +/-10]
    # ADC range = +/-1  : B0 02 0D 01 B0
    # ADC range = +/-5  : B0 02 0D 02 B0
    # ADC range = +/-10 : B0 02 0D 03 B0
    if ssms.adc_range == 1:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x01, 0xB0]))
    elif ssms.adc_range == 5:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x02, 0xB0]))
    elif ssms.adc_range == 10:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x03, 0xB0]))

    # Gain settings:
    # Gain = 1     : B0 03 09 01 00 B0
    # Gain = 10    : B0 03 09 01 01 B0
    # Gain = 100   : B0 03 09 01 02 B0
    # Gain = 1_000 : B0 03 09 01 03 B0
    if ssms.gain == 1:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x00, 0xB0]))
    elif ssms.gain == 10:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x01, 0xB0]))
    elif ssms.gain == 100:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x02, 0xB0]))
    elif ssms.gain == 1_000:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x03, 0xB0]))

    # Single ended mode:
    serial.write(bytearray([0xB0, 0x03, 0x08, 0x01, 0x01, 0xB0]))

    # Excitation switch type:
    serial.write(bytearray([0xB0, 0x02, 0x0C, 0x01, 0xB0]))

    # Set framerate:
    serial.write(
        bytearray(list(np.concatenate([[176, 5, 3], clTbt_sp(ssms.framerate), [176]])))
    )

    # Set frequencies:
    # [CT] 0C 04 [fmin] [fmax] [fcount] [ftype] [CT]
    f_min = clTbt_sp(ssms.exc_freq)
    f_max = clTbt_sp(ssms.exc_freq)
    f_count = [0, 1]
    f_type = [0]
    # bytearray
    serial.write(
        bytearray(
            list(np.concatenate([[176, 12, 4], f_min, f_max, f_count, f_type, [176]]))
        )
    )

    # Set injection config

    el_inj = np.arange(1, ssms.n_el + 1)
    el_gnd = np.roll(el_inj, -(ssms.inj_skip + 1))

    for v_el, g_el in zip(el_inj, el_gnd):
        serial.write(bytearray([0xB0, 0x03, 0x06, v_el, g_el, 0xB0]))

    # Get measurement setup
    serial.write(bytearray([0xB1, 0x01, 0x03, 0xB1]))
    # Set output configuration
    serial.write(bytearray([0xB2, 0x02, 0x01, 0x01, 0xB2]))
    serial.write(bytearray([0xB2, 0x02, 0x03, 0x01, 0xB2]))
    serial.write(bytearray([0xB2, 0x02, 0x02, 0x01, 0xB2]))

    ## start measurement
    # serial.write(bytearray([0xB4, 0x01, 0x01, 0xB4]))
    # stop measurement
    # serial.write(bytearray([0xB4, 0x01, 0x00, 0xB4]))
