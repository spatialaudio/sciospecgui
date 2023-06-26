import struct
from typing import Union
from workingvariables import ScioSpecMeasurementConfig
import numpy as np


def set_measurement_config(serial, smc: ScioSpecMeasurementConfig) -> None:
    """
    set_measurement_config sets the ScioSpec device configuration depending on the smc configuration dataclass.

    Parameters
    ----------
    serial : _type_
        serial connection
    smc : ScioSpecMeasurementConfig
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
    serial.write(bytearray([0xB0, 0x03, 0x02, 0x00, smc.burst_count, 0xB0]))

    # Excitation amplitude double precision
    # A_min = 100nA
    # A_max = 10mA
    if smc.amplitude > 0.001:
        print(f"Divide {smc.amplitude}/1000. Out of available range")
        smc.amplitude = smc.amplitude / 1000
    serial.write(
        bytearray(list(np.concatenate([[176, 9, 5], clTbt_dp(smc.amplitude), [176]])))
    )

    # ADC range settings: [+/-1, +/-5, +/-10]
    # ADC range = +/-1  : B0 02 0D 01 B0
    # ADC range = +/-5  : B0 02 0D 02 B0
    # ADC range = +/-10 : B0 02 0D 03 B0
    if smc.adc_range == 1:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x01, 0xB0]))
    elif smc.adc_range == 5:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x02, 0xB0]))
    elif smc.adc_range == 10:
        serial.write(bytearray([0xB0, 0x02, 0x0D, 0x03, 0xB0]))

    # Gain settings:
    # Gain = 1     : B0 03 09 01 00 B0
    # Gain = 10    : B0 03 09 01 01 B0
    # Gain = 100   : B0 03 09 01 02 B0
    # Gain = 1_000 : B0 03 09 01 03 B0
    if smc.gain == 1:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x00, 0xB0]))
    elif smc.gain == 10:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x01, 0xB0]))
    elif smc.gain == 100:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x02, 0xB0]))
    elif smc.gain == 1_000:
        serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x03, 0xB0]))

    # Single ended mode:
    serial.write(bytearray([0xB0, 0x03, 0x08, 0x01, 0x01, 0xB0]))

    # Excitation switch type:
    serial.write(bytearray([0xB0, 0x02, 0x0C, 0x01, 0xB0]))

    # Set framerate:
    serial.write(
        bytearray(list(np.concatenate([[176, 5, 3], clTbt_sp(smc.framerate), [176]])))
    )

    # Set frequencies:
    # [CT] 0C 04 [fmin] [fmax] [fcount] [ftype] [CT]
    f_min = clTbt_sp(smc.exc_freq)
    f_max = clTbt_sp(smc.exc_freq)
    f_count = [0, 1]
    f_type = [0]
    # bytearray
    serial.write(
        bytearray(
            list(np.concatenate([[176, 12, 4], f_min, f_max, f_count, f_type, [176]]))
        )
    )

    # Set injection config

    el_inj = np.arange(1, smc.n_el + 1)
    el_gnd = np.roll(el_inj, -(smc.inj_skip + 1))

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
