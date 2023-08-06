import os
import subprocess

import numpy as np


def run(magnet_name, working_dir_path, model_java_file_path, model_class_file_path, output_path, model_name,
        split_java_file_path, COMSOL_compile_path, COMSOL_batch_path, compile_batch_file_path, java_jdk_path):
    os.chdir(working_dir_path)
    with open(model_java_file_path) as java_file:
        print("Creating java files initialized.")
        max_no_lines = 6e4
        public_indexes = []
        files = []
        content = java_file.readlines()
        for i, line in enumerate(content):
            if "public static" in line:
                public_indexes += [i]

        no_lines = public_indexes[-1] - public_indexes[0]
        no_files = int(np.ceil(no_lines / max_no_lines))
        max_no_lines = round(no_lines / no_files)
        real_indexes = [public_indexes[i] - public_indexes[0] for i in range(len(public_indexes))]
        closest = [min(real_indexes, key=lambda x: abs(x - max_no_lines * (i + 1))) + public_indexes[0]
                   for i in range(no_files)]
        no_run = [int(content[i][content[i].index('run') + 3:content[i].index('(')]) for i in closest[0:-1]]
        no_run += [int(content[public_indexes[-2]][content[public_indexes[-2]].index('run')
                                                   + 3:content[public_indexes[-2]].index('(')]) + 1]
        additional_lines = {}
        for i in range(no_files):
            file_path = os.path.join(output_path, model_name)
            files += [open(file_path + '_%d.java' % i, 'w')]
            name = model_name + '_%d' % i
            split_java_file_path += [f"{os.path.join(output_path, model_name + '_%d' % i)}"]
            files[i].writelines(content[0:public_indexes[0] - 2] + ['public class ' + name + ' {\n', '\n'])
            if i == 0:
                files[i].writelines('\tpublic static Model run1(Model mph) {\n')
                files[i].writelines(content[public_indexes[0] + 2:closest[i]] + ['}\n'])
                additional_lines[name] = {'start': 2, 'end': no_run[i] - 1}
            elif i + 1 == no_files:
                files[i].writelines(content[closest[i - 1]:public_indexes[-1]] + ['}\n'])
                additional_lines[name] = {'start': no_run[i - 1], 'end': len(public_indexes) - 1}
            else:
                files[i].writelines(content[closest[i - 1]:closest[i]] + ['}\n'])
                additional_lines[name] = {'start': no_run[i - 1], 'end': no_run[i] - 1}
            files[i].close()

    with open(model_java_file_path, 'w') as java_file:
        content = content[0:public_indexes[0] + 2] + ['\n'] + \
                  content[public_indexes[-1]:public_indexes[-1] + 2] + ['\t}\n'] + ['}\n']
        content.insert(public_indexes[0] + 2, '\t\tmph = ' + model_name + '_0.run1(mph);\n')
        ll = 1
        for name, item in additional_lines.items():
            for j in range(item['end'] - item['start'] + 1):
                content.insert(public_indexes[0] + 2 + ll + j,
                               '\t\tmph = ' + name + '.run' + str(item['start'] + j) + '(mph);\n')
            ll += j + 1
        content.insert(public_indexes[0] + 2 + ll, '\t\treturn mph;\n')
        content.insert(public_indexes[0] + 3 + ll, '\t}\n')
        java_file.writelines(content)
    print("Creating java files DONE.")
    print("Excecuting bat file")
    script_lines = []
    class_paths = ''
    for file in split_java_file_path:
        script_lines += [f'"{COMSOL_compile_path}" -jdkroot "{java_jdk_path}" "{file}.java"',
                         f'"{java_jdk_path}\\bin\\jar.exe" cf "{file}.jar" "{file}.class"']
        class_paths += f'-classpathadd "{file}.jar" '

    script_lines += [
        f'"{COMSOL_compile_path}" -jdkroot "{java_jdk_path}" {class_paths}"{model_java_file_path}"',
        f'"{COMSOL_batch_path}" -inputfile "{model_class_file_path}" '
        f'-outputfile "{os.path.join(output_path, magnet_name)}.mph" ']

    with open(compile_batch_file_path, "w") as outfile:
        outfile.write("\n".join(str(line) for line in script_lines))

    proc = subprocess.Popen([compile_batch_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        print(stderr)
    else:
        print(stdout)


def build_global_variables(g, model_data):
    map = g.gateway.jvm.java.util.HashMap()
    constants = g.constants
    end_sim_time = model_data["Options_SIGMA"]["time_vector_solution"]["time_step"][-1][-1]
    # Cliq variables:
    R_crow =  model_data['Circuit']['R_circuit']
    L_circuit =model_data['Circuit']['L_circuit']
    C_cliq = model_data['Quench_Protection']['CLIQ']['C']
    L_cliq = model_data['Quench_Protection']['CLIQ']['L']

    V_cliq_0 = model_data['Quench_Protection']['CLIQ']['U0']
    I_cliq_0 = model_data['Quench_Protection']['CLIQ']['I0']


    sym_factor = model_data['Quench_Protection']['CLIQ']['sym_factor']
    cliq_time = model_data['Quench_Protection']['CLIQ']['t_trigger']
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

    FLAG_M_pers = model_data['Options_SIGMA']['physics']['FLAG_M_pers']
    FLAG_M_pers = "0" if FLAG_M_pers is None else FLAG_M_pers

    FLAG_ifcc = model_data['Options_SIGMA']['physics']['FLAG_ifcc']
    FLAG_ifcc = "0" if FLAG_ifcc is None else FLAG_ifcc

    FLAG_iscc_crossover = model_data['Options_SIGMA']['physics']['FLAG_iscc_crossover']
    FLAG_iscc_crossover = "0" if FLAG_iscc_crossover is None else FLAG_iscc_crossover

    FLAG_iscc_adjw = model_data['Options_SIGMA']['physics']['FLAG_iscc_adjw']
    FLAG_iscc_adjw = "0" if FLAG_iscc_adjw is None else FLAG_iscc_adjw

    FLAG_iscc_adjn = model_data['Options_SIGMA']['physics']['FLAG_iscc_adjn']
    FLAG_iscc_adjn = "0" if FLAG_iscc_adjn is None else FLAG_iscc_adjn

    FLAG_quench_all = model_data['Options_SIGMA']['quench_initialization']['FLAG_quench_all']
    FLAG_quench_all = "0" if FLAG_quench_all is None else FLAG_quench_all

    FLAG_quench_off = model_data['Options_SIGMA']['quench_initialization']['FLAG_quench_off']
    FLAG_quench_off = "0" if FLAG_quench_off is None else FLAG_quench_off

    PARAM_time_quench = model_data['Options_SIGMA']['quench_initialization']['PARAM_time_quench']
    PARAM_time_quench = "0" if PARAM_time_quench is None else PARAM_time_quench

    magnetic_length = model_data['GeneralParameters']['magnetic_length']
    T_initial = model_data['GeneralParameters']['T_initial']

    map.put(constants.LABEL_FLAG_IFCC, FLAG_ifcc)
    map.put(constants.LABEL_FLAG_ISCC_CROSSOVER, FLAG_iscc_crossover)
    map.put(constants.LABEL_FLAG_ISCC_ADJW, FLAG_iscc_adjw)
    map.put(constants.LABEL_FLAG_ISCC_ADJN, FLAG_iscc_adjn)
    map.put(constants.LABEL_FLAG_MPERS, FLAG_M_pers)
    map.put(constants.LABEL_FLAG_QUENCH_ALL, FLAG_quench_all)
    map.put(constants.LABEL_FLAG_QUENCH_OFF, FLAG_quench_off)
    map.put(constants.LABEL_PARAM_QUENCH_TIME, PARAM_time_quench)
    map.put(constants.LABEL_MAGNETIC_LENGTH, magnetic_length)
    map.put(constants.LABEL_OPERATIONAL_TEMPERATUR, str(T_initial))
    map.put(constants.LABEL_INIT_QUENCH_HEAT, str(50000))
    map.put(constants.LABEL_QUENCH_TEMP, str(10))


    num_qh = model_data['Quench_Protection']['Quench_Heaters']['N_strips']
    ins_list = model_data['Quench_Protection']['Quench_Heaters']['s_ins']
    w_list = model_data['Quench_Protection']['Quench_Heaters']['w']
    qh_to_bath_list = model_data['Quench_Protection']['Quench_Heaters']['s_ins_He']
    qh_steel_strip = model_data['Quench_Protection']['Quench_Heaters']['h']
    tau = [round(a * b, 4) for a, b in zip(model_data['Quench_Protection']['Quench_Heaters']['R_warm'],
                                           model_data['Quench_Protection']['Quench_Heaters']['C'])]
    num_qh_div = model_data['Options_SIGMA']['quench_initialization']['num_qh_div']
    u_init = model_data['Quench_Protection']['Quench_Heaters']['U0']
    frac_heater = [round(a / b, 4) for a, b in
                   zip(model_data['Quench_Protection']['Quench_Heaters']['l_stainless_steel'], [sum(x) for x in zip(
                       model_data['Quench_Protection']['Quench_Heaters']['l_stainless_steel'],
                       model_data['Quench_Protection']['Quench_Heaters']['l_copper'])])]
    trigger_time = model_data['Quench_Protection']['Quench_Heaters']['t_trigger']
    ins_thick_to_coil = model_data['Options_SIGMA']['quench_initialization']['th_coils']
    lengths_qh = model_data['Quench_Protection']['Quench_Heaters']['l']

    for i in range(num_qh):
        if model_data["Options_SIGMA"]["time_vector_solution"]["time_step"][-1][-1] < trigger_time[i]:
            trigger_time[i] = end_sim_time + model_data["Options_SIGMA"]["time_vector_solution"]["time_step"][-1][-2]
        map.put(constants.LABEL_INSULATION_THICKNESS_QH_TO_COIL + str(i + 1), str(ins_list[i]))
        map.put(constants.LABEL_WIDTH_QH + str(i + 1), str(w_list[i]))
        map.put(constants.LABEL_INSULATION_THICKNESS_QH_TO_BATH + str(i + 1), str(qh_to_bath_list[i]))
        map.put(constants.LABEL_INSULATION_THICKNESS_QH_STRIP + str(i + 1), str(qh_steel_strip[i]))
        map.put(constants.LABEL_EXPONENTIAL_TIME_CONSTANT_DECAY + str(i + 1), str(tau[i]))
        map.put(constants.LABEL_NUMBER_OF_QH_SUBDIVISIONS + str(i + 1), str(num_qh_div[i]))
        map.put(constants.LABEL_QH + constants.LABEL_L + str(i + 1), str(lengths_qh[i]))
        map.put(constants.LABEL_QH + str(i + 1) + constants.LABEL_FRACTION_OF_QH_STATION, str(frac_heater[i]))
        map.put(constants.LABEL_TRIGGER_TIME_QH + str(i + 1), str(trigger_time[i]))
        map.put(constants.LABEL_INSULATION_THICKNESS_TO_COIL + str(i + 1), str(ins_thick_to_coil[i]))
        map.put(constants.LABEL_INITIAL_QH_VOLTAGE + str(i + 1), str(u_init[i]))

    return map





def build_study(study_type, srv, cfg, study_API, timeRange):
    if study_type is not None:
        if study_type == "Stationary":
            # Add code to create and run study
            study_API.setNewBasicStationaryStudy(srv, cfg, "sol1")
        elif (study_type == "Transient"):
            study_API.setNewMonolithicStudy(srv, cfg, "Default_study", timeRange)


def create_results(srv, cfg, variables1DvsTime, time2DConverted, variables2DConverted, time1DConverted,
                   variables1DvsTimeVector,
                   result_api, input_coordinates_path, path_to_results):

    for i in range(len(variables2DConverted)):
        if len(time2DConverted)>1:
            time_vector_2D = ', '.join(str(x) for x in time2DConverted[i])

        else:
            time_vector_2D = time2DConverted[0]
        result_api.create2DResultNode(srv, cfg, variables2DConverted[i], time_vector_2D, f"data {i}",
                                      input_coordinates_path, path_to_results)
    for j in range(len(time1DConverted)):
        if len(time2DConverted)>1:
            time_vector_1D = ', '.join(str(x) for x in time1DConverted[j])

        else:
            time_vector_1D = time1DConverted[0]

    if cfg.getStudyType() == "Transient":
        for j in range(len(variables1DvsTime)):
            result_api.create1DResultNodeAllTimes(srv, cfg, variables1DvsTime[j], f"1DExport_{j}", path_to_results)

        for k in range(len(variables1DvsTimeVector)):
            result_api.create1DResultNodeTimeVector(srv, cfg, variables1DvsTimeVector[k], time_vector_1D,
                                                    f"data {i + j + 1 + k}", path_to_results)
