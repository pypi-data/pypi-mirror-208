import os
from pathlib import Path

import numpy as np

from steam_pysigma.comsol.BuildGlobalVariables import BuildGlobalVariables
from steam_pysigma import pysigma as ps
from steam_pysigma.domain_generator.GeometryMultipole import GeometryMultipole


class BuildComsolModel:
    """
    Class take in domains and a configuration and builds a functioning comsol model saved as java.
    """

    def __init__(self, model_data=None, input_conductor_params=None,output_path=None, settings=None,
                 path_to_results=None, input_coordinates_path=None, roxie_data=None, bh_curve_database=None):
        """
        Class builds a comsol model.
        :param model_data: data dict from magnet_name.yaml
        :param input_conductor_params: magnet_name.set
        :param output_path: Output path of java files and mph model.
        :param settings: settings dict
        :param path_to_results: location of comsol-generated results
        :param input_coordinates_path: path to file with coordinates to evaluate B_field
        :param roxie_data: roxie data
        :param bh_curve_database: path to bh curve file
        """
        self.g = ps.GatewaySIGMA()
        self.a = ps.ArraysSIGMA
        self.model_data = model_data
        self.output_path = output_path
        self.roxie_data = roxie_data.Roxie_Data
        self.settings_dict = dict(settings)
        self.input_conductor_params = input_conductor_params
        self.funlib_map = ps.FunLibCSVReader().read_csv_funclib_create_hashmap(self.g)
        self.COMSOL_exe_path = Path(self.settings_dict['comsolexe_path']).parent
        self.java_jdk_path = self.settings_dict['JAVA_jdk_path']
        self.COMSOL_compile_path = os.path.join(self.COMSOL_exe_path, 'comsolcompile.exe')  # Change os.join()
        self.COMSOL_batch_path = os.path.join(self.COMSOL_exe_path, 'comsolbatch.exe')
        self.COMSOL_version = os.path.basename(os.path.dirname(self.COMSOL_exe_path.parent.parent)).replace("COMSOL",
                                                                                                            "")
        self.path_to_results = path_to_results if path_to_results != None else self.output_path
        self.bh_curve_database = bh_curve_database
        if self.COMSOL_version != "60" and self.COMSOL_version != "53a":
            raise Exception("Not supporting any other versions than 6.0 and 5.3a")

        self.model_name = f"{self.model_data.general_parameters.magnet_name}_Model"

        self.model_java_file_path = f"{os.path.join(self.output_path, self.model_name)}.java"
        self.compile_batch_file_path = f"{os.path.join(self.output_path, self.model_name)}_Compile_and_Open.bat"
        self.model_class_file_path = f"{os.path.join(self.output_path, self.model_name)}.class"
        self.split_java_file_path = []
        self.study_type = self.model_data.options_sigma.simulation.study_type
        self.num_qh = self.model_data.quench_protection.quench_heaters.N_strips
        self.make_batch_mode_executable = self.model_data.options_sigma.simulation.make_batch_mode_executable
        self.generate_study = self.model_data.options_sigma.simulation.generate_study
        self.input_coordinates_path = input_coordinates_path #str(self.model_data.options_sigma.postprocessing.out_2D_at_points.coordinate_source) if self.model_data.options_sigma.postprocessing.out_2D_at_points.coordinate_source!=None else None

        self.postprocessing_data = self.model_data.options_sigma.postprocessing
        self.variables2DConverted = self.postprocessing_data.out_2D_at_points.variables
        self.time2DConverted = self.postprocessing_data.out_2D_at_points.time  # List of all exported time
        self.variables1DvsTime = self.postprocessing_data.out_1D_vs_times.variables
        self.time1DConverted = self.postprocessing_data.out_1D_vs_times.time
        self.variables1DvsTimeVector = self.postprocessing_data.out_1D_vs_times.variables
        self.timeRange = ", ".join(["range(" + ", ".join(map(str, lst)) + ")" for lst in
                                    self.model_data.options_sigma.time_vector_solution.time_step])

        print(f"Comsol compile path {self.COMSOL_compile_path}")
        print(f"Comsol version {self.COMSOL_version}")

        self.cfg = self.setup_config_sigma()
        self.srv = self.g.TxtSigmaServer(self.cfg.getOutputModelPath(), self.cfg.getComsolBatchPath(),
                                         self.cfg.getComsolCompilePath())

        bgv = BuildGlobalVariables(self.g, self.model_data)
        bgv.validate_sigma_model_data()
        geom_multipole = GeometryMultipole(self.g, self.roxie_data, model_data, self.bh_curve_database, self.input_conductor_params,
                                           self.settings_dict)
        self.domains = geom_multipole.build_magnet()
        self.connect_create_MPH_model(self.domains)
        self.save_files_java()
        self.save_compile_and_open_bat()

    def setup_config_sigma(self):
        cfg = self.g.ConfigSigma()
        cfg.setComsolVersion(self.COMSOL_version)  # for sigma_60
        cfg.setOutputModelPath(self.model_java_file_path)
        cfg.setComsolBatchPath(self.COMSOL_batch_path)
        cfg.setComsolCompilePath(self.COMSOL_compile_path)
        cfg.setExternalCFunLibPath(self.settings_dict["CFunLibPath"])
        cfg.setRunStudy(self.make_batch_mode_executable)
        cfg.setNumOfQHs(self.num_qh)
        cfg.setStudyType(self.study_type)
        cfg.setSymFactor(1)
        if self.model_data.options_sigma.quench_initialization.quench_init_HT is not None:
            array = self.a.convert_list_to_string_array(self.g.gateway,
                                                        self.model_data.options_sigma.quench_initialization.quench_init_HT)
            cfg.setQuenchInitHT(array)
        if self.model_data.options_sigma.quench_initialization.quench_init_heat is not None:
            cfg.setQuenchInitHeat(float(self.model_data.options_sigma.quench_initialization.quench_init_heat))
        qh_positions = self.g.gateway.jvm.java.util.ArrayList()
        if self.model_data.options_sigma.quench_heaters.quench_heater_positions is not None:
            for qh in self.model_data.options_sigma.quench_heaters.quench_heater_positions:
                temp = self.g.gateway.jvm.java.util.ArrayList()
                for pos in qh:
                    temp.add(pos)
                qh_positions.add(temp)
            cfg.setQHPositions(qh_positions)
        return cfg

    def build_study(self):
        """
        If valid study time defined function creates a COMSOL study
        :return: None
        """
        if self.study_type is not None:
            if self.study_type == self.g.MPHC.LABEL_STATIONARY:
                # Add code to create and run study
                self.g.StudyAPI.setNewBasicStationaryStudy(self.srv, self.cfg, "sol1")
            elif self.study_type == self.g.MPHC.LABEL_TRANSIENT:
                self.g.StudyAPI.setNewMonolithicStudy(self.srv, self.cfg, "Default_study", self.timeRange)
            else:
                ValueError("Invaid study_type input")

    def create_results(self, input_coordinates_path, path_to_results):
        """
        Function creates SIGMA result objects to export
        :param input_coordinates_path: path to coordinate file to evaluate 2D variables in.
        :param path_to_results: path to result folder
        :return:
        """
        if self.make_batch_mode_executable:
            for i in range(len(self.variables2DConverted)):
                time_vector_2D = ', '.join(str(x) for x in self.time2DConverted[i])

                self.g.ResultsAPI.create2DResultNode(self.srv, self.cfg, self.variables2DConverted[i], time_vector_2D,
                                                     f"data {i}",
                                                     input_coordinates_path, str(path_to_results))
            if self.study_type == self.g.MPHC.LABEL_TRANSIENT:
                for j in range(len(self.variables1DvsTime)):
                    self.g.ResultsAPI.create1DResultNodeAllTimes(self.srv, self.cfg, self.variables1DvsTime[j],
                                                                 f"1DExport_{j}", path_to_results)

                for k in range(len(self.variables1DvsTimeVector)):
                    print(self.variables1DvsTimeVector[k], self.time1DConverted[k])

                    time_vector_1D = ', '.join(str(x) for x in self.time1DConverted[k])
                    self.g.ResultsAPI.create1DResultNodeTimeVector(self.srv, self.cfg, self.variables1DvsTimeVector[k],
                                                                   time_vector_1D,
                                                                   f"data {i + 1 + k}", path_to_results)
        else:
            pass
            # print("No study run, no results to be exported.")

    def connect_create_MPH_model(self, domains):
        """
        This function connects to the COMSOL server and creates an MPH model by using the MagnetMPHBuilder.
        It then builds the MPH model with the specified domains and global variables.
        If the study type is "Transient" and there are Quench Heaters present, it also builds a Quench Heater MPH model.

        :param domains: a tuple of domains to be included in the MPH model.
        :return: None
        """

        self.srv.connect(self.cfg.getComsolBatchPath())
        self.model = self.g.MagnetMPHBuilder(self.cfg, self.srv)
        # Create map with I0.
        global_map = BuildGlobalVariables(self.g, self.model_data).build_global_variables()
        global_map.put(self.g.MPHC.LABEL_CLIQ_CURRENT_EXT_INITIAL,
                       f"{self.model_data.power_supply.I_initial}")

        self.model = self.g.MagnetMPHBuilder(self.cfg, self.srv)
        self.model.buildMPH(self.a.create_domain_array(self.g.gateway, tuple(domains)), global_map, 4, 1,
                            self.funlib_map)

        if self.study_type == self.g.MPHC.LABEL_TRANSIENT and self.cfg.getNumOfQHs() > 0:
            builder_qh = self.g.QuenchHeaterMPHBuilder(self.cfg, self.srv)
            self.model.connectToServer()
            builder_qh.buildQuenchHeaterMPH()
        if self.generate_study:
            self.build_study()
            # Define result nodes

            self.create_results(self.input_coordinates_path, self.path_to_results)
            self.srv.build(self.cfg.getOutputModelPath())
            self.model.save()

    def save_files_java(self):
        with open(self.model_java_file_path) as java_file:

            print("Java file splitting started.")
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
                file_path = os.path.join(self.output_path, self.model_name)
                files += [open(file_path + '_%d.java' % i, 'w')]
                name = self.model_name + '_%d' % i
                self.split_java_file_path += [f"{os.path.join(self.output_path, self.model_name + '_%d' % i)}"]
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

        with open(self.model_java_file_path, 'w') as java_file:
            content = content[0:public_indexes[0] + 2] + ['\n'] + \
                      content[public_indexes[-1]:public_indexes[-1] + 2] + ['\t}\n'] + ['}\n']
            content.insert(public_indexes[0] + 2, '\t\tmph = ' + self.model_name + '_0.run1(mph);\n')
            ll = 1
            for name, item in additional_lines.items():
                for j in range(item['end'] - item['start'] + 1):
                    content.insert(public_indexes[0] + 2 + ll + j,
                                   '\t\tmph = ' + name + '.run' + str(item['start'] + j) + '(mph);\n')
                ll += j + 1
            content.insert(public_indexes[0] + 2 + ll, '\t\treturn mph;\n')
            content.insert(public_indexes[0] + 3 + ll, '\t}\n')
            java_file.writelines(content)
        print(f"BuilderSIGMA successfully saved files: {self.split_java_file_path}")

    def save_compile_and_open_bat(self):
        """
        Function writes a .bat file which has to be run to create a COMSOL model.
        :return: None
        """
        print("Excecuting bat file")
        script_lines = []
        class_paths = ''
        for file in self.split_java_file_path:
            script_lines += [f'"{self.COMSOL_compile_path}" -jdkroot "{self.java_jdk_path}" "{file}.java"',
                             f'"{self.java_jdk_path}\\bin\\jar.exe" cf "{file}.jar" "{file}.class"']
            class_paths += f'-classpathadd "{file}.jar" '

        script_lines += [
            f'"{self.COMSOL_compile_path}" -jdkroot "{self.java_jdk_path}" {class_paths}"{self.model_java_file_path}"',
            f'"{self.COMSOL_batch_path}" -inputfile "{self.model_class_file_path}" '
            f'-outputfile "{os.path.join(self.output_path, self.model_data.general_parameters.magnet_name)}.mph"']

        with open(self.compile_batch_file_path, "w") as outfile:
            outfile.write("\n".join(str(line) for line in script_lines))
        print(f'BuilderSIGMA successfully saved: {self.compile_batch_file_path}')
        os.chdir(self.output_path)
