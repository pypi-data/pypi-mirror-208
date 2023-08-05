"""
Translation from DLL commands
-----------------------------

Commands
........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_M2CMD`
    - :obj:`Card.execute_commands`
  * - :obj:`SPC_M2CMD` Command
    - :obj:`M2CMD_CARD_START`
    - :obj:`Card.start`, :obj:`Card.arm`
  * - :obj:`SPC_M2CMD` Command
    - :obj:`M2CMD_CARD_STOP`
    - :obj:`Card.stop`
  * - :obj:`SPC_M2CMD` Command
    - :obj:`M2CMD_CARD_RESET`
    - :obj:`Card.reset`
  * - :obj:`SPC_M2CMD` Command
    - :obj:`M2CMD_CARD_FORCETRIGGER`
    - :obj:`Card.force_trigger`
  * - :obj:`SPC_M2CMD` Command
    - :obj:`M2CMD_DATA_STARTDMA`
    - :obj:`Card.array_to_device`
  * - Read
    - :obj:`SPC_M2STATUS`
    - :obj:`Card.get_status_information`
  * - Write
    - :obj:`SPC_TIMEOUT`
    - :obj:`Card.set_timeout`
  * - Read
    - :obj:`SPC_TIMEOUT`
    - :obj:`Card.get_timeout`

Card identity
.............

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Call
    - :obj:`spcm_hOpen`
    - :obj:`Card`
  * - Read
    - :obj:`SPC_PCITYP`
    - :obj:`Card.get_name`, :obj:`Card.get_series_information`
  * - Read
    - :obj:`SPC_PCISERIALNO`
    - :obj:`Card.get_serial_number`
  * - Read
    - :obj:`SPC_PCIDATE`
    - :obj:`Card.get_production_date_information`
  * - Read
    - :obj:`SPC_CALIBDATE`
    - :obj:`Card.get_calibration_date_information`
  * - Write
    - :obj:`SPC_CARDIDENTIFICATION`
    - :obj:`Card.identification_led_enable`, :obj:`Card.identification_led_disable`
  * - Read
    - :obj:`SPC_CARDIDENTIFICATION`
    - :obj:`Card.get_card_identification`

Card information
................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_MIINST_MODULES`
    - :obj:`Card.get_number_of_front_end_modules`
  * - Read
    - :obj:`SPC_MIINST_CHPERMODULE`
    - :obj:`Card.get_number_of_channels_per_front_end_module`
  * - Read
    - :obj:`SPC_MIINST_MAXADCVALUE`
    - :obj:`Card.get_adc_full_scale`
  * - Read
    - :obj:`SPC_MIINST_MINEXTCLOCK`
    - :obj:`Card.get_min_external_clock`
  * - Read
    - :obj:`SPC_MIINST_MAXEXTCLOCK`
    - :obj:`Card.get_max_external_clock`
  * - Read
    - :obj:`SPC_MIINST_MINEXTREFCLOCK`
    - :obj:`Card.get_min_external_reference_clock`
  * - Read
    - :obj:`SPC_MIINST_MAXEXTREFCLOCK`
    - :obj:`Card.get_max_external_reference_clock`

Hardware and PCB version
........................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_PCIVERSION`
    - :obj:`Card.get_pci_information`
  * - Read
    - :obj:`SPC_BASEPCBVERSION`
    - :obj:`Card.get_base_pcb_information`
  * - Read
    - :obj:`SPC_PCIMODULEVERSION`
    - :obj:`Card.get_module_pci_information`
  * - Read
    - :obj:`SPC_MODULEPCBVERSION`
    - :obj:`Card.get_module_pcb_information`
  * - Read
    - :obj:`SPC_PCIEXTVERSION`
    - :obj:`Card.get_extension_pci_information`
  * - Read
    - :obj:`SPC_EXTPCBVERSION`
    - :obj:`Card.get_extension_pcb_information`
  * - Read
    - :obj:`SPC_PXIHWSLOTNO`
    - :obj:`Card.get_pxi_slot_number`

Firmware information
....................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPCM_FW_CTRL`
    - :obj:`Card.get_firmware_version_control_information`
  * - Read
    - :obj:`SPCM_FW_CTRL_GOLDEN`
    - :obj:`Card.get_firmware_version_control_golden_information`
  * - Read
    - :obj:`SPCM_FW_CTRL_ACTIVE`
    - :obj:`Card.get_firmware_version_control_active_information`
  * - Read
    - :obj:`SPCM_FW_CLOCK`
    - :obj:`Card.get_firmware_version_clock_information`
  * - Read
    - :obj:`SPCM_FW_CONFIG`
    - :obj:`Card.get_firmware_version_configuration_information`
  * - Read
    - :obj:`SPCM_FW_MODULEA`
    - :obj:`Card.get_firmware_version_module_a_information`
  * - Read
    - :obj:`SPCM_FW_MODULEB`
    - :obj:`Card.get_firmware_version_module_b_information`
  * - Read
    - :obj:`SPCM_FW_MODEXTRA`
    - :obj:`Card.get_firmware_version_module_star_information`
  * - Read
    - :obj:`SPCM_FW_POWER`
    - :obj:`Card.get_firmware_version_power_information`

Driver information
..................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_GETDRVTYPE`
    - :obj:`Card.get_driver_information`
  * - Read
    - :obj:`SPC_GETDRVVERSION`
    - :obj:`Card.get_driver_version_information`
  * - Read
    - :obj:`SPC_GETKERNELVERSION`
    - :obj:`Card.get_kernel_version_information`

Card modifications
..................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPCM_CUSTOMMOD`
    - :obj:`Card.get_modifications_information`

Features and functions
......................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_PCIFEATURES`, :obj:`SPC_PCIEXTFEATURES`, :obj:`SPC_READAOFEATURES`, :obj:`SPC_SEQMODE_AVAILFEATURES`
    - :obj:`Card.get_features_information`
  * - Read
    - :obj:`SPC_FNCTYPE`
    - :obj:`Card.get_functions_information`

Temperature
...........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_MON_TC_BASE_CTRL`
    - :obj:`Card.get_temperature_base`
  * - Read
    - :obj:`SPC_MON_TC_MODULE_0`
    - :obj:`Card.get_temperature_module_0`
  * - Read
    - :obj:`SPC_MON_TC_MODULE_1`
    - :obj:`Card.get_temperature_module_1`

Card mode
.........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_CARDMODE`
    - :obj:`Card.use_mode_single`, :obj:`Card.use_mode_multi`, :obj:`Card.use_mode_gate`, :obj:`Card.use_mode_single_restart`, :obj:`Card.use_mode_sequence`, :obj:`Card.use_mode_fifo_single`, :obj:`Card.use_mode_fifo_multi`, :obj:`Card.use_mode_fifo_gate`
  * - Read
    - :obj:`SPC_CARDMODE`
    - :obj:`Card.get_mode_information`
  * - Read
    - :obj:`SPC_AVAILCARDMODES`
    - :obj:`Card.get_available_modes_information`

Sample rate
...........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_SAMPLERATE`
    - :obj:`Card.set_sample_rate`
  * - Read
    - :obj:`SPC_SAMPLERATE`
    - :obj:`Card.get_sample_rate`
  * - Read
    - :obj:`SPC_PCISAMPLERATE`
    - :obj:`Card.get_max_sample_rate`
  * - Read
    - :obj:`SPC_MIINST_BYTESPERSAMPLE`
    - :obj:`Card.get_sample_resolution`
  * - Read
    - :obj:`SPC_MIINST_BITSPERSAMPLE`
    - :obj:`Card.get_sample_resolution_bits`

Clock
.....

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_CLOCKOUT`
    - :obj:`Card.clock_output_enable`, :obj:`Card.clock_output_disable`
  * - Read
    - :obj:`SPC_CLOCKOUT`
    - :obj:`Card.get_clock_output`
  * - Read
    - :obj:`SPC_CLOCKOUTFREQUENCY`
    - :obj:`Card.get_clock_output_frequency`
  * - Write
    - :obj:`SPC_REFERENCECLOCK`
    - :obj:`Card.set_external_reference_frequency`
  * - Read
    - :obj:`SPC_REFERENCECLOCK`
    - :obj:`Card.get_external_reference_frequency`
  * - Read
    - :obj:`SPC_AVAILCLOCKMODES`
    - :obj:`Card.get_available_clock_modes_information`
  * - Write
    - :obj:`SPC_CLOCKMODE`
    - :obj:`Card.use_clock_primary_internal`, :obj:`Card.use_clock_secondary_internal`, :obj:`Card.use_clock_external_reference`, :obj:`Card.use_clock_pxie_reference`
  * - Read
    - :obj:`SPC_CLOCKMODE`
    - :obj:`Card.get_clock_mode_information`

Triggers
........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_TRIG_DELAY`
    - :obj:`Card.set_trigger_delay`
  * - Read
    - :obj:`SPC_TRIG_DELAY`
    - :obj:`Card.get_trigger_delay`
  * - Read
    - :obj:`SPC_TRIG_AVAILDELAY`
    - :obj:`Card.get_max_trigger_delay`
  * - Write
    - :obj:`SPC_TRIG_TERM`
    - :obj:`Card.trigger_impedance_use_high`, :obj:`Card.trigger_impedance_use_50`
  * - Read
    - :obj:`SPC_TRIG_TERM`
    - :obj:`Card.get_trigger_impedance`
  * - Write
    - :obj:`SPC_TRIG_EXT0_ACDC`
    - :obj:`Card.trigger_coupling_use_dc`, :obj:`Card.trigger_coupling_use_ac`
  * - Read
    - :obj:`SPC_TRIG_EXT0_ACDC`
    - :obj:`Card.get_trigger_coupling`
  * - Write
    - :obj:`SPC_TRIG_EXT0_MODE`
    - :obj:`Card.trigger_disable`, :obj:`Card.use_trigger_positive_edge`, :obj:`Card.use_trigger_negative_edge`, :obj:`Card.use_trigger_both_edge`, :obj:`Card.use_trigger_enter_window`, :obj:`Card.use_trigger_leave_window`, :obj:`Card.use_trigger_high_gate`, :obj:`Card.use_trigger_low_gate`, :obj:`Card.use_trigger_inside_window_gate`, :obj:`Card.use_trigger_outside_window_gate`
  * - Read
    - :obj:`SPC_TRIG_EXT0_MODE`
    - :obj:`Card.get_trigger_mode_information`
  * - Read
    - :obj:`SPC_TRIG_EXT0_AVAILMODES`
    - :obj:`Card.get_available_trigger_modes_information`

Trigger masks
.............

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_TRIG_ORMASK`
    - :obj:`Card.set_sufficient_triggers`
  * - Read
    - :obj:`SPC_TRIG_ORMASK`
    - :obj:`Card.get_sufficient_triggers`
  * - Read
    - :obj:`SPC_TRIG_AVAILORMASK`
    - :obj:`Card.get_available_sufficient_triggers`
  * - Write
    - :obj:`SPC_TRIG_CH_ORMASK0`
    - :obj:`Card.set_channels_for_sufficient_triggers`
  * - Read
    - :obj:`SPC_TRIG_CH_ORMASK0`
    - :obj:`Card.get_channels_for_sufficient_triggers`
  * - Read
    - :obj:`SPC_TRIG_CH_AVAILORMASK0`
    - :obj:`Card.get_available_channels_for_sufficient_triggers`
  * - Write
    - :obj:`SPC_TRIG_ANDMASK`
    - :obj:`Card.set_necessary_triggers`
  * - Read
    - :obj:`SPC_TRIG_ANDMASK`
    - :obj:`Card.get_necessary_triggers`
  * - Read
    - :obj:`SPC_TRIG_AVAILANDMASK`
    - :obj:`Card.get_available_necessary_triggers`
  * - Write
    - :obj:`SPC_TRIG_CH_ANDMASK0`
    - :obj:`Card.set_channels_for_necessary_triggers`
  * - Read
    - :obj:`SPC_TRIG_CH_ANDMASK0`
    - :obj:`Card.get_channels_for_necessary_triggers`
  * - Read
    - :obj:`SPC_TRIG_CH_AVAILANDMASK0`
    - :obj:`Card.get_available_channels_for_necessary_triggers`

Channels
........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_CHENABLE`
    - :obj:`Card.set_channels_enable`
  * - Read
    - :obj:`SPC_CHENABLE`
    - :obj:`Card.get_channels_enable`
  * - Read
    - :obj:`SPC_CHCOUNT`
    - :obj:`Card.get_number_of_active_channels`
  * - Write
    - :obj:`SPC_AMP0`
    - :obj:`Card.set_amplitude`
  * - Read
    - :obj:`SPC_AMP0`
    - :obj:`Card.get_amplitude`
  * - Write
    - :obj:`SPC_ENABLEOUT0`
    - :obj:`Card.output_enable`, :obj:`Card.output_disable`
  * - Read
    - :obj:`SPC_ENABLEOUT0`
    - :obj:`Card.get_output_enable`
  * - Write
    - :obj:`SPC_FILTER0`
    - :obj:`Card.channel_filter_enable`, :obj:`Card.channel_filter_disable`
  * - Read
    - :obj:`SPC_FILTER0`
    - :obj:`Card.get_filter`
  * - Write
    - :obj:`SPC_DIFF0`
    - :obj:`Card.differential_enable`, :obj:`Card.differential_disable`
  * - Read
    - :obj:`SPC_DIFF0`
    - :obj:`Card.get_differential`
  * - Write
    - :obj:`SPC_DOUBLEOUT0`
    - :obj:`Card.double_enable`, :obj:`Card.double_disable`
  * - Read
    - :obj:`SPC_DOUBLEOUT0`
    - :obj:`Card.get_double`
  * - Write
    - :obj:`SPC_CH0_STOPLEVEL`, :obj:`SPC_CH0_CUSTOM_STOP`
    - :obj:`Card.set_channel_stop_level`
  * - Read
    - :obj:`SPC_CH0_STOPLEVEL`, :obj:`SPC_CH0_CUSTOM_STOP`
    - :obj:`Card.get_channel_stop_level`

Playback
........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPC_LOOPS`
    - :obj:`Card.set_number_of_loops`
  * - Read
    - :obj:`SPC_LOOPS`
    - :obj:`Card.get_number_of_loops`

Sequencing
..........

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Read
    - :obj:`SPC_SEQMODE_AVAILMAXSEGMENT`
    - :obj:`Card.get_max_number_of_segments`
  * - Read
    - :obj:`SPC_SEQMODE_AVAILMAXSTEPS`
    - :obj:`Card.get_max_number_of_sequence_steps`
  * - Read
    - :obj:`SPC_SEQMODE_AVAILMAXLOOP`
    - :obj:`Card.get_max_number_of_loops_per_sequence_step`
  * - Read
    - :obj:`SPC_SEQMODE_AVAILFEATURES`
    - :obj:`Card.get_available_sequence_features_information`
  * - Write
    - :obj:`SPC_SEQMODE_MAXSEGMENTS`
    - :obj:`Card.set_number_of_segments`
  * - Read
    - :obj:`SPC_SEQMODE_MAXSEGMENTS`
    - :obj:`Card.get_number_of_segments`
  * - Write
    - :obj:`SPC_SEQMODE_WRITESEGMENT`
    - :obj:`Card.set_current_segment`
  * - Read
    - :obj:`SPC_SEQMODE_WRITESEGMENT`
    - :obj:`Card.get_current_segment`
  * - Write
    - :obj:`SPC_SEQMODE_SEGMENTSIZE`
    - :obj:`Card.set_segment_length`
  * - Read
    - :obj:`SPC_SEQMODE_SEGMENTSIZE`
    - :obj:`Card.get_segment_length`
  * - Write
    - :obj:`SPC_SEQMODE_STEPMEM0`
    - :obj:`Card.set_step_instruction`
  * - Read
    - :obj:`SPC_SEQMODE_STEPMEM0`
    - :obj:`Card.get_step_instruction`
  * - Write
    - :obj:`SPC_SEQMODE_STARTSTEP`
    - :obj:`Card.set_start_step`
  * - Read
    - :obj:`SPC_SEQMODE_STARTSTEP`
    - :obj:`Card.get_start_step`

Memory and DMA
..............

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Call
    - :obj:`spcm_dwDefTransfer_i64`
    - :obj:`Card.array_to_device`
  * - Write
    - :obj:`SPC_MEMSIZE`
    - :obj:`Card.set_memory_size`
  * - Read
    - :obj:`SPC_MEMSIZE`
    - :obj:`Card.get_memory_size`
  * - Read
    - :obj:`SPC_PCIMEMSIZE`
    - :obj:`Card.get_max_memory_size`
  * - Write
    - :obj:`SPC_MEMTEST`
    - :obj:`Card.memory_test_start`, :obj:`Card.memory_test_stop`
  * - Read
    - :obj:`SPC_MEMTEST`
    - :obj:`Card.get_memory_test`

Multi-purpose input/output (X ports)
....................................

.. list-table::
  :header-rows: 1

  * - Direction
    - Register
    - Equivalent method
  * - Write
    - :obj:`SPCM_X0_MODE`
    - :obj:`Card.io_port_disable`, :obj:`Card.use_io_mode_digital_out`, :obj:`Card.use_io_mode_asynchronous_input`, :obj:`Card.use_io_mode_asynchronous_output`, :obj:`Card.use_io_mode_trigger_output`, :obj:`Card.use_io_mode_run_state_output`, :obj:`Card.use_io_mode_arm_state_output`, :obj:`Card.use_io_mode_continuous_marker_output`, :obj:`Card.use_io_mode_reference_clock_output`, :obj:`Card.use_io_mode_system_clock_output`
  * - Read
    - :obj:`SPCM_X0_MODE`
    - :obj:`Card.get_io_mode_information`
  * - Read
    - :obj:`SPCM_X0_AVAILMODES`
    - :obj:`Card.get_available_io_modes_information`
  * - Write
    - :obj:`SPCM_XX_ASYNCIO`
    - :obj:`Card.set_io_asynchronous`
  * - Read
    - :obj:`SPCM_XX_ASYNCIO`
    - :obj:`Card.get_io_asynchronous`

  
Card class
----------
"""

from spectrum_card.spectrum_header import pyspcm as spcm
from spectrum_card.spectrum_header import spcm_tools

import numpy as np

class Card:
  """
  Opens the connection to the card using :obj:`spcm_hOpen`.

  Parameters
  ----------
  device_address : :obj:`str`
    Directory to the card.
  """
  def __init__(self, device_address = b"/dev/spcm0"):
    self.is_alive = False
    self.card_handle = spcm.spcm_hOpen(spcm.create_string_buffer(device_address))
    if self.card_handle is None:
      raise Exception("No card found...")
    self.is_alive = True
    
  def close(self):
    """
    Closes the connection to the card.
    """
    spcm.spcm_vClose(self.card_handle)
    self.is_alive = False
  
  # Error handling --------------------------------------------------------------
  # =============================================================================
  
  def _handle_error(self, error_message):
    if not error_message:
      return
    is_remote = ((error_message & spcm.SPCM_ERROR_ORIGIN_MASK) == spcm.SPCM_ERROR_ORIGIN_REMOTE)
    error_message_short = error_message & (~spcm.SPCM_ERROR_ORIGIN_MASK)
    if error_message_short == spcm.ERR_VALUE:
      exception_type = ValueError
    else:
      exception_type = Exception
    error_dictionary = {
      spcm.ERR_INIT : "ERR_INIT: An error occurred when initializing the given card. Either the card has already been opened by another process or an hardware error occurred.",
      spcm.ERR_NR : "ERR_NR",
      spcm.ERR_TYP : "ERR_TYP: Initialization only: The type of board is unknown. This is a critical error. Please check whether the board is correctly plugged in the slot and whether you have the latest driver version.",
      spcm.ERR_FNCNOTSUPPORTED : "ERR_FNCNOTSUPPORTED: This function is not supported by the hardware version.",
      spcm.ERR_BRDREMAP : "ERR_BRDREMAP: The board index re map table in the registry is wrong. Either delete this table or check it carefully for double values.",
      spcm.ERR_KERNELVERSION : "ERR_KERNELVERSION: The version of the kernel driver is not matching the version of the DLL. Please do a complete re-installation of the hardware driver. This error normally only occurs if someone copies the driver library and the kernel driver manually.",
      spcm.ERR_HWDRVVERSION : "ERR_HWDRVVERSION: The hardware needs a newer driver version to run properly. Please install the driver that was delivered together with the card.",
      spcm.ERR_ADRRANGE : "ERR_ADRRANGE: One of the address ranges is disabled (fatal error), can only occur under Linux.",
      spcm.ERR_INVALIDHANDLE : "ERR_INVALIDHANDLE: The used handle is not valid.",
      spcm.ERR_BOARDNOTFOUND : "ERR_BOARDNOTFOUND: A card with the given name has not been found.",
      spcm.ERR_BOARDINUSE : "ERR_BOARDINUSE: A card with given name is already in use by another application.",
      spcm.ERR_EXPHW64BITADR : "ERR_EXPHW64BITADR: Express hardware version not able to handle 64 bit addressing -> update needed.",
      spcm.ERR_FWVERSION : "ERR_FWVERSION: Firmware versions of synchronized cards or for this driver do not match -> update needed.",
      spcm.ERR_SYNCPROTOCOL : "ERR_SYNCPROTOCOL: Synchronization protocol versions of synchronized cards do not match -> update needed",
      spcm.ERR_KERNEL : "ERR_KERNEL",
      spcm.ERR_LASTERR : "ERR_LASTERR: Old error waiting to be read. Please read the full error information before proceeding. The driver is locked until the error information has been read.",
      spcm.ERR_ABORT : "ERR_ABORT: Abort of wait function. This return value just tells that the function has been aborted from another thread. The driver library is not locked if this error occurs.",
      spcm.ERR_BOARDLOCKED : "ERR_BOARDLOCKED: The card is already in access and therefore locked by another process. It is not possible to access one card through multiple processes. Only one process can access a specific card at the time.",
      spcm.ERR_DEVICE_MAPPING : "ERR_DEVICE_MAPPING: The device is mapped to an invalid device. The device mapping can be accessed via the Control Center.",
      spcm.ERR_NETWORKSETUP : "ERR_NETWORKSETUP: The network setup of a digitizerNETBOX has failed.",
      spcm.ERR_NETWORKTRANSFER : "ERR_NETWORKTRANSFER: The network data transfer from/to a digitizerNETBOX has failed.",
      spcm.ERR_FWPOWERCYCLE : "ERR_FWPOWERCYCLE: Power cycle (PC off/on) is needed to update the card's firmware (a simple OS reboot is not sufficient !)",
      spcm.ERR_NETWORKTIMEOUT : "ERR_NETWORKTIMEOUT : A network timeout has occurred.",
      spcm.ERR_BUFFERSIZE : "ERR_BUFFERSIZE: The buffer size is not sufficient (too small).",
      spcm.ERR_RESTRICTEDACCESS : "ERR_RESTRICTEDACCESS: The access to the card has been intentionally restricted.",
      spcm.ERR_INVALIDPARAM : "ERR_INVALIDPARAM: An invalid parameter has been used for a certain function.",
      spcm.ERR_TEMPERATURE : "ERR_TEMPERATURE: The temperature of at least one of the card's sensors measures a temperature, that is too high for the hardware.",
      spcm.ERR_FAN : "ERR_FAN",
      spcm.ERR_REG : "ERR_REG: The register is not valid for this type of board",
      spcm.ERR_VALUE : "ERR_VALUE: The value for this register is not in a valid range. The allowed values and ranges are listed in the board specific documentation.",
      spcm.ERR_FEATURE : "RR_FEATURE: Feature (option) is not installed on this board. It's not possible to access this feature if it's not installed.",
      spcm.ERR_SEQUENCE : "ERR_SEQUENCE: Command sequence is not allowed. Please check the manual carefully to see which command sequences are possible.",
      spcm.ERR_READABORT : "ERR_READABORT: Data read is not allowed after aborting the data acquisition.",
      spcm.ERR_NOACCESS : "ERR_NOACCESS: Access to this register is denied. This register is not accessible for users.",
      spcm.ERR_POWERDOWN : "ERR_POWERDOWN",
      spcm.ERR_TIMEOUT : "ERR_TIMEOUT: A timeout occurred while waiting for an interrupt. This error does not lock the driver.",
      spcm.ERR_CALLTYPE : "ERR_CALLTYPE: The access to the register is only allowed with one 64 bit access but not with the multiplexed 32 bit (high and low double word) version.",
      spcm.ERR_EXCEEDSINT32 : "ERR_EXCEEDSINT32: The return value is int32 but the software register exceeds the 32 bit integer range. Use double int32 or int64 accesses instead, to get correct return values.",
      spcm.ERR_NOWRITEALLOWED : "ERR_NOWRITEALLOWED: The register that should be written is a read-only register. No write accesses are allowed.",
      spcm.ERR_SETUP : "ERR_SETUP: The programmed setup for the card is not valid. The error register will show you which setting generates the error message. This error is returned if the card is started or the setup is written.",
      spcm.ERR_CLOCKNOTLOCKED : "ERR_CLOCKNOTLOCKED: Synchronization to external clock failed: no signal connected or signal not stable. Please check external clock or try to use a different sampling clock to make the PLL locking easier.",
      spcm.ERR_MEMINIT : "ERR_MEMINIT: On-board memory initialization error. Power cycle the PC and try another PCIe slot (if possible). In case that the error persists, please contact Spectrum support for further assistance.",
      spcm.ERR_POWERSUPPLY : "ERR_POWERSUPPLY: On-board power supply error. Power cycle the PC and try another PCIe slot (if possible). In case that the error persists, please contact Spectrum support for further assistance.",
      spcm.ERR_ADCCOMMUNICATION : "ERR_ADCCOMMUNICATION: Communication with ADC failed.P ower cycle the PC and try another PCIe slot (if possible). In case that the error persists, please contact Spectrum support for further assistance.",
      spcm.ERR_CHANNEL : "ERR_CHANNEL: The channel number may not be accessed on the board: Either it is not a valid channel number or the channel is not accessible due to the current setup (e.g. Only channel 0 is accessible in interlace mode) ",
      spcm.ERR_NOTIFYSIZE : "ERR_NOTIFYSIZE: The notify size of the last spcm_dwDefTransfer call is not valid. The notify size must be a multiple of the page size of 4096. For data transfer it may also be a fraction of 4k in the range of 16, 32, 64, 128, 256, 512, 1k or 2k. For ABA and timestamp the notify size can be 2k as a minimum.",
      spcm.ERR_RUNNING : "ERR_RUNNING: The board is still running, this function is not available now or this register is not accessible now.",
      spcm.ERR_ADJUST : "ERR_ADJUST: Automatic card calibration has reported an error. Please check the card inputs.",
      spcm.ERR_PRETRIGGERLEN : "ERR_PRETRIGGERLEN: The calculated pretrigger size (resulting from the user defined posttrigger values) exceeds the allowed limit.",
      spcm.ERR_DIRMISMATCH : "ERR_DIRMISMATCH: The direction of card and memory transfer mismatch. In normal operation mode it is not possible to transfer data from PC memory to card if the card is an acquisition card nor it is possible to transfer data from card to PC memory if the card is a generation card.",
      spcm.ERR_POSTEXCDSEGMENT : "ERR_POSTEXCDSEGMENT: The posttrigger value exceeds the programmed segment size in multiple recording/ABA mode. A delay of the multiple recording segments is only possible by using the delay trigger!",
      spcm.ERR_SEGMENTINMEM : "ERR_SEGMENTINMEM: Memsize is not a multiple of segment size when using Multiple Recording/Replay or ABA mode. The programmed segment size must match the programmed memory size.",
      spcm.ERR_MULTIPLEPW : "ERR_MULTIPLEPW: Multiple pulsewidth counters used but card only supports one at the time.",
      spcm.ERR_NOCHANNELPWOR : "ERR_NOCHANNELPWOR: The channel pulsewidth on this card can’t be used together with the OR conjunction. Please use the AND conjunction of the channel trigger sources.",
      spcm.ERR_ANDORMASKOVRLAP : "ERR_ANDORMASKOVRLAP: Trigger AND mask and OR mask overlap in at least one channel. Each trigger source can only be used either in the AND mask or in the OR mask, no source can be used for both.",
      spcm.ERR_ANDMASKEDGE : "RR_ANDMASKEDGE: One channel is activated for trigger detection in the AND mask but has been programmed to a trigger mode using an edge trigger. The AND mask can only work with level trigger modes.",
      spcm.ERR_ORMASKLEVEL : "RR_ORMASKLEVEL: One channel is activated for trigger detection in the OR mask but has been programmed to a trigger mode using a level trigger. The OR mask can only work together with edge trigger modes.",
      spcm.ERR_EDGEPERMOD : "ERR_EDGEPERMOD: This card is only capable to have one programmed trigger edge for each module that is installed. It is not possible to mix different trigger edges on one module.",
      spcm.ERR_DOLEVELMINDIFF : "ERR_DOLEVELMINDIFF: The minimum difference between low output level and high output level is not reached.",
      spcm.ERR_STARHUBENABLE : "ERR_STARHUBENABLE: The card holding the star-hub must be enabled when doing synchronization",
      spcm.ERR_PATPWSMALLEDGE : "ERR_PATPWSMALLEDGE: Combination of pattern with pulsewidth smaller and edge is not allowed.",
      spcm.ERR_XMODESETUP : "ERR_XMODESETUP: The chosen setup for (SPCM_X0_MODE .. SPCM_X19_MODE) is not valid. See hardware manual for details.",
      spcm.ERR_AVRG_TDA : "ERR_AVRG_LSA: Setup for Average LSA Mode not valid. Check Threshold and Replacement values for chosen AVRGMODE.",
      spcm.ERR_NOPCI : "ERR_NOPCI",
      spcm.ERR_PCIVERSION : "ERR_PCIVERSION",
      spcm.ERR_PCINOBOARDS : "ERR_PCINOBOARDS",
      spcm.ERR_PCICHECKSUM : "ERR_PCICHECKSUM: The check sum of the card information has failed. This could be a critical hardware failure. Restart the system and check the connection of the card in the slot.",
      spcm.ERR_DMALOCKED : "ERR_DMALOCKED",
      spcm.ERR_MEMALLOC : "ERR_MEMALLOC: Internal memory allocation failed. Please restart the system and be sure that there is enough free memory.",
      spcm.ERR_EEPROMLOAD : "ERR_EEPROMLOAD: Timeout occurred while loading information from the on-board EEProm. This could be a critical hardware failure. Please restart the system and check the PCI connector.",
      spcm.ERR_CARDNOSUPPORT : "ERR_CARDNOSUPPORT: The card that has been found in the system seems to be a valid Spectrum card of a type that is supported by the driver but the driver did not find this special type internally. Please get the latest driver from www.spectrum-instrumentation.com and install this one.",
      spcm.ERR_CONFIGACCESS : "ERR_CONFIGACCESS: Internal error occured during config writes or reads. Please contact Spectrum support for further assistance",
      spcm.ERR_FIFOBUFOVERRUN : "ERR_FIFOBUFOVERRUN",
      spcm.ERR_FIFOHWOVERRUN : "ERR_FIFOHWOVERRUN: FIFO acquisition: Hardware buffer overrun in FIFO mode. The complete on-board memory has been filled with data and data wasn’t transferred fast enough to PC memory. FIFO replay: Hardware buffer underrun in FIFO mode. The complete on-board memory has been replayed and data wasn’t transferred fast enough from PC memory. If acquisition or replay throughput is lower than the theoretical bus throughput, check the application buffer setup.",
      spcm.ERR_FIFOFINISHED : "ERR_FIFOFINISHED: FIFO transfer has been finished, programmed data length has been transferred completely.",
      spcm.ERR_FIFOSETUP : "ERR_FIFOSETUP",
      spcm.ERR_TIMESTAMP_SYNC : "ERR_TIMESTAMP_SYNC: Synchronization to timestamp reference clock failed. Please check the connection and the signal levels of the reference clock input.",
      spcm.ERR_STARHUB : "ERR_STARHUB: The auto routing function of the Star-Hub initialization has failed. Please check whether all cables are mounted correctly",
      spcm.ERR_INTERNAL_ERROR : "ERR_INTERNAL_ERROR: Internal hardware error detected. Please check for driver and firmware update of the card."
    }
    if error_message_short in error_dictionary:
      error_message_short = error_dictionary[error_message_short]
    raise exception_type(f"Spectrum Instruments device error {error_message}:\n{'Remote' if is_remote else 'Local'} device error.\n{error_message_short}")

  # DLL -------------------------------------------------------------------------
  # =============================================================================
  
  def _get_int32(self, address):
    if not self.is_alive:
      raise Exception("Hardware not defined.")
    response = spcm.int32(0)
    self._handle_error(spcm.spcm_dwGetParam_i32(self.card_handle, address, spcm.byref(response)))
    return response.value

  def _set_int32(self, address, message):
    if not self.is_alive:
      raise Exception("Hardware not defined.")
    self._handle_error(spcm.spcm_dwSetParam_i32(self.card_handle, address, spcm.int32(message)))

  def _get_int64(self, address):
    if not self.is_alive:
      raise Exception("Hardware not defined.")
    response = spcm.int64(0)
    self._handle_error(spcm.spcm_dwGetParam_i64(self.card_handle, address, spcm.byref(response)))
    return response.value

  def _set_int64(self, address, message):
    if not self.is_alive:
      raise Exception("Hardware not defined.")
    self._handle_error(spcm.spcm_dwSetParam_i64(self.card_handle, address, spcm.int64(message)))

  def _transfer_array_i64(self, buffer_type, direction, notify_size, host_address, device_address, data_size):
    self._handle_error(spcm.spcm_dwDefTransfer_i64(self.card_handle, buffer_type, direction, notify_size, host_address, device_address, data_size))

  # Identity --------------------------------------------------------------------
  # =============================================================================
  
  def get_card_type(self):
    """
    Reads raw data from :obj:`SPC_PCITYP`.
    For decoded information, use :obj:`get_name` and :obj:`get_series_information` instead.

    Returns
    -------
    bit_type : :obj:`int`
      Bit code for card type.
    """
    return self._get_int32(spcm.SPC_PCITYP)
  
  def get_name(self):
    """
    Reads :obj:`SPC_PCITYP` to find the name of the card.

    Returns
    -------
    name : :obj:`str`
      Name of the card.
    """
    return spcm_tools.szTypeToName(self.get_card_type())
  
  def get_series(self):
    """
    Reads raw data from :obj:`SPC_PCITYP`.
    For decoded information, use :obj:`get_series_information` instead.

    Returns
    -------
    bit_series : :obj:`int`
      Bit code for card series.
    """
    response = self._get_int32(spcm.SPC_PCITYP)
    return response & spcm.TYP_SERIESMASK
  
  def get_series_information(self):
    """
    Reads :obj:`SPC_PCITYP` to find the series of the card.

    Returns
    -------
    Series : :obj:`str`
      Series of the card.
    """
    series = self.get_series()
    if series == spcm.TYP_MISERIES:
      return "MI"
    elif series == spcm.TYP_MCSERIES:
      return "MC"
    elif series == spcm.TYP_MXSERIES:
      return "MX"
    elif series == spcm.TYP_M2ISERIES:
      return "M2i"
    elif series == spcm.TYP_M2IEXPSERIES:
      return "M2i Express"
    elif series == spcm.TYP_M3ISERIES:
      return "M3i"
    elif series == spcm.TYP_M3IEXPSERIES:
      return "M3i Express"
    elif series == spcm.TYP_M4IEXPSERIES:
      return "M4i Express"
    elif series == spcm.TYP_M4XEXPSERIES:
      return "M4x Express"
    elif series == spcm.TYP_M2PEXPSERIES:
      return "M4p Express"
    elif series == spcm.TYP_M5IEXPSERIES:
      return "M4i Express"
  
  def get_serial_number(self):
    """
    Reads :obj:`SPC_PCISERIALNO` to find the series of the card.

    Returns
    -------
    serial_number : :obj:`int`
      Serial number of the card.
    """
    return self._get_int32(spcm.SPC_PCISERIALNO)
  
  def get_production_date(self):
    """
    Reads raw data from :obj:`SPC_PCIDATE`.
    For decoded information, use :obj:`get_production_date_information` instead.

    Returns
    -------
    bit_date : :obj:`int`
      Bit code for production date.
    """
    return self._get_int32(spcm.SPC_PCIDATE)
  
  def get_production_date_information(self):
    """
    Reads :obj:`SPC_PCIDATE` to find the production date of the card.

    Returns
    -------
    date : :obj:`dict`
      Contains two entries:
      :obj:`"Year"` is an :obj:`int` which contains the year the card was produced.
      :obj:`"Week"` is an :obj:`int` which contains the week of the year the card was produced.
    """
    bitmap = self.get_production_date()
    return {"Week":(bitmap>>16), "Year":(bitmap & 0xFFFF)}
  
  def get_calibration_date(self):
    """
    Reads raw data from :obj:`SPC_CALIBDATE`.
    For decoded information, use :obj:`get_calibration_date_information` instead.

    Returns
    -------
    bit_date : :obj:`int`
      Bit code for production date.
    """
    return self._get_int32(spcm.SPC_CALIBDATE)
  
  def get_calibration_date_information(self):
    """
    Reads :obj:`SPC_CALIBDATE` to find the calibration date of the card.

    Returns
    -------
    date : :obj:`dict`
      Contains two entries:
      :obj:`"Year"` is an :obj:`int` which contains the year the card was calibrated.
      :obj:`"Week"` is an :obj:`int` which contains the week of the year the card was calibrated.
    """
    bitmap = self.get_calibration_date()
    return {"Week":(bitmap>>16), "Year":(bitmap & 0xFFFF)}
  
  def get_is_demo_card(self):
    """
    Reads :obj:`SPC_MIINST_ISDEMOCARD` to find out if the card is a "demo" card (i.e., a software emulation).

    Returns
    -------
    is_demo : :obj:`int`
      :obj:`1` if the card is a demo, otherwise :obj:`0`.
    """
    return self._get_int32(spcm.SPC_MIINST_ISDEMOCARD)
  
  def set_card_identification(self, value):
    """
    Writes to :obj:`SPC_CARDIDENTIFICATION` to set or unset the card's notification LED to identification mode.
    You may want to use :obj:`identification_led_enable` and :obj:`identification_led_disable` instead.

    Parameters
    ----------
    value : :obj:`int`
      :obj:`1` to get the LED to flash, otherwise :obj:`0`.
    """
    self._set_int32(spcm.SPC_CARDIDENTIFICATION, value)

  def identification_led_enable(self):
    """
    Writes to :obj:`SPC_CARDIDENTIFICATION` to set the card's notification LED to identification mode.
    """
    self.set_card_identification(1)

  def identification_led_disable(self):
    """
    Writes to :obj:`SPC_CARDIDENTIFICATION` to set the card's notification LED to normal mode.
    """
    self.set_card_identification(0)

  def get_card_identification(self):
    """
    Reads :obj:`SPC_CARDIDENTIFICATION` to see if the card's notification LED is in identification mode.

    Returns
    -------
    value : :obj:`int`
      :obj:`1` if the LED is flashing, otherwise :obj:`0`.
    """
    return self._get_int32(spcm.SPC_CARDIDENTIFICATION)

  
  # Card information ------------------------------------------------------------
  # =============================================================================
  
  def get_number_of_front_end_modules(self):
    """
    Reads :obj:`SPC_MIINST_MODULES`.

    Returns
    -------
    number : :obj:`int`
    """
    return self._get_int32(spcm.SPC_MIINST_MODULES)
  
  def get_number_of_channels_per_front_end_module(self):
    """
    Reads :obj:`SPC_MIINST_CHPERMODULE`.

    Returns
    -------
    number : :obj:`int`
    """
    return self._get_int32(spcm.SPC_MIINST_CHPERMODULE)
  
  def get_adc_full_scale(self):
    """
    Reads :obj:`SPC_MIINST_MAXADCVALUE`.

    Returns
    -------
    full_scale : :obj:`int`
    """
    return self._get_int32(spcm.SPC_MIINST_MAXADCVALUE)
  
  def get_min_external_clock(self):
    """
    Reads :obj:`SPC_MIINST_MINEXTCLOCK`.

    Returns
    -------
    frequency : :obj:`int`
      Minimum allowed external clock frequency in Hz.
    """
    return self._get_int32(spcm.SPC_MIINST_MINEXTCLOCK)
  
  def get_max_external_clock(self):
    """
    Reads :obj:`SPC_MIINST_MAXEXTCLOCK`.

    Returns
    -------
    frequency : :obj:`int`
      Maximum allowed external clock frequency in Hz.
    """
    return self._get_int32(spcm.SPC_MIINST_MAXEXTCLOCK)
  
  def get_min_external_reference_clock(self):
    """
    Reads :obj:`SPC_MIINST_MINEXTREFCLOCK`.

    Returns
    -------
    frequency : :obj:`int`
      Minimum allowed reference clock frequency in Hz.
    """
    return self._get_int32(spcm.SPC_MIINST_MINEXTREFCLOCK)
  
  def get_max_external_reference_clock(self):
    """
    Reads :obj:`SPC_MIINST_MAXEXTREFCLOCK`.

    Returns
    -------
    frequency : :obj:`int`
      Maximum allowed reference clock frequency in Hz.
    """
    return self._get_int32(spcm.SPC_MIINST_MAXEXTREFCLOCK)
  
  # Temperature -----------------------------------------------------------------
  # =============================================================================
  
  def get_temperature_base(self, unit = "C"):
    """
    Reads :obj:`SPC_MON_TK_BASE_CTRL`, :obj:`SPC_MON_TC_BASE_CTRL` or :obj:`SPC_MON_TF_BASE_CTRL`.

    Parameters
    ----------
    unit : :obj:`str`
      Either :obj:`"K"` for temperature in Kelvin, :obj:`"C"` for temperature in Celsius (default), or :obj:`"F"` for temperature in Fahrenheit.

    Returns
    -------
    temperature : :obj:`int`
      Temperature in the unit selected (defaulting to Celsius).
    """
    if unit == "K":
      unit_offset = 0
    if unit == "C":
      unit_offset = 1
    if unit == "F":
      unit_offset = 2
    return self._get_int32(spcm.SPC_MON_TK_BASE_CTRL + (spcm.SPC_MON_TC_BASE_CTRL - spcm.SPC_MON_TK_BASE_CTRL)*unit_offset)
  
  def get_temperature_module_0(self, unit = "C"):
    """
    Reads :obj:`SPC_MON_TK_MODULE_0`, :obj:`SPC_MON_TC_MODULE_0` or :obj:`SPC_MON_TF_MODULE_0`.

    Parameters
    ----------
    unit : :obj:`str`
      Either :obj:`"K"` for temperature in Kelvin, :obj:`"C"` for temperature in Celsius (default), or :obj:`"F"` for temperature in Fahrenheit.

    Returns
    -------
    temperature : :obj:`int`
      Temperature in the unit selected (defaulting to Celsius).
    """
    if unit == "K":
      unit_offset = 0
    if unit == "C":
      unit_offset = 1
    if unit == "F":
      unit_offset = 2
    return self._get_int32(spcm.SPC_MON_TK_MODULE_0 + (spcm.SPC_MON_TC_BASE_CTRL - spcm.SPC_MON_TK_BASE_CTRL)*unit_offset)
  
  def get_temperature_module_1(self, unit = "C"):
    """
    Reads :obj:`SPC_MON_TK_MODULE_1`, :obj:`SPC_MON_TC_MODULE_1` or :obj:`SPC_MON_TF_MODULE_1`.

    Parameters
    ----------
    unit : :obj:`str`
      Either :obj:`"K"` for temperature in Kelvin, :obj:`"C"` for temperature in Celsius (default), or :obj:`"F"` for temperature in Fahrenheit.

    Returns
    -------
    temperature : :obj:`int`
      Temperature in the unit selected (defaulting to Celsius).
    """
    if unit == "K":
      unit_offset = 0
    if unit == "C":
      unit_offset = 1
    if unit == "F":
      unit_offset = 2
    return self._get_int32(spcm.SPC_MON_TK_MODULE_1 + (spcm.SPC_MON_TC_BASE_CTRL - spcm.SPC_MON_TK_BASE_CTRL)*unit_offset)

  # Hardware and PCB version ----------------------------------------------------
  # =============================================================================
  
  def get_pci_version(self):
    """
    Reads :obj:`SPC_PCIVERSION`.
    For decoded information, use :obj:`get_pci_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for PCI version
    """
    return self._get_int32(spcm.SPC_PCIVERSION)
  
  def get_pci_information(self):
    """
    Reads :obj:`SPC_PCIVERSION` and displays as a :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Hardware version"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_pci_version()
    return {"Hardware version":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_base_pcb_version(self):
    """
    Reads :obj:`SPC_BASEPCBVERSION`.
    For decoded information, use :obj:`get_base_pcb_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for PCB version
    """
    return self._get_int32(spcm.SPC_BASEPCBVERSION)
  
  def get_base_pcb_information(self):
    """
    Reads :obj:`SPC_BASEPCBVERSION` and displays as a :obj:`str`.

    Returns
    -------
    version : :obj:`str`
      Version in :obj:`str` format.
    """
    bitmap = self.get_base_pcb_version()
    return f"{bitmap >> 8}.{bitmap & 0xFF}"
  
  def get_module_pci_version(self):
    """
    Reads :obj:`SPC_PCIMODULEVERSION`.
    For decoded information, use :obj:`get_module_pci_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for module PCI version
    """
    return self._get_int32(spcm.SPC_PCIMODULEVERSION)
  
  def get_module_pci_information(self):
    """
    Reads :obj:`SPC_PCIMODULEVERSION` and displays as a :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Hardware version"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_module_pci_version()
    return {"Hardware version":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_module_pcb_version(self):
    """
    Reads :obj:`SPC_MODULEPCBVERSION`.
    For decoded information, use :obj:`get_module_pcb_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for module PCB version
    """
    return self._get_int32(spcm.SPC_MODULEPCBVERSION)
  
  def get_module_pcb_information(self):
    """
    Reads :obj:`SPC_MODULEPCBVERSION` and displays as a :obj:`str`.

    Returns
    -------
    version : :obj:`str`
      Version in :obj:`str` format.
    """
    bitmap = self.get_module_pcb_version()
    return f"{bitmap >> 8}.{bitmap & 0xFF}"
  
  def get_extension_pci_version(self):
    """
    Reads :obj:`SPC_PCIEXTVERSION`.
    For decoded information, use :obj:`get_extension_pci_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for extension PCI version
    """
    return self._get_int32(spcm.SPC_PCIEXTVERSION)
  
  def get_extension_pci_information(self):
    """
    Reads :obj:`SPC_PCIEXTVERSION` and displays as a :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Hardware version"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_extension_pci_version()
    return {"Hardware version":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_extension_pcb_version(self):
    """
    Reads :obj:`SPC_EXTPCBVERSION`.
    For decoded information, use :obj:`get_module_pcb_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code for extension PCB version
    """
    return self._get_int32(spcm.SPC_EXTPCBVERSION)
  
  def get_extension_pcb_information(self):
    """
    Reads :obj:`SPC_EXTPCBVERSION` and displays as a :obj:`str`.

    Returns
    -------
    version : :obj:`str`
      Version in :obj:`str` format.
    """
    bitmap = self.get_extension_pcb_version()
    return f"{bitmap >> 8}.{bitmap & 0xFF}"
  
  def get_pxi_slot_number(self):
    """
    Reads :obj:`SPC_PXIHWSLOTNO`.

    Returns
    -------
    number : :obj:`str`
      PXI slot number.
    """
    return self._get_int32(spcm.SPC_PXIHWSLOTNO)
  
  # Firmware information --------------------------------------------------------
  # =============================================================================
  
  def get_firmware_version_control(self):
    """
    Reads :obj:`SPCM_FW_CTRL`.
    For decoded information, use :obj:`get_firmware_version_control_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_CTRL)
  
  def get_firmware_version_control_information(self):
    """
    Reads :obj:`SPCM_FW_CTRL` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_control()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_control_golden(self):
    """
    Reads :obj:`SPCM_FW_CTRL_GOLDEN`.
    For decoded information, use :obj:`get_firmware_version_control_golden_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_CTRL_GOLDEN)
  
  def get_firmware_version_control_golden_information(self):
    """
    Reads :obj:`SPCM_FW_CTRL_GOLDEN` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_control_golden()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_control_active(self):
    """
    Reads :obj:`SPCM_FW_CTRL_ACTIVE`.
    For decoded information, use :obj:`get_firmware_version_control_active_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_CTRL_ACTIVE)
  
  def get_firmware_version_control_active_information(self):
    """
    Reads :obj:`SPCM_FW_CTRL_ACTIVE` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_control_active()
    return {"Firmware type":(bitmap >> 28), "Firmware version":((bitmap >> 16) & 0xFFF)}
  
  def get_firmware_version_clock(self):
    """
    Reads :obj:`SPCM_FW_CLOCK`.
    For decoded information, use :obj:`get_firmware_version_clock_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_CLOCK)
  
  def get_firmware_version_clock_information(self):
    """
    Reads :obj:`SPCM_FW_CLOCK` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_clock()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_configuration(self):
    """
    Reads :obj:`SPCM_FW_CONFIG`.
    For decoded information, use :obj:`get_firmware_version_configuration_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_CONFIG)
  
  def get_firmware_version_configuration_information(self):
    """
    Reads :obj:`SPCM_FW_CONFIG` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_configuration()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_module_a(self):
    """
    Reads :obj:`SPCM_FW_MODULEA`.
    For decoded information, use :obj:`get_firmware_version_module_a_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_MODULEA)
  
  def get_firmware_version_module_a_information(self):
    """
    Reads :obj:`SPCM_FW_MODULEA` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_module_a()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_module_b(self):
    """
    Reads :obj:`SPCM_FW_MODULEB`.
    For decoded information, use :obj:`get_firmware_version_module_b_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_MODULEB)
  
  def get_firmware_version_module_b_information(self):
    """
    Reads :obj:`SPCM_FW_MODULEB` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_module_b()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_module_star(self):
    """
    Reads :obj:`SPCM_FW_MODEXTRA`.
    For decoded information, use :obj:`get_firmware_version_module_star_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_MODEXTRA)
  
  def get_firmware_version_module_star_information(self):
    """
    Reads :obj:`SPCM_FW_MODEXTRA` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_module_star()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}
  
  def get_firmware_version_power(self):
    """
    Reads :obj:`SPCM_FW_POWER`.
    For decoded information, use :obj:`get_firmware_version_power_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_FW_POWER)
  
  def get_firmware_version_power_information(self):
    """
    Reads :obj:`SPCM_FW_POWER` and displays as :obj:`dict`.

    Returns
    -------
    version : :obj:`dict`
      Contains two entries: :obj:`"Firmware type"` and :obj:`"Firmware version"`.
    """
    bitmap = self.get_firmware_version_power()
    return {"Firmware type":(bitmap >> 16), "Firmware version":bitmap & 0xFFFF}

  # Driver information ----------------------------------------------------------
  # =============================================================================
  
  def get_driver(self):
    """
    Reads :obj:`SPC_GETDRVTYPE`.
    For decoded information, use :obj:`get_driver_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_GETDRVTYPE)
  
  def get_driver_information(self):
    """
    Reads :obj:`SPC_GETDRVTYPE` and displays in :obj:`str` format.

    Returns
    -------
    version : :obj:`str`
      Name of driver.
    """
    driver = self.get_driver()
    if driver == spcm.DRVTYP_LINUX32:
      return "32 bit Linux"
    if driver == spcm.DRVTYP_LINUX64:
      return "64 bit Linux"
    if driver == spcm.DRVTYP_WDM32:
      return "32 bit Windows"
    if driver == spcm.DRVTYP_WDM64:
      return "64 bit Windows"
    if driver == spcm.DRVTYP_WOW64:
      return "64 bit Windows, used by 32 bit application"
    
  def get_driver_version(self):
    """
    Reads :obj:`SPC_GETDRVVERSION`.
    For decoded information, use :obj:`get_driver_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_GETDRVVERSION)
  
  def get_driver_version_information(self):
    """
    Reads :obj:`SPC_GETDRVVERSION` and displays in :obj:`str` format.

    Returns
    -------
    version : :obj:`str`
      Version of driver
    """
    driver_version = self.get_driver_version()
    return f"{driver_version >> 24}.{(driver_version >> 16) & 0xFF} build {(driver_version) & 0xFFFF}"
  
  def get_kernel_version(self):
    """
    Reads :obj:`SPC_GETKERNELVERSION`.
    For decoded information, use :obj:`get_driver_information` instead.

    Returns
    -------
    version : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_GETKERNELVERSION)
  
  def get_kernel_version_information(self):
    """
    Reads :obj:`SPC_GETKERNELVERSION` and displays in :obj:`str` format.

    Returns
    -------
    version : :obj:`str`
      Version of driver
    """
    kernel_version = self.get_kernel_version()
    return f"{kernel_version >> 24}.{(kernel_version >> 16) & 0xFF} build {(kernel_version) & 0xFFFF}"
  
  # Modifications ---------------------------------------------------------------
  # =============================================================================
  
  def get_modifications(self):
    """
    Reads :obj:`SPCM_CUSTOMMOD`.
    For decoded information, use :obj:`get_modifications_information` instead.

    Returns
    -------
    modifications : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_CUSTOMMOD)

  def get_modifications_information(self):
    """
    Reads :obj:`SPCM_CUSTOMMOD` and displays in :obj:`dict` format.

    Returns
    -------
    modifications : :obj:`dict`
      Contains three entries for modifications for different parts of the card: :obj:`"Card"`, :obj:`"Front-end"`, and :obj:`"Star-hub"`.
    """
    modifications = self.get_modifications()
    return {
      "Card":(modifications & 0xFF),
      "Front-end":((modifications >> 8) & 0xFF),
      "Star-hub":((modifications >> 16) & 0xFF)
    }

  # Features and functions ------------------------------------------------------
  # =============================================================================
  
  def get_features(self):
    """
    Reads :obj:`SPC_PCIFEATURES`.
    For decoded information, use :obj:`get_features_information` instead.

    Returns
    -------
    features : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_PCIFEATURES)
  
  def get_extended_features(self):
    """
    Reads :obj:`SPC_PCIEXTFEATURES`.
    For decoded information, use :obj:`get_features_information` instead.

    Returns
    -------
    features : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_PCIEXTFEATURES)
  
  def get_readout_features(self):
    """
    Reads :obj:`SPC_READAOFEATURES`.
    For decoded information, use :obj:`get_features_information` instead.

    Returns
    -------
    features : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_READAOFEATURES)
  
  def get_features_information(self):
    """
    Reads :obj:`SPC_PCIFEATURES`, :obj:`SPC_PCIEXTFEATURES`, :obj:`SPC_READAOFEATURES`, and :obj:`SPC_SEQMODE_AVAILFEATURES` and displays each feature of the card in a list.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each available feature written as a :obj:`str`.
    """
    bitmap = self.get_features()
    features = []
    if bitmap & spcm.SPCM_FEAT_MULTI:
      features.append("Multiple recording/replay")
    if bitmap & spcm.SPCM_FEAT_GATE:
      features.append("Gated sampling/replay")
    if bitmap & spcm.SPCM_FEAT_DIGITAL:
      features.append("Digital input/output")
    if bitmap & spcm.SPCM_FEAT_TIMESTAMP:
      features.append("Timestamp")
    if bitmap & spcm.SPCM_FEAT_STARHUB6_EXTM:
      features.append("6 card star-hub extension/piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB8_EXTM:
      features.append("8 card star-hub extension/piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB16_EXTM:
      features.append("16 card star-hub extension/piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB4:
      features.append("4 card star-hub piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB5:
      features.append("5 card star-hub piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB8:
      features.append("8 card star-hub piggyback")
    if bitmap & spcm.SPCM_FEAT_STARHUB16:
      features.append("16 card star-hub piggyback")
    if bitmap & spcm.SPCM_FEAT_ABA:
      features.append("ABA mode")
    if bitmap & spcm.SPCM_FEAT_BASEXIO:
      features.append("Base XIO option")
    if bitmap & spcm.SPCM_FEAT_AMPLIFIER_10V:
      features.append("10 V amplifier calibration")
    if bitmap & spcm.SPCM_FEAT_STARHUBSYSMASTER:
      features.append("Master star-hub card")
    if bitmap & spcm.SPCM_FEAT_STARHUBSYSSLAVE:
      features.append("Slave star-hub card")
    if bitmap & spcm.SPCM_FEAT_DIFFMODE:
      features.append("Differential mode")
    if bitmap & spcm.SPCM_FEAT_SEQUENCE:
      features.append("Sequence mode")
    if bitmap & spcm.SPCM_FEAT_AMPMODULE_10V:
      features.append("10 V amplifier module")
    if bitmap & spcm.SPCM_FEAT_NETBOX:
      features.append("NETBOX")
    if bitmap & spcm.SPCM_FEAT_REMOTESERVER:
      features.append("Remote server option")
    if bitmap & spcm.SPCM_FEAT_SCAPP:
      features.append("SCAPP option")
    if bitmap & spcm.SPCM_FEAT_DIG16_SMB:
      features.append("Additional SMB connectors")
    if bitmap & spcm.SPCM_FEAT_DIG16_FX2:
      features.append("Additional FX2 connectors")
    if bitmap & spcm.SPCM_FEAT_DIGITALBWFILTER:
      features.append("Bandwidth filter")
    if bitmap & spcm.SPCM_FEAT_CUSTOMMOD_MASK:
      features.append(f"Custom modification {bitmap >> 28}")

    bitmap = self.get_extended_features()
    if bitmap & spcm.SPCM_FEAT_EXTFW_SEGSTAT:
      features.append("Block statistics firmware option")
    if bitmap & spcm.SPCM_FEAT_EXTFW_SEGAVERAGE:
      features.append("Block average firmware option")
    if bitmap & spcm.SPCM_FEAT_EXTFW_BOXCAR:
      features.append("Boxcar average firmware option")

    SPCM_AO_SET = 0x00000002
    SPCM_AO_DIFF = 0x00000004
    SPCM_AO_PROGFILTER = 0x00000008
    SPCM_AO_PROGOFFSET = 0x00000010
    SPCM_AO_PROGGAIN = 0x00000020
    SPCM_AO_PROGSTOPLEVEL = 0x00000040
    SPCM_AO_DOUBLEOUT = 0x00000080
    SPCM_AO_ENABLEOUT = 0x00000100
    bitmap = self.get_readout_features()
    if bitmap & SPCM_AO_SET:
      features.append("Single ended output")
    if bitmap & SPCM_AO_DIFF:
      features.append("Differential output")
    if bitmap & SPCM_AO_PROGFILTER:
      features.append("Output filters")
    if bitmap & SPCM_AO_PROGOFFSET:
      features.append("Programmable output offset")
    if bitmap & SPCM_AO_PROGGAIN:
      features.append("Programmable output gain")
    if bitmap & SPCM_AO_PROGSTOPLEVEL:
      features.append("Programmable output stop level")
    if bitmap & SPCM_AO_DOUBLEOUT:
      features.append("Double output")
    if bitmap & SPCM_AO_ENABLEOUT:
      features.append("Output enable functions")

    bitmap = self.get_available_sequence_features()
    if bitmap & spcm.SPCSEQ_ENDLOOPONTRIG:
      features.append("Loop step until trigger")
    if bitmap & spcm.SPCSEQ_END:
      features.append("Final step")
    
    return features
  
  def get_functions(self):
    """
    Reads :obj:`SPC_FNCTYPE`.
    For decoded information, use :obj:`get_functions_information` instead.

    Returns
    -------
    features : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_FNCTYPE)
  
  def get_functions_information(self):
    """
    Reads :obj:`SPC_FNCTYP` and displays each function of the card in a list.

    Returns
    -------
    functions : :obj:`list` of :obj:`str`
      A list of each available function written as a :obj:`str`.
    """
    bitmap = self.get_functions()
    functions = []
    if bitmap & spcm.SPCM_TYPE_AI:
      functions.append("Analogue input")
    if bitmap & spcm.SPCM_TYPE_AO:
      functions.append("Analogue output")
    if bitmap & spcm.SPCM_TYPE_DI:
      functions.append("Digital input")
    if bitmap & spcm.SPCM_TYPE_DO:
      functions.append("Digital output")
    if bitmap & spcm.SPCM_TYPE_DIO:
      functions.append("Digital input/output")
    return functions
  
  # Card mode -------------------------------------------------------------------
  # =============================================================================
  
  def set_mode(self, mode):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card.
    To do this without using bit codes, use :obj:`use_mode_single`, :obj:`use_mode_multi`, :obj:`use_mode_gate`, :obj:`use_mode_single_restart`, :obj:`use_mode_sequence`, :obj:`use_mode_fifo_single`, :obj:`use_mode_fifo_multi`, or :obj:`use_mode_fifo_gate` instead.

    Parameters
    ----------
    features : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_CARDMODE, mode)

  def use_mode_single(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_STD_SINGLE`.
    """
    self.set_mode(spcm.SPC_REP_STD_SINGLE)
  
  def use_mode_multi(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_STD_MULTI`.
    """
    self.set_mode(spcm.SPC_REP_STD_MULTI)

  def use_mode_gate(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_STD_GATE`.
    """
    self.set_mode(spcm.SPC_REP_STD_GATE)

  def use_mode_single_restart(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_STD_SINGLERESTART`.
    """
    self.set_mode(spcm.SPC_REP_STD_SINGLERESTART)

  def use_mode_sequence(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_STD_SEQUENCE`.
    """
    self.set_mode(spcm.SPC_REP_STD_SEQUENCE)

  def use_mode_fifo_single(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_FIFO_SINGLE`.
    """
    self.set_mode(spcm.SPC_REP_FIFO_SINGLE)
  
  def use_mode_fifo_multi(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_FIFO_MULTI`.
    """
    self.set_mode(spcm.SPC_REP_FIFO_MULTI)

  def use_mode_fifo_gate(self):
    """
    Writes to :obj:`SPC_CARDMODE` to set the mode of the card to :obj:`SPC_REP_FIFO_GATE`.
    """
    self.set_mode(spcm.SPC_REP_FIFO_GATE)

  def get_mode(self):
    """
    Reads :obj:`SPC_CARDMODE` to find the current mode that the card is in.
    For decoded information, use :obj:`get_mode_information` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_CARDMODE)
  
  def get_mode_information(self):
    """
    Reads :obj:`SPC_CARDMODE` and displays the current card mode as a :obj:`str`.

    Returns
    -------
    mode : :obj:`str`
      The mode the card is in as a :obj:`str`.
    """
    mode = self.get_mode()
    if mode & spcm.SPC_REP_STD_SINGLE:
      return "Single"
    if mode & spcm.SPC_REP_STD_MULTI:
      return "Multi"
    if mode & spcm.SPC_REP_STD_GATE:
      return "Gate"
    if mode & spcm.SPC_REP_STD_SINGLERESTART:
      return "Single restart"
    if mode & spcm.SPC_REP_STD_SEQUENCE:
      return "Sequence"
    if mode & spcm.SPC_REP_FIFO_SINGLE:
      return "FIFO single"
    if mode & spcm.SPC_REP_FIFO_MULTI:
      return "FIFO multi"
    if mode & spcm.SPC_REP_FIFO_GATE:
      return "FIFO gate"
    
  def get_available_modes(self):
    """
    Reads :obj:`SPC_AVAILCARDMODES`.
    For decoded information, use :obj:`get_available_modes_information` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_AVAILCARDMODES)
  
  def get_available_modes_information(self):
    """
    Reads :obj:`SPC_AVAILCARDMODES` and displays each available mode for the card in a list.

    Returns
    -------
    modes : :obj:`list` of :obj:`str`
      A list of each available mode written as a :obj:`str`.
    """
    mode = self.get_available_modes()
    modes = []
    if mode & spcm.SPC_REP_STD_SINGLE:
      modes.append("Single")
    if mode & spcm.SPC_REP_STD_MULTI:
      modes.append("Multi")
    if mode & spcm.SPC_REP_STD_GATE:
      modes.append("Gate")
    if mode & spcm.SPC_REP_STD_SINGLERESTART:
      modes.append("Single restart")
    if mode & spcm.SPC_REP_STD_SEQUENCE:
      modes.append("Sequence")
    if mode & spcm.SPC_REP_FIFO_SINGLE:
      modes.append("FIFO single")
    if mode & spcm.SPC_REP_FIFO_MULTI:
      modes.append("FIFO multi")
    if mode & spcm.SPC_REP_FIFO_GATE:
      modes.append("FIFO gate")
    return modes

  # Sample rate -----------------------------------------------------------------
  # =============================================================================
  
  def set_sample_rate(self, sample_rate, multiplier = ""):
    """
    Writes a sample rate to :obj:`SPC_SAMPLERATE`.

    Parameters
    ----------
    sample_rate : :obj:`int`
      The sample rate in S/s.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), :obj:`"k"`, :obj:`"M"` or :obj:`"G"`.
    """
    if multiplier == "k":
      sample_rate *= 1e3
    elif multiplier == "M":
      sample_rate *= 1e6
    elif multiplier == "G":
      sample_rate *= 1e9
    elif multiplier != "":
      raise ValueError("multiplier must be either \"k\", \"M\", \"G\" or \"\".")
    self._set_int64(spcm.SPC_SAMPLERATE, int(sample_rate))

  def get_sample_rate(self):
    """
    Reads :obj:`SPC_SAMPLERATE`.

    Returns
    -------
    sample_rate : :obj:`int`
      The current sample rate in Sa/s.
    """
    return self._get_int64(spcm.SPC_SAMPLERATE)

  def get_max_sample_rate(self):
    """
    Reads :obj:`SPC_PCISAMPLERATE`.

    Returns
    -------
    sample_rate : :obj:`int`
      The card's maximum sample rate in Sa/s.
    """
    return self._get_int64(spcm.SPC_PCISAMPLERATE)
  
  def get_sample_resolution(self):
    """
    Reads :obj:`SPC_MIINST_BYTESPERSAMPLE`.

    Returns
    -------
    resolution : :obj:`int`
      The resolution of each sample in Bytes/sample.
    """
    return self._get_int32(spcm.SPC_MIINST_BYTESPERSAMPLE)
  
  def get_sample_resolution_bits(self):
    """
    Reads :obj:`SPC_MIINST_BITSPERSAMPLE`.

    Returns
    -------
    resolution : :obj:`int`
      The resolution of each sample in bits/sample.
    """
    return self._get_int32(spcm.SPC_MIINST_BITSPERSAMPLE)

  # Clock -----------------------------------------------------------------------
  # =============================================================================
  
  def set_clock_output(self, enable):
    """
    Writes to :obj:`SPC_CLOCKOUT`.
    You may instead want to use :obj:`clock_output_enable` and :obj:`clock_output_disable`.

    Parameters
    ----------
    enable : :obj:`int`
      :obj:`1` if output is enabled, :obj:`0` otherwise.
    """
    self._set_int32(spcm.SPC_CLOCKOUT, enable)

  def clock_output_enable(self):
    """
    Writes to :obj:`SPC_CLOCKOUT` to enable the clock output.
    """
    self.set_clock_output(1)
  
  def clock_output_disable(self):
    """
    Writes to :obj:`SPC_CLOCKOUT` to disable the clock output.
    """
    self.set_clock_output(0)

  def get_clock_output(self):
    """
    Reads :obj:`SPC_CLOCKOUT`.

    Returns
    -------
    enabled : :obj:`int`
      :obj:`1` if output is enabled, :obj:`0` otherwise.
    """
    return self._get_int32(spcm.SPC_CLOCKOUT)
  
  def get_clock_output_frequency(self):
    """
    Reads :obj:`SPC_CLOCKOUTFREQUENCY`.

    Returns
    -------
    frequency : :obj:`int`
      Output frequency in Hz.
    """
    return self._get_int32(spcm.SPC_CLOCKOUTFREQUENCY)
  
  def set_external_reference_frequency(self, frequency, multiplier = ""):
    """
    Writes to :obj:`SPC_REFERENCECLOCK`.

    Parameters
    ----------
    frequency : :obj:`int`
      Reference frequency in Hz.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), :obj:`"k"`, :obj:`"M"` or :obj:`"G"`.
    """
    if multiplier == "k":
      frequency *= 1e3
    elif multiplier == "M":
      frequency *= 1e6
    elif multiplier == "G":
      frequency *= 1e9
    elif multiplier != "":
      raise ValueError("multiplier must be either \"k\", \"M\", \"G\" or \"\".")
    self._set_int64(spcm.SPC_REFERENCECLOCK, int(frequency))

  def get_external_reference_frequency(self):
    """
    Reads :obj:`SPC_REFERENCECLOCK`.

    Returns
    -------
    frequency : :obj:`int`
      Reference frequency in Hz.
    """
    return self._get_int32(spcm.SPC_REFERENCECLOCK)
  
  def get_available_clock_modes(self):
    """
    Reads :obj:`SPC_AVAILCLOCKMODES`.
    For decoded information, use :obj:`get_available_clock_modes_information` instead.

    Returns
    -------
    modes : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_AVAILCLOCKMODES)
  
  def get_available_clock_modes_information(self):
    """
    Reads :obj:`SPC_AVAILCLOCKMODES` and displays each available mode for the clock in a list.

    Returns
    -------
    modes : :obj:`list` of :obj:`str`
      A list of each available mode written as a :obj:`str`.
    """
    bitmap = self.get_available_clock_modes()
    clock_modes = []
    if bitmap & spcm.SPC_CM_INTPLL:
      clock_modes.append("Primary internal quartz")
    if bitmap & spcm.SPC_CM_QUARTZ2:
      clock_modes.append("Secondary internal quartz")
    if bitmap & spcm.SPC_CM_EXTREFCLOCK:
      clock_modes.append("External reference")
    if bitmap & spcm.SPC_CM_PXIREFCLOCK:
      clock_modes.append("PXIe backplane clock reference")
    return clock_modes

  def set_clock_mode(self, clock_mode):
    """
    Writes to :obj:`SPC_CLOCKMODE`.
    To do this without using bit codes, use :obj:`use_clock_primary_internal`, :obj:`use_clock_secondary_internal`, :obj:`use_clock_external_reference`, or :obj:`use_clock_pxie_reference` instead.

    Parameters
    ----------
    mode : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_CLOCKMODE, clock_mode)

  def use_clock_primary_internal(self):
    """
    Writes :obj:`SPC_CM_INTPLL` to :obj:`SPC_CLOCKMODE`.
    """
    self.set_clock_mode(spcm.SPC_CM_INTPLL)

  def use_clock_secondary_internal(self):
    """
    Writes :obj:`SPC_CM_QUARTZ2` to :obj:`SPC_CLOCKMODE`.
    """
    self.set_clock_mode(spcm.SPC_CM_QUARTZ2)

  def use_clock_external_reference(self):
    """
    Writes :obj:`SPC_CM_EXTREFCLOCK` to :obj:`SPC_CLOCKMODE`.
    """
    self.set_clock_mode(spcm.SPC_CM_EXTREFCLOCK)

  def use_clock_pxie_reference(self):
    """
    Writes :obj:`SPC_CM_PXIREFCLOCK` to :obj:`SPC_CLOCKMODE`.
    """
    self.set_clock_mode(spcm.SPC_CM_PXIREFCLOCK)

  def get_clock_mode(self):
    """
    Reads :obj:`SPC_CLOCKMODE`.
    For decoded information, use :obj:`get_clock_mode_information` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_CLOCKMODE)

  def get_clock_mode_information(self):
    """
    Reads :obj:`SPC_CLOCKMODE` and displays the current clock mode as a string.

    Returns
    -------
    mode : :obj:`str`
      The current clock mode written as a :obj:`str`.
    """
    bitmap = self.get_clock_mode()
    if bitmap == spcm.SPC_CM_INTPLL:
      return "Primary internal quartz"
    if bitmap == spcm.SPC_CM_QUARTZ2:
      return "Secondary internal quartz"
    if bitmap == spcm.SPC_CM_EXTREFCLOCK:
      return "External reference"
    if bitmap == spcm.SPC_CM_PXIREFCLOCK:
      return "PXIe backplane clock reference"

  # Trigger masks ---------------------------------------------------------------
  # =============================================================================

  def set_trigger_or_mask(self, mask):
    """
    Writes to :obj:`SPC_TRIG_ORMASK`.
    To do this without using bit codes, use :obj:`set_sufficient_triggers`.

    Parameters
    ----------
    mask : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_ORMASK, mask)

  def set_sufficient_triggers(
      self,
      software = False,
      external_0 = False,
      external_1 = False,
      # pxi_0 = False,
      # pxi_1 = False,
      # pxi_2 = False,
      # pxi_3 = False,
      # pxi_4 = False,
      # pxi_5 = False,
      # pxi_6 = False,
      # pxi_7 = False,
      # pxi_star = False,
      # pxid_star_b = False
    ):
    """
    Writes to :obj:`SPC_TRIG_ORMASK`.
    Set each parameter to :obj:`True` to add it to the OR mask.
    """
    mask = 0
    if software:
      mask |= spcm.SPC_TMASK_SOFTWARE
    if external_0:
      mask |= spcm.SPC_TMASK_EXT0
    if external_1:
      mask |= spcm.SPC_TMASK_EXT1
    # if pxi_0:
    #   mask |= spcm.SPC_TMASK_PXI0
    # if pxi_1:
    #   mask |= spcm.SPC_TMASK_PXI1
    # if pxi_2:
    #   mask |= spcm.SPC_TMASK_PXI2
    # if pxi_3:
    #   mask |= spcm.SPC_TMASK_PXI3
    # if pxi_4:
    #   mask |= spcm.SPC_TMASK_PXI4
    # if pxi_5:
    #   mask |= spcm.SPC_TMASK_PXI5
    # if pxi_6:
    #   mask |= spcm.SPC_TMASK_PXI6
    # if pxi_7:
    #   mask |= spcm.SPC_TMASK_PXI7
    # if pxi_star:
    #   mask |= spcm.SPC_TMASK_PXISTAR
    # if pxid_star_b:
    #   mask |= spcm.SPC_TMASK_PXIDSTARB
    self.set_trigger_or_mask(mask)

  def get_trigger_or_mask(self):
    """
    Reads :obj:`SPC_TRIG_ORMASK`.
    For decoded information, use :obj:`get_sufficient_triggers` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_ORMASK)
  
  def get_sufficient_triggers(self):
    """
    Reads :obj:`SPC_TRIG_ORMASK` and displays each sufficient trigger in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each sufficient trigger written as a :obj:`str`.
    """
    mask = self.get_trigger_or_mask()
    triggers = []
    if mask & spcm.SPC_TMASK_SOFTWARE:
      triggers.append("Software")
    if mask & spcm.SPC_TMASK_EXT0:
      triggers.append("External 0")
    if mask & spcm.SPC_TMASK_EXT1:
      triggers.append("External 1")
    if mask & spcm.SPC_TMASK_PXI0:
      triggers.append("PXI 0")
    if mask & spcm.SPC_TMASK_PXI1:
      triggers.append("PXI 1")
    if mask & spcm.SPC_TMASK_PXI2:
      triggers.append("PXI 2")
    if mask & spcm.SPC_TMASK_PXI3:
      triggers.append("PXI 3")
    if mask & spcm.SPC_TMASK_PXI4:
      triggers.append("PXI 4")
    if mask & spcm.SPC_TMASK_PXI5:
      triggers.append("PXI 5")
    if mask & spcm.SPC_TMASK_PXI6:
      triggers.append("PXI 6")
    if mask & spcm.SPC_TMASK_PXI7:
      triggers.append("PXI 7")
    if mask & spcm.SPC_TMASK_PXISTAR:
      triggers.append("PXI star")
    if mask & spcm.SPC_TMASK_PXIDSTARB:
      triggers.append("PXID star B")
    return triggers
  
  def get_available_triggers_for_or_mask(self):
    """
    Reads :obj:`SPC_TRIG_AVAILORMASK`.
    For decoded information, use :obj:`get_available_sufficient_triggers` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_AVAILORMASK)

  def get_available_sufficient_triggers(self):
    """
    Reads :obj:`SPC_TRIG_AVAILORMASK` and displays each available sufficient trigger in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each available sufficient trigger written as a :obj:`str`.
    """
    mask = self.get_available_triggers_for_or_mask()
    triggers = []
    if mask & spcm.SPC_TMASK_SOFTWARE:
      triggers.append("Software")
    if mask & spcm.SPC_TMASK_EXT0:
      triggers.append("External 0")
    if mask & spcm.SPC_TMASK_EXT1:
      triggers.append("External 1")
    if mask & spcm.SPC_TMASK_PXI0:
      triggers.append("PXI 0")
    if mask & spcm.SPC_TMASK_PXI1:
      triggers.append("PXI 1")
    if mask & spcm.SPC_TMASK_PXI2:
      triggers.append("PXI 2")
    if mask & spcm.SPC_TMASK_PXI3:
      triggers.append("PXI 3")
    if mask & spcm.SPC_TMASK_PXI4:
      triggers.append("PXI 4")
    if mask & spcm.SPC_TMASK_PXI5:
      triggers.append("PXI 5")
    if mask & spcm.SPC_TMASK_PXI6:
      triggers.append("PXI 6")
    if mask & spcm.SPC_TMASK_PXI7:
      triggers.append("PXI 7")
    if mask & spcm.SPC_TMASK_PXISTAR:
      triggers.append("PXI star")
    if mask & spcm.SPC_TMASK_PXIDSTARB:
      triggers.append("PXID star B")
    return triggers
  
  def set_channels_triggered_by_or_mask(self, mask):
    """
    Writes to :obj:`SPC_TRIG_CH_ORMASK0`.
    To do this without using bit codes, use :obj:`set_channels_for_sufficient_triggers`.

    Parameters
    ----------
    channels : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_CH_ORMASK0, mask)

  def set_channels_for_sufficient_triggers(
      self,
      channel_0 = False,
      channel_1 = False,
      channel_2 = False,
      channel_3 = False,
      channel_4 = False,
      channel_5 = False,
      channel_6 = False,
      channel_7 = False
    ):
    """
    Writes to :obj:`SPC_TRIG_CH_ORMASK0`.
    Set each parameter to :obj:`True` to add the channel to those effected by the OR mask.
    """
    mask = 0
    if channel_0:
      mask |= spcm.SPC_TMASK0_CH0
    if channel_1:
      mask |= spcm.SPC_TMASK0_CH1
    if channel_2:
      mask |= spcm.SPC_TMASK0_CH2
    if channel_3:
      mask |= spcm.SPC_TMASK0_CH3
    if channel_4:
      mask |= spcm.SPC_TMASK0_CH4
    if channel_5:
      mask |= spcm.SPC_TMASK0_CH5
    if channel_6:
      mask |= spcm.SPC_TMASK0_CH6
    if channel_7:
      mask |= spcm.SPC_TMASK0_CH7
    self.set_channels_triggered_by_or_mask(mask)

  def get_channels_triggered_by_or_mask(self):
    """
    Reads :obj:`SPC_TRIG_CH_ORMASK0`.
    For decoded information, use :obj:`get_channels_for_sufficient_triggers` instead.

    Returns
    -------
    channels : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_CH_ORMASK0)
  
  def get_channels_for_sufficient_triggers(self):
    """
    Reads :obj:`SPC_TRIG_CH_ORMASK0` and displays each channel in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each channel written as a :obj:`str`.
    """
    mask = self.get_channels_triggered_by_or_mask()
    channels = []
    if mask & spcm.SPC_TMASK0_CH0:
      channels.append("Channel 0")
    if mask & spcm.SPC_TMASK0_CH1:
      channels.append("Channel 1")
    if mask & spcm.SPC_TMASK0_CH2:
      channels.append("Channel 2")
    if mask & spcm.SPC_TMASK0_CH3:
      channels.append("Channel 3")
    if mask & spcm.SPC_TMASK0_CH4:
      channels.append("Channel 4")
    if mask & spcm.SPC_TMASK0_CH5:
      channels.append("Channel 5")
    if mask & spcm.SPC_TMASK0_CH6:
      channels.append("Channel 6")
    if mask & spcm.SPC_TMASK0_CH7:
      channels.append("Channel 7")
    return channels
  
  def get_available_channels_triggered_by_or_mask(self):
    """
    Reads :obj:`SPC_TRIG_CH_AVAILORMASK0`.
    For decoded information, use :obj:`get_available_channels_for_sufficient_triggers` instead.

    Returns
    -------
    channels : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_CH_AVAILORMASK0)
  
  def get_available_channels_for_sufficient_triggers(self):
    """
    Reads :obj:`SPC_TRIG_CH_AVAILORMASK0` and displays each channel in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each channel written as a :obj:`str`.
    """
    mask = self.get_available_channels_triggered_by_or_mask()
    channels = []
    if mask & spcm.SPC_TMASK0_CH0:
      channels.append("Channel 0")
    if mask & spcm.SPC_TMASK0_CH1:
      channels.append("Channel 1")
    if mask & spcm.SPC_TMASK0_CH2:
      channels.append("Channel 2")
    if mask & spcm.SPC_TMASK0_CH3:
      channels.append("Channel 3")
    if mask & spcm.SPC_TMASK0_CH4:
      channels.append("Channel 4")
    if mask & spcm.SPC_TMASK0_CH5:
      channels.append("Channel 5")
    if mask & spcm.SPC_TMASK0_CH6:
      channels.append("Channel 6")
    if mask & spcm.SPC_TMASK0_CH7:
      channels.append("Channel 7")
    return channels
  
  def set_trigger_and_mask(self, mask):
    """
    Writes to :obj:`SPC_TRIG_ANDMASK`.
    To do this without using bit codes, use :obj:`set_necessary_triggers`.

    Parameters
    ----------
    mask : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_ANDMASK, mask)

  def set_necessary_triggers(
      self,
      external_0 = False,
      external_1 = False,
      # pxi_0 = False,
      # pxi_1 = False,
      # pxi_2 = False,
      # pxi_3 = False,
      # pxi_4 = False,
      # pxi_5 = False,
      # pxi_6 = False,
      # pxi_7 = False,
      # pxi_star = False,
      # pxid_star_b = False
    ):
    """
    Writes to :obj:`SPC_TRIG_ANDMASK`.
    Set each parameter to :obj:`True` to add it to the AND mask.
    """
    mask = 0
    if external_0:
      mask |= spcm.SPC_TMASK_EXT0
    if external_1:
      mask |= spcm.SPC_TMASK_EXT1
    # if pxi_0:
    #   mask |= spcm.SPC_TMASK_PXI0
    # if pxi_1:
    #   mask |= spcm.SPC_TMASK_PXI1
    # if pxi_2:
    #   mask |= spcm.SPC_TMASK_PXI2
    # if pxi_3:
    #   mask |= spcm.SPC_TMASK_PXI3
    # if pxi_4:
    #   mask |= spcm.SPC_TMASK_PXI4
    # if pxi_5:
    #   mask |= spcm.SPC_TMASK_PXI5
    # if pxi_6:
    #   mask |= spcm.SPC_TMASK_PXI6
    # if pxi_7:
    #   mask |= spcm.SPC_TMASK_PXI7
    # if pxi_star:
    #   mask |= spcm.SPC_TMASK_PXISTAR
    # if pxid_star_b:
    #   mask |= spcm.SPC_TMASK_PXIDSTARB
    self.set_trigger_and_mask(mask)

  def get_trigger_and_mask(self):
    """
    Reads :obj:`SPC_TRIG_ANDMASK`.
    For decoded information, use :obj:`get_necessary_triggers` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_ANDMASK)
  
  def get_necessary_triggers(self):
    """
    Reads :obj:`SPC_TRIG_ANDMASK` and displays each necessary trigger in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each necessary trigger written as a :obj:`str`.
    """
    mask = self.get_trigger_and_mask()
    triggers = []
    if mask & spcm.SPC_TMASK_EXT0:
      triggers.append("External 0")
    if mask & spcm.SPC_TMASK_EXT1:
      triggers.append("External 1")
    if mask & spcm.SPC_TMASK_PXI0:
      triggers.append("PXI 0")
    if mask & spcm.SPC_TMASK_PXI1:
      triggers.append("PXI 1")
    if mask & spcm.SPC_TMASK_PXI2:
      triggers.append("PXI 2")
    if mask & spcm.SPC_TMASK_PXI3:
      triggers.append("PXI 3")
    if mask & spcm.SPC_TMASK_PXI4:
      triggers.append("PXI 4")
    if mask & spcm.SPC_TMASK_PXI5:
      triggers.append("PXI 5")
    if mask & spcm.SPC_TMASK_PXI6:
      triggers.append("PXI 6")
    if mask & spcm.SPC_TMASK_PXI7:
      triggers.append("PXI 7")
    if mask & spcm.SPC_TMASK_PXISTAR:
      triggers.append("PXI star")
    if mask & spcm.SPC_TMASK_PXIDSTARB:
      triggers.append("PXID star B")
    return triggers
  
  def get_available_triggers_for_and_mask(self):
    """
    Reads :obj:`SPC_TRIG_AVAILANDMASK`.
    For decoded information, use :obj:`get_available_necessary_triggers` instead.

    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_AVAILANDMASK)
  
  def get_available_necessary_triggers(self):
    """
    Reads :obj:`SPC_TRIG_AVAILANDMASK` and displays each available necessary trigger in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each available necessary trigger written as a :obj:`str`.
    """
    mask = self.get_available_triggers_for_and_mask()
    triggers = []
    if mask & spcm.SPC_TMASK_EXT0:
      triggers.append("External 0")
    if mask & spcm.SPC_TMASK_EXT1:
      triggers.append("External 1")
    if mask & spcm.SPC_TMASK_PXI0:
      triggers.append("PXI 0")
    if mask & spcm.SPC_TMASK_PXI1:
      triggers.append("PXI 1")
    if mask & spcm.SPC_TMASK_PXI2:
      triggers.append("PXI 2")
    if mask & spcm.SPC_TMASK_PXI3:
      triggers.append("PXI 3")
    if mask & spcm.SPC_TMASK_PXI4:
      triggers.append("PXI 4")
    if mask & spcm.SPC_TMASK_PXI5:
      triggers.append("PXI 5")
    if mask & spcm.SPC_TMASK_PXI6:
      triggers.append("PXI 6")
    if mask & spcm.SPC_TMASK_PXI7:
      triggers.append("PXI 7")
    if mask & spcm.SPC_TMASK_PXISTAR:
      triggers.append("PXI star")
    if mask & spcm.SPC_TMASK_PXIDSTARB:
      triggers.append("PXID star B")
    return triggers
  
  def set_channels_triggered_by_and_mask(self, mask):
    """
    Writes to :obj:`SPC_TRIG_CH_ANDMASK0`.
    To do this without using bit codes, use :obj:`set_channels_for_necessary_triggers`.

    Parameters
    ----------
    channels : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_CH_ANDMASK0, mask)

  def set_channels_for_necessary_triggers(
      self,
      channel_0 = False,
      channel_1 = False,
      channel_2 = False,
      channel_3 = False,
      channel_4 = False,
      channel_5 = False,
      channel_6 = False,
      channel_7 = False
    ):
    """
    Writes to :obj:`SPC_TRIG_CH_ANDMASK0`.
    Set each parameter to :obj:`True` to add the channel to those effected by the AND mask.
    """
    mask = 0
    if channel_0:
      mask |= spcm.SPC_TMASK0_CH0
    if channel_1:
      mask |= spcm.SPC_TMASK0_CH1
    if channel_2:
      mask |= spcm.SPC_TMASK0_CH2
    if channel_3:
      mask |= spcm.SPC_TMASK0_CH3
    if channel_4:
      mask |= spcm.SPC_TMASK0_CH4
    if channel_5:
      mask |= spcm.SPC_TMASK0_CH5
    if channel_6:
      mask |= spcm.SPC_TMASK0_CH6
    if channel_7:
      mask |= spcm.SPC_TMASK0_CH7
    self.set_channels_triggered_by_and_mask(mask)

  def get_channels_triggered_by_and_mask(self):
    """
    Reads :obj:`SPC_TRIG_CH_ANDMASK0`.
    For decoded information, use :obj:`get_channels_for_necessary_triggers` instead.

    Returns
    -------
    channels : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_CH_ANDMASK0)
  
  def get_channels_for_necessary_triggers(self):
    """
    Reads :obj:`SPC_TRIG_CH_ANDMASK0` and displays each channel in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each channel written as a :obj:`str`.
    """
    mask = self.get_channels_triggered_by_and_mask()
    channels = []
    if mask & spcm.SPC_TMASK0_CH0:
      channels.append("Channel 0")
    if mask & spcm.SPC_TMASK0_CH1:
      channels.append("Channel 1")
    if mask & spcm.SPC_TMASK0_CH2:
      channels.append("Channel 2")
    if mask & spcm.SPC_TMASK0_CH3:
      channels.append("Channel 3")
    if mask & spcm.SPC_TMASK0_CH4:
      channels.append("Channel 4")
    if mask & spcm.SPC_TMASK0_CH5:
      channels.append("Channel 5")
    if mask & spcm.SPC_TMASK0_CH6:
      channels.append("Channel 6")
    if mask & spcm.SPC_TMASK0_CH7:
      channels.append("Channel 7")
    return channels
  
  def get_available_channels_triggered_by_and_mask(self):
    """
    Reads :obj:`SPC_TRIG_CH_AVAILANDMASK0`.
    For decoded information, use :obj:`get_available_channels_for_necessary_triggers` instead.

    Returns
    -------
    channels : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_CH_AVAILANDMASK0)
  
  def get_available_channels_for_necessary_triggers(self):
    """
    Reads :obj:`SPC_TRIG_CH_AVAILANDMASK0` and displays each channel in a :obj:`list` of :obj:`str`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      A list of each channel written as a :obj:`str`.
    """
    mask = self.get_available_channels_triggered_by_and_mask()
    channels = []
    if mask & spcm.SPC_TMASK0_CH0:
      channels.append("Channel 0")
    if mask & spcm.SPC_TMASK0_CH1:
      channels.append("Channel 1")
    if mask & spcm.SPC_TMASK0_CH2:
      channels.append("Channel 2")
    if mask & spcm.SPC_TMASK0_CH3:
      channels.append("Channel 3")
    if mask & spcm.SPC_TMASK0_CH4:
      channels.append("Channel 4")
    if mask & spcm.SPC_TMASK0_CH5:
      channels.append("Channel 5")
    if mask & spcm.SPC_TMASK0_CH6:
      channels.append("Channel 6")
    if mask & spcm.SPC_TMASK0_CH7:
      channels.append("Channel 7")
    return channels
  
  # Triggers --------------------------------------------------------------------
  # =============================================================================

  def set_trigger_delay(self, delay):
    """
    Writes to :obj:`SPC_TRIG_DELAY`.

    Parameters
    ----------
    delay : :obj:`int`
      Delay in number of samples.
    """
    return self._set_int64(spcm.SPC_TRIG_DELAY, delay)
  
  def get_trigger_delay(self):
    """
    Reads :obj:`SPC_TRIG_DELAY`.

    Returns
    -------
    delay : :obj:`int`
      Delay in number of samples.
    """
    return self._get_int64(spcm.SPC_TRIG_DELAY)
  
  def get_max_trigger_delay(self):
    """
    Reads :obj:`SPC_TRIG_AVAILDELAY`.

    Returns
    -------
    delay : :obj:`int`
      Delay in number of samples.
    """
    return self._get_int64(spcm.SPC_TRIG_AVAILDELAY)

  def set_trigger_input_termination(self, type):
    """
    Writes to :obj:`SPC_TRIG_TERM`.
    To do this without using bit codes, use :obj:`trigger_impedance_use_high` and :obj:`trigger_impedance_use_50`.

    Parameters
    ----------
    type : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_TERM, type)

  def trigger_impedance_use_high(self):
    """
    Writes to :obj:`SPC_TRIG_TERM`.
    Sets impedance to 1 kOhm.
    """
    self.set_trigger_input_termination(1)

  def trigger_impedance_use_50(self):
    """
    Writes to :obj:`SPC_TRIG_TERM`.
    Sets impedance to 50 Ohm.
    """
    self.set_trigger_input_termination(0)

  def get_trigger_input_termination(self):
    """
    Reads :obj:`SPC_TRIG_TERM`.
    For decoded information, use :obj:`get_trigger_impedance` instead.

    Returns
    -------
    type : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_TERM)
  
  def get_trigger_impedance(self):
    """
    Reads :obj:`SPC_TRIG_TERM`.
    Returns either :obj:`"High"` or :obj:`"50 Ohm"`.

    Returns
    -------
    impedance : :obj:`str`
      String of input impedance.
    """
    bit_code = self.get_trigger_input_termination()
    if bit_code == 0:
      return "High"
    if bit_code == 1:
      return "50 Ohm"
    
  def set_trigger_input_coupling(self, trigger_index, type):
    """
    Writes to :obj:`SPC_TRIG_EXT0_ACDC` or :obj:`SPC_TRIG_EXT1_ACDC`.
    To do this without using bit codes, use :obj:`trigger_coupling_use_dc` and :obj:`trigger_coupling_use_ac`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    type : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_EXT0_ACDC + (spcm.SPC_TRIG_EXT1_ACDC - spcm.SPC_TRIG_EXT0_ACDC)*trigger_index, type)

  def trigger_coupling_use_dc(self, trigger_index = 1):
    """
    Writes to :obj:`SPC_TRIG_EXT0_ACDC` or :obj:`SPC_TRIG_EXT1_ACDC`.
    Sets trigger coupling to dc.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    """
    self.set_trigger_input_coupling(trigger_index, 0)

  def trigger_coupling_use_ac(self, trigger_index = 1):
    """
    Writes to :obj:`SPC_TRIG_EXT0_ACDC` or :obj:`SPC_TRIG_EXT1_ACDC`.
    Sets trigger coupling to ac.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    """
    self.set_trigger_input_coupling(trigger_index, 1)

  def get_trigger_input_coupling(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_ACDC` or :obj:`SPC_TRIG_EXT1_ACDC`.
    For decoded information, use :obj:`get_trigger_coupling` instead.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    coupling : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT0_ACDC + (spcm.SPC_TRIG_EXT1_ACDC - spcm.SPC_TRIG_EXT0_ACDC)*trigger_index)
  
  def get_trigger_coupling(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_ACDC` or :obj:`SPC_TRIG_EXT1_ACDC`.
    Returns either :obj:`"dc"` or :obj:`"ac"`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    impedance : :obj:`str`
      String of input impedance.
    """
    bit_code = self.get_trigger_input_coupling(trigger_index)
    if bit_code == 0:
      return "dc"
    if bit_code == 1:
      return "ac"
    
  def set_trigger_mode(self, trigger_index, mode):
    """
    Writes to :obj:`SPC_TRIG_EXT0_MODE`.
    To do this without using bit codes, use :obj:`trigger_disable`, :obj:`use_trigger_positive_edge`, :obj:`use_trigger_negative_edge`, :obj:`use_trigger_both_edge`, :obj:`use_trigger_enter_window`, :obj:`use_trigger_leave_window`, :obj:`use_trigger_high_gate`, :obj:`use_trigger_low_gate`, :obj:`use_trigger_inside_window_gate`, or :obj:`use_trigger_outside_window_gate`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    mode : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_TRIG_EXT0_MODE + (spcm.SPC_TRIG_EXT1_MODE - spcm.SPC_TRIG_EXT0_MODE)*trigger_index, mode)

  def trigger_disable(self, trigger_index, make_sufficient = True):
    """
    Writes :obj:`SPC_TM_NONE` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), removes this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_NONE)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask & (~((spcm.SPC_TMASK_EXT0 & 3) << trigger_index)))

  def use_trigger_positive_edge(self, trigger_index, threshold, multiplier = "", re_arm_threshold = None, make_sufficient = True):
    """
    Writes :obj:`SPC_TM_POS` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    re_arm_threshold : :obj:`float`
      Is :obj:`None` by default.
      Can be set to a voltage (in units determined by :obj:`multiplier`) such that the trigger level must go under this threshold to be re-armed after a trigger (using flag :obj:`SPC_TM_REARM`).
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    if re_arm_threshold is None:
      self.set_trigger_mode(trigger_index, spcm.SPC_TM_POS)
    else:
      self.set_trigger_mode(trigger_index, spcm.SPC_TM_POS | spcm.SPC_TM_REARM)
      self.set_lower_trigger_threshold(trigger_index, re_arm_threshold, multiplier)
    self.set_upper_trigger_threshold(trigger_index, threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_negative_edge(self, trigger_index, threshold, multiplier = "", re_arm_threshold = None, make_sufficient = True):
    """
    Writes :obj:`SPC_TM_NEG` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    re_arm_threshold : :obj:`float`
      Is :obj:`None` by default.
      Can be set to a voltage (in units determined by :obj:`multiplier`) such that the trigger level must go over this threshold to be re-armed after a trigger (using flag :obj:`SPC_TM_REARM`).
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    if re_arm_threshold is None:
      self.set_trigger_mode(trigger_index, spcm.SPC_TM_NEG)
      self.set_upper_trigger_threshold(trigger_index, threshold, multiplier)
    else:
      self.set_trigger_mode(trigger_index, spcm.SPC_TM_NEG | spcm.SPC_TM_REARM)
      self.set_lower_trigger_threshold(trigger_index, threshold, multiplier)
      self.set_upper_trigger_threshold(trigger_index, re_arm_threshold, multiplier)
    
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_both_edge(self, trigger_index, threshold, multiplier = "", make_sufficient = True):
    """
    Writes :obj:`SPC_TM_BOTH` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_BOTH)
    self.set_upper_trigger_threshold(trigger_index, threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_enter_window(self, trigger_index, lower_threshold, upper_threshold, multiplier = "", make_sufficient = True):
    """
    Writes :obj:`SPC_TM_WINENTER` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    lower_threshold : :obj:`float`
      Voltage.
    upper_threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_WINENTER)
    self.set_upper_trigger_threshold(trigger_index, upper_threshold, multiplier)
    self.set_lower_trigger_threshold(trigger_index, lower_threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_leave_window(self, trigger_index, lower_threshold, upper_threshold, multiplier = "", make_sufficient = True):
    """
    Writes :obj:`SPC_TM_WINLEAVE` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    lower_threshold : :obj:`float`
      Voltage.
    upper_threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_WINLEAVE)
    self.set_upper_trigger_threshold(trigger_index, upper_threshold, multiplier)
    self.set_lower_trigger_threshold(trigger_index, lower_threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_high_gate(self, trigger_index, threshold, multiplier = "", make_sufficient = False):
    """
    Writes :obj:`SPC_TM_HIGH` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (:obj:`False` is default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_HIGH)
    self.set_upper_trigger_threshold(trigger_index, threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_low_gate(self, trigger_index, threshold, multiplier = "", make_sufficient = False):
    """
    Writes :obj:`SPC_TM_LOW` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (:obj:`False` is default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_LOW)
    self.set_upper_trigger_threshold(trigger_index, threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_inside_window_gate(self, trigger_index, lower_threshold ,upper_threshold, multiplier = "", make_sufficient = False):
    """
    Writes :obj:`SPC_TM_INWIN` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    lower_threshold : :obj:`float`
      Voltage.
    upper_threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (:obj:`False` is default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_INWIN)
    self.set_upper_trigger_threshold(trigger_index, upper_threshold, multiplier)
    self.set_lower_trigger_threshold(trigger_index, lower_threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def use_trigger_outside_window_gate(self, trigger_index, lower_threshold ,upper_threshold, multiplier = "", make_sufficient = False):
    """
    Writes :obj:`SPC_TM_OUTSIDEWIN` to :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    lower_threshold : :obj:`float`
      Voltage.
    upper_threshold : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    make_sufficient : :obj:`bool`
      If :obj:`True` (:obj:`False` is default), adds this trigger to the OR mask (see :obj:`set_sufficient_triggers`).
    """
    self.set_trigger_mode(trigger_index, spcm.SPC_TM_OUTSIDEWIN)
    self.set_upper_trigger_threshold(trigger_index, upper_threshold, multiplier)
    self.set_lower_trigger_threshold(trigger_index, lower_threshold, multiplier)
    if make_sufficient:
      or_mask = self.get_trigger_or_mask()
      self.set_trigger_or_mask(or_mask | ((spcm.SPC_TMASK_EXT0 & 3) << trigger_index))

  def get_trigger_mode(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_MODE`.
    For decoded information, use :obj:`get_trigger_mode_information` instead.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    mode : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT0_MODE + (spcm.SPC_TRIG_EXT1_MODE - spcm.SPC_TRIG_EXT0_MODE)*trigger_index)
  
  def get_trigger_mode_information(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_MODE`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    mode : :obj:`str`
      Current mode in :obj:`str` form.
    """
    bit_code = self.get_trigger_mode(trigger_index)
    re_arm = bit_code & spcm.SPC_TM_REARM != 0
    bit_code &= spcm.SPC_TM_MODEMASK
    if bit_code == spcm.SPC_TM_NONE:
      return "None"
    elif bit_code == spcm.SPC_TM_POS:
      if re_arm:
        return "Positive edge (re-arming)"
      return "Positive edge"
    elif bit_code == spcm.SPC_TM_NEG:
      if re_arm:
        return "Negative edge (re-arming)"
      return "Negative edge"
    elif bit_code == spcm.SPC_TM_BOTH:
      return "Both edge"
    elif bit_code == spcm.SPC_TM_HIGH:
      return "High gate"
    elif bit_code == spcm.SPC_TM_LOW:
      return "Low gate"
    elif bit_code == spcm.SPC_TM_WINENTER:
      return "Enter window"
    elif bit_code == spcm.SPC_TM_WINLEAVE:
      return "Leave window"
    elif bit_code == spcm.SPC_TM_INWIN:
      return "Inside window gate"
    elif bit_code == spcm.SPC_TM_OUTSIDEWIN:
      return "Outside window gate"
    
  def get_available_trigger_modes(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_AVAILMODES`.
    For decoded information, use :obj:`get_available_trigger_modes_information` instead.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    modes : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT0_AVAILMODES + (spcm.SPC_TRIG_EXT1_MODE - spcm.SPC_TRIG_EXT0_MODE)*trigger_index)
  
  def get_available_trigger_modes_information(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_AVAILMODES`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    modes : :obj:`list` of :obj:`str`
      Available modes in :obj:`str` form.
    """
    bit_code = self.get_available_trigger_modes(trigger_index)
    modes = []
    if bit_code & spcm.SPC_TM_REARM:
      modes.append("Re-arming")
    if bit_code & spcm.SPC_TM_POS:
      modes.append("Positive edge")
    if bit_code & spcm.SPC_TM_NEG:
      modes.append("Negative edge")
    if bit_code & spcm.SPC_TM_BOTH:
      modes.append("Both edge")
    if bit_code & spcm.SPC_TM_HIGH:
      modes.append("High gate")
    if bit_code & spcm.SPC_TM_LOW:
      modes.append("Low gate")
    if bit_code & spcm.SPC_TM_WINENTER:
      modes.append("Enter window")
    if bit_code & spcm.SPC_TM_WINLEAVE:
      modes.append("Leave window")
    if bit_code & spcm.SPC_TM_INWIN:
      modes.append("Inside window gate")
    if bit_code & spcm.SPC_TM_OUTSIDEWIN:
      modes.append("Outside window gate")
    return modes
  
  def set_upper_trigger_threshold(self, trigger_index, threshold, multiplier = ""):
    """
    Writes to :obj:`SPC_TRIG_EXT0_LEVEL0`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    """
    if multiplier == "":
      threshold = int(threshold*1e3)
    elif multiplier != "m":
      raise ValueError("multiplier must be either \"m\" or \"\".")
    self._set_int32(spcm.SPC_TRIG_EXT0_LEVEL0 + (spcm.SPC_TRIG_EXT1_LEVEL0 - spcm.SPC_TRIG_EXT0_LEVEL0)*trigger_index, threshold)
  
  def get_upper_trigger_threshold(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_LEVEL0`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    threshold : :obj:`float`
      Lower voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT0_LEVEL0 + (spcm.SPC_TRIG_EXT1_LEVEL0 - spcm.SPC_TRIG_EXT0_LEVEL0)*trigger_index)*1e-3

  def get_upper_trigger_threshold_min(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL0_MIN`.
    
    Returns
    -------
    threshold : :obj:`float`
      Lower voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_MIN)*1e-3
  
  def get_upper_trigger_threshold_max(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL0_MAX`.
    
    Returns
    -------
    threshold : :obj:`float`
      Lower voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_MAX)*1e-3
  
  def get_upper_trigger_threshold_step(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL0_STEP`.
    
    Returns
    -------
    threshold : :obj:`float`
      Lower voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_STEP)*1e-3
  
  def set_lower_trigger_threshold(self, trigger_index, threshold, multiplier = ""):
    """
    Writes to :obj:`SPC_TRIG_EXT0_LEVEL1`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    threshold : :obj:`float`
      Voltage
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    """
    if multiplier == "":
      threshold = int(threshold*1e3)
    elif multiplier != "m":
      raise ValueError("multiplier must be either \"m\" or \"\".")
    self._set_int32(spcm.SPC_TRIG_EXT0_LEVEL1 + (spcm.SPC_TRIG_EXT1_LEVEL0 - spcm.SPC_TRIG_EXT0_LEVEL0)*trigger_index, threshold)
  
  def get_lower_trigger_threshold(self, trigger_index):
    """
    Reads :obj:`SPC_TRIG_EXT0_LEVEL1`.

    Parameters
    ----------
    trigger_index : :obj:`int`
      Which trigger.
    
    Returns
    -------
    threshold : :obj:`float`
      Upper voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT0_LEVEL1 + (spcm.SPC_TRIG_EXT1_LEVEL1 - spcm.SPC_TRIG_EXT0_LEVEL1)*trigger_index)*1e-3
  
  def get_lower_trigger_threshold_min(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL1_MIN`.
    
    Returns
    -------
    threshold : :obj:`float`
      Upper voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_MIN)*1e-3
  
  def get_lower_trigger_threshold_max(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL1_MAX`.
    
    Returns
    -------
    threshold : :obj:`float`
      Upper voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_MAX)*1e-3
  
  def get_lower_trigger_threshold_step(self):
    """
    Reads :obj:`SPC_TRIG_EXT_AVAIL1_STEP`.
    
    Returns
    -------
    threshold : :obj:`float`
      Upper voltage in V.
    """
    return self._get_int32(spcm.SPC_TRIG_EXT_AVAIL0_STEP)*1e-3

  
  # Channels --------------------------------------------------------------------
  # =============================================================================
  
  def set_channel_enable(self, channels):
    """
    Writes to :obj:`SPC_CHENABLE`.
    To do this without using bit codes, use :obj:`set_channels_enable`.

    Parameters
    ----------
    channels : :obj:`int`
      Bit code.
    """
    self._set_int64(spcm.SPC_CHENABLE, channels)

  def set_channels_enable(
      self,
      channel_0 = False,
      channel_1 = False,
      channel_2 = False,
      channel_3 = False
    ):
    """
    Writes to :obj:`SPC_CHENABLE`.
    Set any of the parameters to :obj:`True` to enable that channel.
    """
    bit_code = 0
    if channel_0:
      bit_code |= spcm.CHANNEL0
    if channel_1:
      bit_code |= spcm.CHANNEL1
    if channel_2:
      bit_code |= spcm.CHANNEL2
    if channel_3:
      bit_code |= spcm.CHANNEL3
    self.set_channel_enable(bit_code)

  def get_channel_enable(self):
    """
    Reads :obj:`SPC_CHENABLE`.
    For decoded information, use :obj:`get_channels_enable`.
    
    Returns
    -------
    channels : :obj:`int`
      Bit code.
    """
    return self._get_int64(spcm.SPC_CHENABLE)
  
  def get_channels_enable(self):
    """
    Reads :obj:`SPC_CHENABLE`.
    
    Returns
    -------
    channels : :obj:`list` of :obj:`str`
      List of enabled channels in string form.
    """
    bit_code = self.get_channel_enable()
    channels = []
    if bit_code & spcm.CHANNEL0:
      channels.append("Channel 0")
    if bit_code & spcm.CHANNEL1:
      channels.append("Channel 1")
    if bit_code & spcm.CHANNEL2:
      channels.append("Channel 2")
    if bit_code & spcm.CHANNEL3:
      channels.append("Channel 3")
    return channels
  
  def get_number_of_active_channels(self):
    """
    Reads :obj:`SPC_CHCOUNT`.
    
    Returns
    -------
    channels : :obj:`int`
      The number of enabled channels.
    """
    return self._get_int32(spcm.SPC_CHCOUNT)
  
  def set_amplitude(self, channel_index, amplitude, multiplier = ""):
    """
    Writes to :obj:`SPC_AMP0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    amplitude : :obj:`float`
      Voltage.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    """
    if multiplier == "":
      amplitude = int(amplitude*1e3)
    elif multiplier != "m":
      raise ValueError("multiplier must be either \"m\" or \"\".")
    self._set_int32(spcm.SPC_AMP0 + channel_index*(spcm.SPC_AMP1 - spcm.SPC_AMP0), amplitude)

  def get_amplitude(self, channel_index):
    """
    Reads :obj:`SPC_AMP0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.

    Returns
    -------
    amplitude : :obj:`float`
      Voltage in V.

    """
    return (self._get_int32(spcm.SPC_AMP0 + channel_index*(spcm.SPC_AMP1 - spcm.SPC_AMP0)))*1e-3
  
  def set_output_enable(self, channel_index, enable):
    """
    Writes to :obj:`SPC_ENABLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    self._set_int32(spcm.SPC_ENABLEOUT0 + channel_index*(spcm.SPC_ENABLEOUT1 - spcm.SPC_ENABLEOUT0), enable)

  def output_enable(self, channel_index):
    """
    Writes 1 to :obj:`SPC_ENABLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    """
    self.set_output_enable(channel_index, 1)

  def output_disable(self, channel_index):
    """
    Writes 0 to :obj:`SPC_ENABLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    """
    self.set_output_enable(channel_index, 0)

  def get_output_enable(self, channel_index):
    """
    Reads from :obj:`SPC_ENABLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.

    Returns
    -------
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    return self._get_int32(spcm.SPC_ENABLEOUT0 + channel_index*(spcm.SPC_ENABLEOUT1 - spcm.SPC_ENABLEOUT0))
  
  def set_filter(self, channel_index, enable):
    """
    Writes to :obj:`SPC_FILTER0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    self._set_int32(spcm.SPC_FILTER0 + channel_index*(spcm.SPC_FILTER1 - spcm.SPC_FILTER0), enable)

  def channel_filter_enable(self, channel_index):
    """
    Writes 1 to :obj:`SPC_FILTER0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    """
    self.set_filter(channel_index, 1)

  def channel_filter_disable(self, channel_index):
    """
    Writes 0 to :obj:`SPC_FILTER0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    """
    self.set_filter(channel_index, 0)

  def get_filter(self, channel_index):
    """
    Reads :obj:`SPC_FILTER0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.

    Returns
    -------
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    return self._get_int32(spcm.SPC_FILTER0 + channel_index*(spcm.SPC_FILTER1 - spcm.SPC_FILTER0))
  
  def set_differential(self, channel_index, enable):
    """
    Writes to :obj:`SPC_DIFF0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    self._set_int32(spcm.SPC_DIFF0 + channel_index*(spcm.SPC_DIFF1 - spcm.SPC_DIFF0), enable)

  def differential_enable(self, channel_index):
    """
    Writes 1 to :obj:`SPC_DIFF0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    """
    self.set_differential(channel_index, 1)

  def differential_disable(self, channel_index):
    """
    Writes 0 to :obj:`SPC_DIFF0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    """
    self.set_differential(channel_index, 0)

  def get_differential(self, channel_index):
    """
    Reads :obj:`SPC_DIFF0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).

    Returns
    -------
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    return self._get_int32(spcm.SPC_DIFF0 + channel_index*(spcm.SPC_DIFF1 - spcm.SPC_DIFF0))
  
  def set_double(self, channel_index, enable):
    """
    Writes to :obj:`SPC_DOUBLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    self._set_int32(spcm.SPC_DOUBLEOUT0 + channel_index*(spcm.SPC_DOUBLEOUT1 - spcm.SPC_DOUBLEOUT0), enable)

  def double_enable(self, channel_index):
    """
    Writes 1 to :obj:`SPC_DOUBLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    """
    self.set_double(channel_index, 1)

  def double_disable(self, channel_index):
    """
    Writes 0 to :obj:`SPC_DOUBLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).
    """
    self.set_double(channel_index, 0)

  def get_double(self, channel_index):
    """
    Reads :obj:`SPC_DOUBLEOUT0`.

    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel (0 for channels 0 and 1, 2 for channels 2 and 3).

    Returns
    -------
    enable : :obj:`int`
      :obj:`1` for enabled, :obj:`0` for disabled.
    """
    return self._get_int32(spcm.SPC_DOUBLEOUT0 + channel_index*(spcm.SPC_DOUBLEOUT1 - spcm.SPC_DOUBLEOUT0))
  
  def set_stop_level(self, channel_index, stop_level_code):
    """
    Writes to :obj:`SPC_CH0_STOPLEVEL`.
    To do this without using bit codes, use :obj:`set_channel_stop_level`.
    
    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    stop_level_code : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_CH0_STOPLEVEL + channel_index*(spcm.SPC_CH1_STOPLEVEL - spcm.SPC_CH0_STOPLEVEL), stop_level_code)

  def get_stop_level(self, channel_index):
    """
    Reads :obj:`SPC_CH0_STOPLEVEL`.
    For decoded information, use :obj:`get_channel_stop_level`.
    
    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    
    Returns
    -------
    stop_level_code : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_CH0_STOPLEVEL + channel_index*(spcm.SPC_CH1_STOPLEVEL - spcm.SPC_CH0_STOPLEVEL))
  
  def set_stop_level_custom(self, channel_index, value):
    """
    Writes to :obj:`SPC_CH0_CUSTOM_STOP`.
    To do this without using bit codes, use :obj:`set_channel_stop_level`.
    
    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    value : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_CH0_CUSTOM_STOP + channel_index*(spcm.SPC_CH1_CUSTOM_STOP - spcm.SPC_CH0_CUSTOM_STOP), value)

  def get_stop_level_custom(self, channel_index):
    """
    Reads :obj:`SPC_CH0_CUSTOM_STOP`.
    For decoded information, use :obj:`get_channel_stop_level`.
    
    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    
    Returns
    -------
    stop_level : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_CH0_CUSTOM_STOP + channel_index*(spcm.SPC_CH1_CUSTOM_STOP - spcm.SPC_CH0_CUSTOM_STOP))

  def set_channel_stop_level(
      self,
      channel_index,
      zero = False,
      low = False,
      high = False,
      hold_last = False,
      custom_value = None
    ):
    """
    Writes to :obj:`SPC_CH0_STOPLEVEL` and :obj:`SPC_CH0_CUSTOM_STOP`.
    To set a custom value, set the parameter :obj:`custom_value` to a :obj:`float` between :obj:`-1.0` and :obj:`1.0`.
    To set it to any other stop level mode, set that parameter to :obj:`True`.
    """
    if zero:
      self.set_stop_level(channel_index, spcm.SPCM_STOPLVL_ZERO)
    elif low:
      self.set_stop_level(channel_index, spcm.SPCM_STOPLVL_LOW)
    elif high:
      self.set_stop_level(channel_index, spcm.SPCM_STOPLVL_HIGH)
    elif hold_last:
      self.set_stop_level(channel_index, spcm.SPCM_STOPLVL_HOLDLAST)
    elif custom_value is not None:
      self.set_stop_level(channel_index, spcm.SPCM_STOPLVL_CUSTOM)
      limit = int(2**(self.get_sample_resolution_bits() - 1) - 1)
      self.set_stop_level_custom(channel_index, int(limit*np.clip(custom_value, -1, 1)))

  def get_channel_stop_level(self, channel_index):
    """
    Reads :obj:`SPC_CH0_STOPLEVEL` and :obj:`SPC_CH0_CUSTOM_STOP`.
    
    Parameters
    ----------
    channel_index : :obj:`int`
      Which channel.
    
    Returns
    -------
    stop_level : :obj:`str` or :obj:`float`
      If stop level is set to a particular mode, returns that mode as a :obj:`str`.
      If this mode is :obj:`SPCM_STOPLVL_CUSTOM` then it returns the custom level as a :obj:`float` between :obj:`-1.0` and :obj:`1.0`.
    """
    stop_level = self.get_stop_level(channel_index)
    if stop_level == spcm.SPCM_STOPLVL_ZERO:
      return "Zero"
    if stop_level == spcm.SPCM_STOPLVL_LOW:
      return "Low"
    if stop_level == spcm.SPCM_STOPLVL_HIGH:
      return "High"
    if stop_level == spcm.SPCM_STOPLVL_HOLDLAST:
      return "Hold last"
    if stop_level == spcm.SPCM_STOPLVL_CUSTOM:
      limit = int(2**(self.get_sample_resolution_bits() - 1) - 1)
      return self.get_stop_level_custom(channel_index)/limit
  
  # Commands --------------------------------------------------------------------
  # =============================================================================
  
  def execute_command(self, command):
    """
    Writes to :obj:`SPC_M2CMD`.
    To do this without using bit codes, use :obj:`execute_commands`.
    
    Parameters
    ----------
    command : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPC_M2CMD, command)

  def execute_commands(
      self,
      reset = False,
      write_setup = False,
      start = False,
      enable_trigger = False,
      force_trigger = False,
      disable_trigger = False,
      stop = False,
      dma_start = False,
      dma_wait = False,
      dma_stop = False,
      wait_for_prefill = False,
      wait_for_trigger = False,
      wait_until_ready = False
    ):
    """
    Writes to :obj:`SPC_M2CMD`.
    To call a command, set the corresponding parameter to :obj:`True`.
    """
    command = 0
    if reset:
      command |= spcm.M2CMD_CARD_RESET
    if write_setup:
      command |= spcm.M2CMD_CARD_WRITESETUP
    if start:
      command |= spcm.M2CMD_CARD_START
    if enable_trigger:
      command |= spcm.M2CMD_CARD_ENABLETRIGGER
    if force_trigger:
      command |= spcm.M2CMD_CARD_FORCETRIGGER
    if disable_trigger:
      command |= spcm.M2CMD_CARD_DISABLETRIGGER
    if stop:
      command |= spcm.M2CMD_CARD_STOP
    if dma_start:
      command |= spcm.M2CMD_DATA_STARTDMA
    if dma_wait:
      command |= spcm.M2CMD_DATA_WAITDMA
    if dma_stop:
      command |= spcm.M2CMD_DATA_STOPDMA
    if wait_for_prefill:
      command |= spcm.M2CMD_CARD_WAITPREFULL
    if wait_for_trigger:
      command |= spcm.M2CMD_CARD_WAITTRIGGER
    if wait_until_ready:
      command |= spcm.M2CMD_CARD_WAITREADY
    self.execute_command(command)

  def start(self):
    """
    Writes :obj:`M2CMD_CARD_START` to :obj:`SPC_M2CMD`.
    """
    self.execute_commands(start = True)

  def arm(self):
    """
    Writes :obj:`M2CMD_CARD_START` and :obj:`M2CMD_CARD_ENABLETRIGGER` to :obj:`SPC_M2CMD`.
    """
    self.execute_commands(start = True, enable_trigger = True)

  def force_trigger(self):
    """
    Writes :obj:`M2CMD_CARD_FORCETRIGGER` to :obj:`SPC_M2CMD`.
    """
    self.execute_commands(force_trigger = True)

  def stop(self):
    """
    Writes :obj:`M2CMD_CARD_STOP` to :obj:`SPC_M2CMD`.
    """
    self.execute_commands(stop = True)

  def reset(self):
    """
    Writes :obj:`M2CMD_CARD_RESET` to :obj:`SPC_M2CMD`.
    """
    self.execute_commands(reset = True)

  def set_timeout(self, time_to_live, multiplier = ""):
    """
    Writes to :obj:`SPC_TIMEOUT`.
    
    Parameters
    ----------
    time_to_live : :obj:`int`
      Timeout duration in seconds.
    multiplier : :obj:`str`
      Can be metric prefixes :obj:`""` (default), or :obj:`"m"`.
    """
    if multiplier == "":
      time_to_live = int(time_to_live*1e3)
    elif multiplier != "m":
      raise ValueError("multiplier must be either \"m\" or \"\".")
    self._set_int32(spcm.SPC_TIMEOUT, time_to_live)

  def get_timeout(self):
    """
    Reads :obj:`SPC_TIMEOUT`.
    
    Returns
    -------
    time_to_live : :obj:`int`
      Timeout duration in seconds.
    """
    return self._get_int32(spcm.SPC_TIMEOUT)*1e-3

  # DMA and memory --------------------------------------------------------------
  # =============================================================================
  
  def array_to_device(self, data, segment = 0, aux_data = None, aux_data_channels = None):
    """
    Transfers signals from the host to the card using :obj:`_transfer_array_i64`.

    Parameters
    ----------
    data : :obj:`list` of :obj:`numpy.ndarray` of :obj:`float`
      A :obj:`list` of sampled waveforms to be transferred to the card.
      The first element in the :obj:`list` is the waveform that is assigned to the first enabled channel, and so on.
      Values are assumed to be between :obj:`-1.0` and :obj:`1.0`.
    segment : :obj:`int`
      The segment that the waveform is loaded into.
      Only relevant if the card is in a mode that uses segments, such as sequencing.
    aux_data : :obj:`list` of :obj:`numpy.ndarray` of :obj:`bool`
      An optional :obj:`list` of binary waveforms to be played out of the IO ports (X0, X1 and/or X2).
      Requires information given in :obj:`aux_data_channels`.
      Will automatically set up port modes and signal discretisation based on information given.
    aux_data_channels : :obj:`list` of :obj:`dict`
      Information that says where in which channels the binary waveforms in :obj:`aux_data_channels` are taken from, and which port they are output.
      Each :obj:`dict` in the overall :obj:`list` corresponds to one of the waveforms in :obj:`aux_data_channels`.
      The dictionary should contain three elements:
      :obj:`"Port"` is an :obj:`int` that corresponds to which of the digital IO ports that waveform should be sent to;
      :obj:`"Channel"` is an :obj:`int` that corresponds to which of the channels the digital waveform should be encoded in; and
      :obj:`"Bit"` is either :obj:`15`, :obj:`14` or :obj:`13`, which corresponds to which bit of the channel should be sacrificed for the digital waveform.
      Note that this should be consistent for every segment of memory.
    """
    # Change segment
    if self.get_mode_information() in ["Sequence", "Multi"]:
      self.set_segment_length(segment, data[0].size)
      previous_segment = self.get_current_segment()
      self.set_current_segment(segment)

    # Initialise buffer
    stride = self.get_sample_resolution()
    channels = self.get_number_of_active_channels()
    data_buffer = spcm_tools.pvAllocMemPageAligned(channels*stride*data[0].size)
    data_pointer = spcm_tools.cast(data_buffer, spcm.ptr16)

    digital_output_used = [False, False, False]
    for channel in range(channels):
      # Find out if there are digital outs and, if so, set the discretisation rate
      max_bits = self.get_sample_resolution_bits()
      aux_data_reverse_lookup = []
      if aux_data is not None:
        for aux_data_channel_index, aux_data_channel in enumerate(aux_data_channels):
          if aux_data_channel["Channel"] == channel:
            bit = aux_data_channel["Bit"]
            max_bits = min(bit, max_bits)
            aux_data_reverse_lookup.append([aux_data_channel_index, bit])
            self.use_io_mode_digital_out(aux_data_channel["Port"], aux_data_channel["Channel"], aux_data_channel["Bit"])
            digital_output_used[aux_data_channel["Port"]] = True
      limit = int(2**(max_bits - 1) - 1)

      # Add waveform and digital outs to buffer
      channel_data = data[channel]
      for sample_index, sample in enumerate(channel_data):
        # Discretise waveform, and blank out bits meant for aux digital out
        data_pointer[channel + channels*sample_index] = int(limit*np.clip(sample, -1, 1)) & (~(0x7 << max_bits))
        # Append aux digital outs
        for reverse_lookup in aux_data_reverse_lookup:
          data_pointer[channel + channels*sample_index] |= (int(aux_data[reverse_lookup[0]][sample_index]) & 1) << reverse_lookup[1]
    
    # Disable ports if digital io are not in use
    for port in range(3):
      if not digital_output_used[port]:
        io_mode = self.get_io_mode_information(port)
        if "Digital out" in io_mode:
          self.io_port_disable(port)

    # Transfer buffer to card
    self._transfer_array_i64(spcm.SPCM_BUF_DATA, spcm.SPCM_DIR_PCTOCARD, 0, data_buffer, 0, stride*data[0].size*channels)
    self.execute_commands(dma_start = True, dma_wait = True)

    # Tidy up
    if self.get_mode_information() in ["Sequence", "Multi"]:
      self.set_current_segment(previous_segment)
  
  def set_memory_size(self, size):
    """
    Writes to :obj:`SPC_MEMSIZE`.
    
    Parameters
    ----------
    size : :obj:`int`
      Memory size in samples per channel.
    """
    self._set_int64(spcm.SPC_MEMSIZE, size)
  
  def get_memory_size(self):
    """
    Reads :obj:`SPC_MEMSIZE`.
    
    Returns
    -------
    size : :obj:`int`
      Memory size in samples per channel.
    """
    return self._get_int64(spcm.SPC_MEMSIZE)
  
  def get_max_memory_size(self):
    """
    Reads :obj:`SPC_PCIMEMSIZE`.
    
    Returns
    -------
    size : :obj:`int`
      Memory size on the card in Bytes.
    """
    return self._get_int64(spcm.SPC_PCIMEMSIZE)
  
  def set_memory_test(self, enable):
    """
    Writes to :obj:`SPC_MEMTEST`.
    
    Parameters
    ----------
    enable : :obj:`int`
      :obj:`1` if mode is enabled, :obj:`0` otherwise.
    """
    self._set_int64(spcm.SPC_MEMTEST, enable)

  def memory_test_start(self):
    """
    Writes :obj:`1` to :obj:`SPC_MEMTEST`.
    """
    self.set_memory_test(self, 1)

  def memory_test_stop(self):
    """
    Writes :obj:`0` to :obj:`SPC_MEMTEST`.
    """
    self.set_memory_test(self, 0)

  def get_memory_test(self):
    """
    Reads :obj:`SPC_MEMTEST`.
    
    Returns
    -------
    enable : :obj:`int`
      :obj:`1` if mode is enabled, :obj:`0` otherwise.
    """
    return self._get_int64(spcm.SPC_MEMTEST)
  
  # Playback --------------------------------------------------------------------
  # =============================================================================
  
  def set_number_of_loops(self, number_of_loops):
    """
    Writes to :obj:`SPC_LOOPS`.
    
    Parameters
    ----------
    number_of_loops : :obj:`int`
      How many times the waveform should be looped.
      If set to :obj:`0`, will loop indefinitely.
    """
    self._set_int32(spcm.SPC_LOOPS, number_of_loops)
  
  def get_number_of_loops(self):
    """
    Writes to :obj:`SPC_LOOPS`.
    
    Returns
    -------
    number_of_loops : :obj:`int`
      How many times the waveform should be looped.
      If set to :obj:`0`, will loop indefinitely.
    """
    return self._get_int32(spcm.SPC_LOOPS)

  # Sequencing ------------------------------------------------------------------
  # =============================================================================
  
  def get_max_number_of_segments(self):
    """
    Reads :obj:`SPC_SEQMODE_AVAILMAXSEGMENT`.
    
    Returns
    -------
    size : :obj:`int`
      Max number of segments that can be used with the card.
    """
    return self._get_int64(spcm.SPC_SEQMODE_AVAILMAXSEGMENT)
  
  def get_max_number_of_sequence_steps(self):
    """
    Reads :obj:`SPC_SEQMODE_AVAILMAXSTEPS`.
    
    Returns
    -------
    size : :obj:`int`
      Max number of steps that can be used with the card.
    """
    return self._get_int64(spcm.SPC_SEQMODE_AVAILMAXSTEPS)
  
  def get_max_number_of_loops_per_sequence_step(self):
    """
    Reads :obj:`SPC_SEQMODE_AVAILMAXLOOP`.
    
    Returns
    -------
    loops : :obj:`int`
      Max number of loops that can be used in each sequence step.
      Note that steps can also be set to loop indefinitely. 
    """
    return self._get_int64(spcm.SPC_SEQMODE_AVAILMAXLOOP)
  
  def get_available_sequence_features(self):
    """
    Reads :obj:`SPC_SEQMODE_AVAILFEATURES`.
    For decoded information, use :obj:`get_features_information` or :obj:`get_available_sequence_features_information` instead.

    Returns
    -------
    features : :obj:`int`
      Bit code.
    """
    return self._get_int64(spcm.SPC_SEQMODE_AVAILFEATURES)
  
  def get_available_sequence_features_information(self):
    """
    Reads :obj:`SPC_SEQMODE_AVAILFEATURES`.

    Returns
    -------
    features : :obj:`list` of :obj:`str`
      The features that can be used in sequence mode in :obj:`str` format.
    """
    bitmap = self.get_available_sequence_features()
    features = []
    if bitmap & spcm.SPCSEQ_ENDLOOPONTRIG:
      features.append("Loop step until trigger")
    if bitmap & spcm.SPCSEQ_END:
      features.append("Final step")
    return features
  
  def set_number_of_segments(self, number_of_segments):
    """
    Writes to :obj:`SPC_SEQMODE_MAXSEGMENTS`.
    
    Parameters
    ----------
    number_of_segments : :obj:`int`
      The number of segments to split the memory into.
    """
    self._set_int64(spcm.SPC_SEQMODE_MAXSEGMENTS, number_of_segments)

  def get_number_of_segments(self):
    """
    Reads :obj:`SPC_SEQMODE_MAXSEGMENTS`.
    
    Returns
    -------
    number_of_segments : :obj:`int`
      The number of segments to split the memory into.
    """
    return self._get_int64(spcm.SPC_SEQMODE_MAXSEGMENTS)
  
  def set_current_segment(self, segment):
    """
    Writes to :obj:`SPC_SEQMODE_WRITESEGMENT`.
    
    Parameters
    ----------
    segment : :obj:`int`
      The segment currently "armed" for reading and writing to.
    """
    self._set_int64(spcm.SPC_SEQMODE_WRITESEGMENT, segment)

  def get_current_segment(self):
    """
    Reads :obj:`SPC_SEQMODE_WRITESEGMENT`.
    
    Returns
    -------
    segment : :obj:`int`
      The segment currently "armed" for reading and writing to.
    """
    return self._get_int64(spcm.SPC_SEQMODE_WRITESEGMENT)
  
  def set_segment_size(self, size):
    """
    Writes to :obj:`SPC_SEQMODE_SEGMENTSIZE`.
    Sets the length of the currently armed segment.
    
    Parameters
    ----------
    size : :obj:`int`
      Length of segment in samples per channel.
    """
    self._set_int64(spcm.SPC_SEQMODE_SEGMENTSIZE, size)

  def set_segment_length(self, segment, length):
    """
    Writes to :obj:`SPC_SEQMODE_SEGMENTSIZE`.
    Sets the length of any segment segment.
    
    Parameters
    ----------
    segment : :obj:`int`
      The segment to set the length of.
    size : :obj:`int`
      Length of segment in samples per channel.
    """
    previous_segment = self.get_current_segment()
    self.set_current_segment(segment)
    self.set_segment_size(length)
    self.set_current_segment(previous_segment)

  def get_segment_size(self):
    """
    Reads :obj:`SPC_SEQMODE_SEGMENTSIZE`.
    Reads the length of the currently armed segment.
    
    Returns
    -------
    size : :obj:`int`
      Length of segment in samples per channel.
    """
    return self._get_int64(spcm.SPC_SEQMODE_SEGMENTSIZE)

  def get_segment_length(self, segment):
    """
    Reads :obj:`SPC_SEQMODE_SEGMENTSIZE`.
    Reads the length of any segment segment.
    
    Parameters
    ----------
    segment : :obj:`int`
      The segment to get the length of.
    
    Returns
    -------
    size : :obj:`int`
      Length of segment in samples per channel.
    """
    previous_segment = self.get_current_segment()
    self.set_current_segment(segment)
    length = self.get_segment_size()
    self.set_current_segment(previous_segment)
    return length
  
  def set_sequence_instruction(self, step, instruction):
    """
    Writes to :obj:`SPC_SEQMODE_STEPMEM0`.
    To do this without using bit codes, use :obj:`set_step_instruction`.
    
    Parameters
    ----------
    step : :obj:`int`
      The step to write to.
    instruction : :obj:`int`
      Bit code.
    """
    self._set_int64(spcm.SPC_SEQMODE_STEPMEM0 + step, instruction)

  def set_step_instruction(
      self,
      step,
      segment,
      number_of_loops = 1,
      next_step = None, 
      loop_until_trigger = False,
      end_of_sequence = False
      ):
    """
    Writes to :obj:`SPC_SEQMODE_STEPMEM0`.
    
    Parameters
    ----------
    step : :obj:`int`
      The step to write to.
    segment : :obj:`int`
      The segment the step points to.
    number_of_loops : :obj:`int`
      How many times the step should be looped.
    next_step : :obj:`int`
      The step that follows this one.
      If :obj:`None` (default), will either point to step :obj:`step + 1` or, if :obj:`end_of_sequence` is set to :obj:`True`, will point to step :obj:`0`.
    loop_until_trigger : :obj:`bool`
      Whether to wait for a trigger until proceeding to the next step.
    end_of_sequence : :obj:`bool`
      Whether or not the step is the final step in the sequence.
    """
    instruction = 0x0000000000000000

    instruction |= segment & spcm.SPCSEQ_SEGMENTMASK

    if next_step is None:
      if end_of_sequence:
        next_step = 0
      else:
        next_step = step + 1
    instruction |= (next_step << 16) & spcm.SPCSEQ_NEXTSTEPMASK

    instruction |= (number_of_loops << 32) & (spcm.SPCSEQ_LOOPMASK << 32)

    if loop_until_trigger:
      instruction |= spcm.SPCSEQ_ENDLOOPONTRIG << 32
    
    if end_of_sequence:
      instruction |= spcm.SPCSEQ_END << 32
    
    self.set_sequence_instruction(step, instruction)

  def get_sequence_instruction(self, step):
    """
    Reads :obj:`SPC_SEQMODE_STEPMEM0`.
    For decoded information, use :obj:`get_step_instruction` instead.
    
    Parameters
    ----------
    step : :obj:`int`
      The step to write to.

    Returns
    -------
    instruction : :obj:`int`
      Bit code.
    """
    return self._get_int64(spcm.SPC_SEQMODE_STEPMEM0 + step)
  
  def get_step_instruction(self, step):
    """
    Reads :obj:`SPC_SEQMODE_STEPMEM0`.
    
    Parameters
    ----------
    step : :obj:`int`
      The step to write to.

    Returns
    -------
    instruction : :obj:`dict`
      Contains information under keys of :obj:`"Segment"`, :obj:`"Next step"`, :obj:`"Number of loops"`, :obj:`"Loop until trigger"` and :obj:`"End of sequence"`.
      Each has the same meaning as in the parameters for :obj:`set_step_instruction`.
    """
    bit_code = self.get_sequence_instruction(step)
    segment = bit_code & spcm.SPCSEQ_SEGMENTMASK
    next_step = (bit_code & spcm.SPCSEQ_NEXTSTEPMASK) >> 16
    number_of_loops = (bit_code >> 32) & spcm.SPCSEQ_LOOPMASK
    loop_until_trigger = (((bit_code >> 32) & spcm.SPCSEQ_ENDLOOPONTRIG) != 0)
    end_of_sequence = (((bit_code >> 32) & spcm.SPCSEQ_END) != 0)
    return {"Segment":segment, "Next step":next_step, "Number of loops":number_of_loops, "Loop until trigger":loop_until_trigger, "End of sequence":end_of_sequence}

  def set_start_step(self, step):
    """
    Writes to :obj:`SPC_SEQMODE_STARTSTEP`.
    
    Parameters
    ----------
    step : :obj:`int`
      The starting step of the sequence.
    """
    self._set_int64(spcm.SPC_SEQMODE_STARTSTEP, step)

  def get_start_step(self):
    """
    Reads :obj:`SPC_SEQMODE_STARTSTEP`.
    
    Returns
    -------
    step : :obj:`int`
      The starting step of the sequence.
    """
    return self._get_int64(spcm.SPC_SEQMODE_STARTSTEP)

  # Status ----------------------------------------------------------------------
  # =============================================================================
  
  def get_status(self):
    """
    Reads :obj:`SPC_M2STATUS`.
    For decoded information, use :obj:`get_status_information` instead.
    
    Returns
    -------
    status : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPC_M2STATUS)
  
  def get_status_information(self):
    """
    Reads :obj:`SPC_M2STATUS`.
    
    Returns
    -------
    status : :obj:`list` of :obj:`list`
      A list describing the status of the card.
    """
    status = []
    response = self.get_status()

    if response & spcm.M2STAT_CARD_PRETRIGGER:
      status.append("Pre-trigger")
    if response & spcm.M2STAT_CARD_TRIGGER:
      status.append("Trigger")
    if response & spcm.M2STAT_CARD_READY:
      status.append("Ready")
    if response & spcm.M2STAT_CARD_SEGMENT_PRETRG:
      status.append("Segment pre-trigger")

    if response & spcm.M2STAT_DATA_BLOCKREADY:
      status.append("DMA: Block ready")
    if response & spcm.M2STAT_DATA_END:
      status.append("DMA: End")
    if response & spcm.M2STAT_DATA_OVERRUN:
      status.append("DMA: Over-run")
    if response & spcm.M2STAT_DATA_ERROR:
      status.append("DMA: Error")

    return status
  
  # IO lines --------------------------------------------------------------------
  # =============================================================================
  def set_io_mode(self, port, mode):
    """
    Writes to :obj:`SPCM_X0_MODE`.
    To do this without using bit codes, use :obj:`io_port_disable`, :obj:`use_io_mode_digital_out`, :obj:`use_io_mode_asynchronous_input`, :obj:`use_io_mode_asynchronous_output`, :obj:`use_io_mode_trigger_output`, :obj:`use_io_mode_run_state_output`, :obj:`use_io_mode_arm_state_output`, :obj:`use_io_mode_continuous_marker_output`, :obj:`use_io_mode_reference_clock_output` or :obj:`use_io_mode_system_clock_output` instead.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    mode : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPCM_X0_MODE + (spcm.SPCM_X1_MODE - spcm.SPCM_X0_MODE)*port, mode)
  
  def io_port_disable(self, port):
    """
    Writes :obj:`SPCM_XMODE_DISABLE` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_DISABLE)

  def use_io_mode_digital_out(self, port, channel, bit):
    """
    Writes :obj:`SPCM_XMODE_DIGOUT` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    command = spcm.SPCM_XMODE_DIGOUT
    command |= spcm.SPCM_XMODE_DIGOUTSRC_CH0 << channel
    if bit == 15:
      command |= spcm.SPCM_XMODE_DIGOUTSRC_BIT15
    elif bit == 14:
      command |= spcm.SPCM_XMODE_DIGOUTSRC_BIT14
    elif bit == 13:
      command |= spcm.SPCM_XMODE_DIGOUTSRC_BIT13
    self.set_io_mode(port, command)

  def use_io_mode_asynchronous_input(self, port):
    """
    Writes :obj:`SPCM_XMODE_ASYNCIN` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_ASYNCIN)

  def use_io_mode_asynchronous_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_ASYNCOUT` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_ASYNCOUT)

  def use_io_mode_trigger_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_TRIGOUT` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_TRIGOUT)

  def use_io_mode_run_state_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_RUNSTATE` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_RUNSTATE)

  def use_io_mode_arm_state_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_ARMSTATE` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_RUNSTATE)

  def use_io_mode_continuous_marker_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_CONTOUTMARK` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_RUNSTATE)

  def use_io_mode_reference_clock_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_REFCLKOUT` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_REFCLKOUT)

  def use_io_mode_system_clock_output(self, port):
    """
    Writes :obj:`SPCM_XMODE_SYSCLKOUT` to :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    """
    self.set_io_mode(port, spcm.SPCM_XMODE_SYSCLKOUT)
  
  def get_io_mode(self, port):
    """
    Reads :obj:`SPCM_X0_MODE`.
    For decoded information, use :obj:`get_available_io_modes_information` instead.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    
    Returns
    -------
    modes : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_X0_MODE + (spcm.SPCM_X1_MODE - spcm.SPCM_X0_MODE)*port)
  
  def get_io_mode_information(self, port):
    """
    Reads :obj:`SPCM_X0_MODE`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    
    Returns
    -------
    mode : :obj:`str`
      Mode in :obj:`str` format
    """
    bit_code = self.get_io_mode(port)
    bit_code_digital_out = bit_code & 0xFFFF0000
    bit_code &= 0x0000FFFF
    if bit_code == spcm.SPCM_XMODE_DISABLE:
      return "Disabled"
    elif bit_code == spcm.SPCM_XMODE_ASYNCIN:
      return "Asynchronous input"
    elif bit_code == spcm.SPCM_XMODE_ASYNCOUT:
      return "Asynchronous output"
    elif bit_code == spcm.SPCM_XMODE_DIGIN:
      return "Digital input"
    elif bit_code == spcm.SPCM_XMODE_DIGOUT:
      mode = "Digital output; Channel"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_CH0:
        mode += " 0"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_CH1:
        mode += " 1"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_CH2:
        mode += " 2"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_CH3:
        mode += " 3"
      mode += "; Bit "
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_BIT15:
        mode += " 15"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_BIT14:
        mode += " 14"
      if bit_code_digital_out & spcm.SPCM_XMODE_DIGOUTSRC_BIT13:
        mode += " 13"
      mode += ";"
      return mode
    elif bit_code == spcm.SPCM_XMODE_TRIGOUT:
      return "Trigger output"
    elif bit_code == spcm.SPCM_XMODE_DIGIN2BIT:
      return "Digital (2 bit) input"
    elif bit_code == spcm.SPCM_XMODE_RUNSTATE:
      return "Run state output"
    elif bit_code == spcm.SPCM_XMODE_ARMSTATE:
      return "Arm state output"
    elif bit_code == spcm.SPCM_XMODE_REFCLKOUT:
      return "Reference clock output"
    elif bit_code == spcm.SPCM_XMODE_SYSCLKOUT:
      return "System clock output"
    elif bit_code == spcm.SPCM_XMODE_CONTOUTMARK:
      return "Continuous marker output"
  
  def get_available_io_modes(self, port):
    """
    Reads :obj:`SPCM_X0_AVAILMODES`.
    For decoded information, use :obj:`get_available_io_modes_information` instead.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    
    Returns
    -------
    modes : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_X0_AVAILMODES + (spcm.SPCM_X1_MODE - spcm.SPCM_X0_MODE)*port)

  def get_available_io_modes_information(self, port):
    """
    Reads :obj:`SPCM_X0_AVAILMODES`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    
    Returns
    -------
    modes : :obj:`list` of :obj:`str`
      Modes in :obj:`str` format
    """
    bit_code = self.get_available_io_modes(port)
    modes = []
    if bit_code & spcm.SPCM_XMODE_ASYNCIN:
      modes.append("Asynchronous input")
    if bit_code & spcm.SPCM_XMODE_ASYNCOUT:
      modes.append("Asynchronous output")
    if bit_code & spcm.SPCM_XMODE_DIGIN:
      modes.append("Digital input")
    if bit_code & spcm.SPCM_XMODE_DIGOUT:
      modes.append("Digital output")
    if bit_code & spcm.SPCM_XMODE_TRIGOUT:
      modes.append("Trigger output")
    if bit_code & spcm.SPCM_XMODE_DIGIN2BIT:
      modes.append("Digital (2 bit) input")
    if bit_code & spcm.SPCM_XMODE_RUNSTATE:
      modes.append("Run state output")
    if bit_code & spcm.SPCM_XMODE_ARMSTATE:
      modes.append("Arm state output")
    if bit_code & spcm.SPCM_XMODE_REFCLKOUT:
      modes.append("Reference clock output")
    if bit_code & spcm.SPCM_XMODE_SYSCLKOUT:
      modes.append("System clock output")
    if bit_code & spcm.SPCM_XMODE_CONTOUTMARK:
      modes.append("Continuous marker output")
    return modes
  
  def set_io_asynchronous_register(self, value):
    """
    Writes to :obj:`SPCM_XX_ASYNCIO`.
    To do this without using bit codes, use ... instead.

    Parameters
    ----------
    value : :obj:`int`
      Bit code.
    """
    self._set_int32(spcm.SPCM_XX_ASYNCIO, value)

  def set_io_asynchronous(self, port, value):
    """
    Writes to :obj:`SPCM_XX_ASYNCIO`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    value : :obj:`bool`
      Port value.
    """
    bit_code = self.get_io_asynchronous_register()  # Get previous output
    if value:
      bit_code |= (1 << port)
    else:
      bit_code &= ~(1 << port)
    self.set_io_asynchronous_register(bit_code)
    return (bit_code & (1 << port)) != 0
  
  def get_io_asynchronous_register(self):
    """
    Reads :obj:`SPCM_XX_ASYNCIO`.
    For decoded information, use ... instead.

    Returns
    -------
    value : :obj:`int`
      Bit code.
    """
    return self._get_int32(spcm.SPCM_XX_ASYNCIO)
  
  def get_io_asynchronous(self, port):
    """
    Reads :obj:`SPCM_XX_ASYNCIO`.

    Parameters
    ----------
    port : :obj:`int`
      Which IO port.
    
    Returns
    -------
    value : :obj:`bool`
      Port value.
    """
    bit_code = self.get_io_asynchronous_register()
    return (bit_code & (1 << port)) != 0