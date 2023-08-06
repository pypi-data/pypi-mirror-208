from configparser import ConfigParser

from simses.commons.config.generation.analysis import AnalysisConfigGenerator
from simses.commons.config.generation.simulation import SimulationConfigGenerator
from simses.commons.config.simulation.battery import BatteryConfig
from simses.simulation.batch_processing import BatchProcessing
from simses.simulation.simbas.room_tool_reader import RoomToolReader
import os
import copy


class SimBAS(BatchProcessing):

    """
    This is the SimBAS example for BatchProcessing.
    """

    __CELL_EXT: str = '.xml'

    def __init__(self, use_room_tool: bool = True):
        super().__init__(do_simulation=True, do_analysis=True)
        self.__use_room_tool: bool = use_room_tool

    def _setup_config(self) -> dict:

        # Use case:
        #use_case = 'ecar'
        # use_case = 'eboat'
        use_case = 'hpc+bess'

        if use_case == 'ecar':
            config_file_name = 'simulation_SimBAS_Ecar'
            room_tool_file = 'report_auto.csv'
            ac_power: float = 105e3
        elif use_case == 'eboat':
            config_file_name = 'simulation_SimBAS_Eboot'
            room_tool_file = 'report_boot.csv'
            ac_power: float = 320000.0
        elif use_case == 'hpc+bess':
            config_file_name = 'simulation_SimBAS_HPC+BSS'
            room_tool_file = 'report_ladesäule.csv'
            ac_power: float = 320000.0


        profile_path = os.getcwd() + '\Profiles'

        config_generator: SimulationConfigGenerator = SimulationConfigGenerator()
        config_generator.load_default_config()
        config_generator.load_specific_config(config_file_name)

        # Set profile direction
        config_generator.set_profile_direction(profile_path)

        # generating config options
        config_generator.clear_storage_technology()
        dcdc_1: str = config_generator.add_fix_efficiency_dcdc(1.0)
        acdc_1: str = config_generator.add_no_loss_acdc()
        housing_1: str = config_generator.add_no_housing()
        hvac_1: str = config_generator.add_no_hvac()
        # generating storage systems
        config_generator.clear_storage_system_ac()
        config_generator.clear_storage_system_dc()
        # setting up multiple configurations with manual naming of simulations

        config_set: dict = dict()
        count: int = 0

        room_tool_reader: RoomToolReader = RoomToolReader(room_tool_file)
        room_tool_entries = room_tool_reader.get_data_report()
        for current_number in range(len(room_tool_entries)):

            cell = room_tool_entries["Model"][current_number]
            serial, parallel = 1, 1
            current_config_generator = copy.deepcopy(config_generator)

            cell_type: str = 'IseaCellType;' + cell + '_00001'# + self.__CELL_EXT
            # serial, parallel = room_tool_reader.get_battery_scale()
            serial = int(room_tool_entries["Cells in series"][current_number])
            parallel = int(room_tool_entries["Cells in parallel"][current_number])
            energy = int(room_tool_entries["Energy (Wh)"][current_number])
            voltage_ic = int(room_tool_entries["Nom. module voltage (V)"][current_number])

            # room_tool_reader: RoomToolReader = RoomToolReader(room_tool_file, cell=cell)
            # print(serial, parallel)
            # capacity = room_tool_reader.get_energy()
            # voltage_ic = room_tool_reader.get_nominal_voltage()
            storage = current_config_generator.add_lithium_ion_battery(capacity=energy, cell_type=cell_type)
            ac_system_1: str = current_config_generator.add_storage_system_ac(ac_power, voltage_ic, acdc_1, housing_1,
                                                                          hvac_1)
            current_config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage)
            count += 1
            config: ConfigParser = current_config_generator.get_config()
            # Attention: SimSES can only handle ONE serial/parallel config for ALL batteries
            # config.add_section('BATTERY')
            config.set(BatteryConfig.SECTION, BatteryConfig.CELL_SERIAL_SCALE, str(serial))
            config.set(BatteryConfig.SECTION, BatteryConfig.CELL_PARALLEL_SCALE, str(parallel))
            config_set['storage_' + str(count)] = config
            # for section in config.sections():
            #     print(section)
            #     print(dict(config.items(section)))
            # config_generator.show()
        return config_set

    def _analysis_config(self) -> ConfigParser:
        config_generator: AnalysisConfigGenerator = AnalysisConfigGenerator()
        config_generator.print_results(False)
        config_generator.do_plotting(True)
        config_generator.do_batch_analysis(True)
        return config_generator.get_config()

    def clean_up(self) -> None:
        pass

    def __read_cell_config(self, filename: str, delimiter: str = ',') -> [[str]]:
        cell_config: [[str]] = list()
        with open(filename, 'r', newline='') as file:
            for line in file:
                line: str = line.rstrip()
                if not line or line.startswith('#') or line.startswith('"'):
                    continue
                cell_config.append(line.split(delimiter))
        return cell_config


if __name__ == "__main__":
    batch_processing: BatchProcessing = SimBAS()
    batch_processing.run()
    batch_processing.clean_up()
