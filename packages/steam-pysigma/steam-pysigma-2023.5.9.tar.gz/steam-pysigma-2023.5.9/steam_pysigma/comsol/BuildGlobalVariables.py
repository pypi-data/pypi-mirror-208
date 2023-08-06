import logging
import os

from steam_pysigma import pysigma as ps

class BuildGlobalVariables:
    def __init__(self, g, model_data):
        self.g = g
        self.model_data = model_data


    def validate_sigma_model_data(self):
        """
        Method checks the SIGMA options in the model_data to be valid to parse into SIGMA.
        :return:
        """
        model_data = self.model_data
        constants = self.g.MPHC
        logging.getLogger().setLevel(logging.INFO)

        # logging.warning('And this, too')
        options_sigma = model_data.options_sigma

        # Check key time_vector_solution.time_step
        time_step = options_sigma.time_vector_solution.time_step
        # Check type list[list] with three values
        if type(time_step) == list:
            if any(isinstance(el, list) for el in time_step):
                # Check data in vector is valid;
                for i in range(len(time_step)):
                    if len(time_step[i]) == 3:
                        if time_step[i][0] > time_step[i][2]:
                            raise ValueError(
                                "options_sigma.time_vector_solution.time_step has invalid data. Start value can not be larger than end value.")
                        else:
                           pass
                        if i <= len(time_step) - 2:
                            if time_step[i][2] > time_step[i + 1][0]:
                                raise ValueError(
                                    "options_sigma.time_vector_solution.time_step has overlapping time step intervals")
                    else:
                        raise ValueError(
                            "options_sigma.time_vector_solution.time_step has invalid data. Three element per sublist needed")

        # Check options_sigma.simulation
        study_type = options_sigma.simulation.study_type
        print(constants.LABEL_TRANSIENT)
        if study_type == constants.LABEL_TRANSIENT or study_type == constants.LABEL_STATIONARY:
            pass
        else:
            raise ValueError(f"String is not Transient or Stationary.")

        # Check options_sigma.physics
        if study_type == constants.LABEL_TRANSIENT:
            for key, value in options_sigma.physics:
                if key == "tauCC_PE":
                    pass
                elif value is None:
                    raise ValueError(f'{key} is set to null. To make sigma run this will be set to 0 as default.')

        # Check options_sigma.quench_initialization only valid if Transient
        if options_sigma.simulation.study_type == constants.LABEL_TRANSIENT:
            for key, value in options_sigma.quench_initialization:
                if "FLAG" in key:
                    if value is None:
                        raise ValueError(f'{key} is set to null. To make sigma run this will be set to 0 as default.')
                if key == "num_qh_div":
                    if len(value) != model_data.quench_protection.quench_heaters.N_strips:
                        raise ValueError(
                            f"The number of quench heater divisions must be {model_data.quench_protection.quench_heaters.N_strips}")
                if key == "quench_init_heat":
                    if value is None:
                        raise ValueError(f"{key} can't be none")
                    else:
                        if value < 0:
                            raise ValueError("Power for initialize quench can't be negative")
                if key == "quench_stop_temp":
                    if value is None:
                        raise ValueError(f"{key} can't be none")
                    if value < 0:
                        raise ValueError("Tempereatur for initialize quench can't be negative")

        # Check options_sigma.postprocessing.out_2D_at_points
        for key, value in options_sigma.postprocessing.out_2D_at_points:
            if key == "coordinate_source":
                # Check if source exists
                if value is not None:
                    if not os.path.exists(value):
                        raise ValueError("Given coordinate file path does not exist")

                    else:
                        logging.info("Using coordinate file to evaluate 2D plots")

            if options_sigma.simulation.study_type == constants.LABEL_TRANSIENT:
                if key == "time":
                    # Check number of values
                    if len(value) != len(options_sigma.postprocessing.out_2D_at_points.variables):
                        raise ValueError("Number of time vectors must be the same as number of variables.")
                    else:
                        for i in range(len(value)):
                            if len(value[i]) == 3:
                                if value[0] > value[2]:
                                    raise ValueError(
                                        "options_sigma.postprocessing.out_2D_at_points.time has invalid data. Start value can not be larger than end value.")
                                else:
                                    pass
                            else:
                                raise ValueError(
                                    "options_sigma.postprocessing.out_2D_at_points.time has invalid data. Three elements needed.")
        if options_sigma.simulation.study_type == constants.LABEL_TRANSIENT:
            for key, value in options_sigma.postprocessing.out_1D_vs_times:
                if key == "time":
                    # Check number of values
                    if len(value) != len(options_sigma.postprocessing.out_1D_vs_times.variables):
                        raise ValueError("Number of time vectors must be the same as number of variables.")
                    else:
                        for i in range(len(value)):
                            if len(value[i]) == 3:
                                if value[0] > value[2]:
                                    raise ValueError(
                                        f"options_sigma.postprocessing.out_1D_vs_times.time has invalid data for value {value}. Start value can not be larger than end value.")
                            else:
                                raise ValueError(
                                    "options_sigma.postprocessing.out_1D_vs_times.time has invalid data. Three elements needed.")

        # options_sigma.quench_heaters
        # th_coils = options_sigma.quench_heaters.th_coils
        # if 0 in th_coils:
        #     raise ValueError("List contains zero values")

    def helper_check_time_step_valid(self, time_step):
        if type(time_step) == list:
            if any(isinstance(el, list) for el in time_step):
                # Check data in vector is valid;
                for i in range(len(time_step)):
                    if len(time_step[i]) == 3:
                        if time_step[i][0] > time_step[i][2]:
                            raise ValueError(
                                "#options_sigma.time_vector_solution.time_step has invalid data. Start value can not be larger than end value.")
                        else:
                            pass
                        if i <= len(time_step) - 2:
                            if time_step[i][2] > time_step[i + 1][0]:
                                raise ValueError(
                                    "options_sigma.time_vector_solution.time_step has overlapping time step intervals")
                    else:
                        raise ValueError(
                            "options_sigma.time_vector_solution.time_step has invalid data. Three element per sublist needed")
    def build_global_variables(self):
        """
        Function builds all global variables nessesary for QH simulations.
        :return: map with global variables
        """
        map = self.g.gateway.jvm.java.util.HashMap()
        constants = self.g.MPHC
        # Cliq variables:
        end_sim_time = self.model_data.options_sigma.time_vector_solution.time_step[-1][-1]

        R_crow = self.model_data.circuit.R_circuit
        L_circuit = self.model_data.circuit.L_circuit
        C_cliq = self.model_data.quench_protection.cliq.C
        L_cliq = self.model_data.quench_protection.cliq.L

        V_cliq_0 = self.model_data.quench_protection.cliq.U0
        I_cliq_0 = self.model_data.quench_protection.cliq.I0

        sym_factor = self.model_data.quench_protection.cliq.sym_factor
        cliq_time = self.model_data.quench_protection.cliq.t_trigger
        if cliq_time > end_sim_time:
            with_cliq = 0
        else:
            with_cliq = 1

        if V_cliq_0 == None:
            V_cliq_0 = 0
        if I_cliq_0 == None:
            I_cliq_0 = 0
        if sym_factor == None:
            sym_factor = 1
        if L_circuit == None:
            L_circuit = "1e-6"
        if L_cliq == None:
            L_cliq = "1e-6"
        map.put(constants.LABEL_CLIQ_RCROW, str(R_crow))
        map.put(constants.LABEL_CLIQ_LCIR, str(L_circuit))
        map.put(constants.LABEL_CLIQ_CAPASITOR, str(C_cliq))
        map.put(constants.LABEL_CLIQ_INDUCTANCE, str(L_cliq))
        map.put(constants.LABEL_CLIQ_VOLTAGE_INITIAL, str(V_cliq_0))
        map.put(constants.LABEL_CLIQ_CURRENT_INITIAL, str(I_cliq_0))
        map.put(constants.LABEL_CLIQ_SYMFACTOR, str(sym_factor))
        map.put(constants.LABEL_CLIQ_SWITCH, str(with_cliq))

        FLAG_M_pers = self.model_data.options_sigma.physics.FLAG_M_pers
        FLAG_M_pers = "0" if FLAG_M_pers is None else FLAG_M_pers

        FLAG_ifcc = self.model_data.options_sigma.physics.FLAG_ifcc
        FLAG_ifcc = "0" if FLAG_ifcc is None else FLAG_ifcc

        FLAG_iscc_crossover = self.model_data.options_sigma.physics.FLAG_iscc_crossover
        FLAG_iscc_crossover = "0" if FLAG_iscc_crossover is None else FLAG_iscc_crossover

        FLAG_iscc_adjw = self.model_data.options_sigma.physics.FLAG_iscc_adjw
        FLAG_iscc_adjw = "0" if FLAG_iscc_adjw is None else FLAG_iscc_adjw

        FLAG_iscc_adjn = self.model_data.options_sigma.physics.FLAG_iscc_adjn
        FLAG_iscc_adjn = "0" if FLAG_iscc_adjn is None else FLAG_iscc_adjn

        FLAG_quench_all = self.model_data.options_sigma.quench_initialization.FLAG_quench_all
        FLAG_quench_all = "0" if FLAG_quench_all is None else FLAG_quench_all

        FLAG_quench_off = self.model_data.options_sigma.quench_initialization.FLAG_quench_off
        FLAG_quench_off = "0" if FLAG_quench_off is None else FLAG_quench_off

        PARAM_time_quench = self.model_data.options_sigma.quench_initialization.PARAM_time_quench
        PARAM_time_quench = "0" if PARAM_time_quench is None else PARAM_time_quench

        magnetic_length = self.model_data.general_parameters.magnetic_length
        T_initial = self.model_data.general_parameters.T_initial

        quench_heat = self.model_data.options_sigma.quench_initialization.quench_init_heat
        quench_temp = self.model_data.options_sigma.quench_initialization.quench_stop_temp

        map.put(constants.LABEL_FLAG_IFCC, str(FLAG_ifcc))
        map.put(constants.LABEL_FLAG_ISCC_CROSSOVER, str(FLAG_iscc_crossover))
        map.put(constants.LABEL_FLAG_ISCC_ADJW, str(FLAG_iscc_adjw))
        map.put(constants.LABEL_FLAG_ISCC_ADJN, str(FLAG_iscc_adjn))
        map.put(constants.LABEL_FLAG_MPERS, str(FLAG_M_pers))
        map.put(constants.LABEL_FLAG_QUENCH_ALL, str(FLAG_quench_all))
        map.put(constants.LABEL_FLAG_QUENCH_OFF, str(FLAG_quench_off))
        map.put(constants.LABEL_PARAM_QUENCH_TIME, str(PARAM_time_quench))
        map.put(constants.LABEL_MAGNETIC_LENGTH, str(magnetic_length))
        map.put(constants.LABEL_OPERATIONAL_TEMPERATUR, str(T_initial))
        map.put(constants.LABEL_INIT_QUENCH_HEAT, str(quench_heat))
        map.put(constants.LABEL_QUENCH_TEMP, str(quench_temp))

        ins_list = self.model_data.quench_protection.quench_heaters.s_ins
        w_list = self.model_data.quench_protection.quench_heaters.w
        qh_to_bath_list = self.model_data.quench_protection.quench_heaters.s_ins_He
        qh_steel_strip = self.model_data.quench_protection.quench_heaters.h
        tau = [round(a * b, 4) for a, b in
               zip(self.model_data.quench_protection.quench_heaters.R_warm, self.model_data.quench_protection.quench_heaters.C)]
        num_qh_div = self.model_data.options_sigma.quench_initialization.num_qh_div
        u_init = self.model_data.quench_protection.quench_heaters.U0
        i_init = [round(a / b, 3) for a, b in zip(self.model_data.quench_protection.quench_heaters.U0,
                                                  self.model_data.quench_protection.quench_heaters.R_warm)]
        frac_heater = self.model_data.quench_protection.quench_heaters.f_cover
        trigger_time = self.model_data.quench_protection.quench_heaters.t_trigger
        ins_thick_to_coil = self.model_data.options_sigma.quench_heaters.th_coils
        lengths_qh = self.model_data.quench_protection.quench_heaters.l

        for i in range(self.model_data.quench_protection.quench_heaters.N_strips):
            if self.model_data.options_sigma.time_vector_solution.time_step[-1][-1] < trigger_time[i]:
                trigger_time[i] = self.model_data.options_sigma.time_vector_solution.time_step[-1][-1]
            map.put(constants.LABEL_INSULATION_THICKNESS_QH_TO_COIL + str(i + 1), str(ins_list[i]))
            map.put(constants.LABEL_WIDTH_QH + str(i + 1), str(w_list[i]))
            map.put(constants.LABEL_INSULATION_THICKNESS_QH_TO_BATH + str(i + 1), str(qh_to_bath_list[i]))
            map.put(constants.LABEL_INSULATION_THICKNESS_QH_STRIP + str(i + 1), str(qh_steel_strip[i]))
            map.put(constants.LABEL_EXPONENTIAL_TIME_CONSTANT_DECAY + str(i + 1), str(tau[i]))
            map.put(constants.LABEL_QH + constants.LABEL_L + str(i + 1), str(lengths_qh[i]))
            map.put(constants.LABEL_NUMBER_OF_QH_SUBDIVISIONS + str(i + 1), str(num_qh_div[i]))
            map.put(constants.LABEL_INITIAL_QH_CURRENT + str(i + 1), str(i_init[i]))
            map.put(constants.LABEL_INITIAL_QH_VOLTAGE + str(i + 1), str(u_init[i]))
            map.put(constants.LABEL_QH + str(i + 1) + constants.LABEL_FRACTION_OF_QH_STATION, str(frac_heater[i]))
            map.put(constants.LABEL_TRIGGER_TIME_QH + str(i + 1), str(trigger_time[i]))
            map.put(constants.LABEL_INSULATION_THICKNESS_TO_COIL + str(i + 1), str(ins_thick_to_coil[i]))

        return map
