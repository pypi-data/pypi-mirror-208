import os
from pathlib import Path

import pandas as pd
from py4j.java_gateway import launch_gateway, JavaGateway, GatewayParameters


class SetupConfigSIGMA:
    def __init__(self, g, model_java_file_path, COMSOL_batch_path, COMSOL_compile_path, funLibPath, run_study, numOfQH,
                 study_type, qh_positions, quench_init_HTs=None, quench_init_heat=None):
        self.cfg = g.ConfigSigma()
        self.cfg.setOutputModelPath(model_java_file_path)
        self.cfg.setComsolBatchPath(COMSOL_batch_path)
        self.cfg.setComsolCompilePath(COMSOL_compile_path)
        self.cfg.setExternalCFunLibPath(funLibPath)
        self.cfg.setRunStudy(run_study)
        self.cfg.setNumOfQHs(numOfQH)
        self.cfg.setStudyType(study_type)
        QHPositions = g.gateway.jvm.java.util.ArrayList()
        for qh in qh_positions:
            temp = g.gateway.jvm.java.util.ArrayList()
            for pos in qh:
                temp.add(pos)
            QHPositions.add(temp)
        self.cfg.setQHPositions(QHPositions)
        if quench_init_HTs != None and len(quench_init_HTs)>0:
            array = ArraysSIGMA.convert_list_to_string_array(g.gateway, quench_init_HTs)
            self.cfg.setQuenchInitHT(array)
            self.cfg.setQuenchInitHeat(quench_init_heat)


class GatewaySIGMA:
    """
    Python wrapper for SIGMA jars exposes java methods and attributes.
    """

    def __init__(self):
        jars_path = os.path.join(Path(__file__).parent, '*')
        print(
            f"PySIGMA started and uses {[each for each in os.listdir(Path(__file__).parent) if each.endswith('.jar')][0]}")
        # print(f"OS environ paths: {os.environ}")
        # print(jars_path)
        # print(type(jars_path))
        # # print(os.listdir(Path(jars_path).resolve()))
        #
        # jars_path = os.path.join('steam_sdk', 'wrappers', 'java', 'SIGMA', 'jars', '*')
        # print(jars_path)
        # print(Path(jars_path).resolve())
        # print(type(jars_path))
        # print(os.listdir(Path(jars_path).parent.resolve()))

        self.port = launch_gateway(classpath=jars_path, die_on_exit=True)

        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(port=self.port))
        self.Point = self.gateway.jvm.model.geometry.basic.Point
        self.Line = self.gateway.jvm.model.geometry.basic.Line
        self.Arc = self.gateway.jvm.model.geometry.basic.Arc
        self.EllipticArc = self.gateway.jvm.model.geometry.basic.EllipticArc
        self.Circumference = self.gateway.jvm.model.geometry.basic.Circumference
        self.Area = self.gateway.jvm.model.geometry.basic.Area
        self.HyperLine = self.gateway.jvm.model.geometry.basic.HyperLine
        self.Element = self.gateway.jvm.model.geometry.Element
        self.Domain = self.gateway.jvm.model.domains.Domain
        self.AirFarFieldDomain = self.gateway.jvm.model.domains.database.AirFarFieldDomain
        self.AirDomain = self.gateway.jvm.model.domains.database.AirDomain
        self.IronDomain = self.gateway.jvm.model.domains.database.IronDomain
        self.HoleDomain = self.gateway.jvm.model.domains.database.HoleDomain
        self.CoilDomain = self.gateway.jvm.model.domains.database.CoilDomain
        self.WedgeDomain = self.gateway.jvm.model.domains.database.WedgeDomain
        self.MatDatabase = self.gateway.jvm.model.materials.database.MatDatabase
        self.ConfigSigma = self.gateway.jvm.config.ConfigSigma
        self.TxtSigmaServer = self.gateway.jvm.server.TxtSigmaServer
        self.MagnetMPHBuilder = self.gateway.jvm.comsol.MagnetMPHBuilder
        self.QuenchHeaterMPHBuilder = self.gateway.jvm.comsol.QuenchHeaterMPHBuilder
        self.Cable = self.gateway.jvm.model.geometry.coil.Cable
        self.Winding = self.gateway.jvm.model.geometry.coil.Winding
        self.Pole = self.gateway.jvm.model.geometry.coil.Pole
        self.Coil = self.gateway.jvm.model.geometry.coil.Coil
        self.Magnet_T0_QH = self.gateway.jvm.input.OthersT0.Magnet_T0_QH
        self.Magnet_T1_QH = self.gateway.jvm.input.OthersT0.Magnet_T1_QH
        self.MPHC = self.gateway.jvm.comsol.constants.MPHC
        self.StudyAPI = self.gateway.jvm.comsol.api.StudyAPI
        self.ResultsAPI = self.gateway.jvm.comsol.api.ResultsAPI
        self.constants = self.gateway.jvm.comsol.constants.MPHC
    # def __del__(self):
    #     self.gateway.shutdown()


class ArraysSIGMA:

    @staticmethod
    def create_hyper_line_array(gateway, args):
        HyperLine = gateway.jvm.model.geometry.basic.HyperLine
        if type(args) is tuple:
            hl_array = gateway.new_array(HyperLine, len(args))
            for i in range(len(args)):
                hl_array[i] = args[i]
        else:
            hl_array = gateway.new_array(HyperLine, 1)
            hl_array[0] = args
        return hl_array

    @staticmethod
    def create_element_array(gateway, args):
        Element = gateway.jvm.model.geometry.Element
        if type(args) is tuple:
            el_array = gateway.new_array(Element, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(Element, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_string_array(gateway, args):
        if any(var_type is type(args) for var_type in [tuple, list]):
            el_array = gateway.new_array(gateway.jvm.String, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(gateway.jvm.String, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_double_array(gateway, args):
        if type(args) is tuple:
            el_array = gateway.new_array(gateway.jvm.double, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(gateway.jvm.double, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_int_array(gateway, args):
        if type(args) is tuple:
            el_array = gateway.new_array(gateway.jvm.int, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(gateway.jvm.int, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_domain_array(gateway, args):
        Domain = gateway.jvm.model.domains.Domain
        if type(args) is tuple:
            el_array = gateway.new_array(Domain, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(Domain, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_area_array(gateway, args):
        Area = gateway.jvm.model.geometry.basic.Area
        if type(args) is tuple:
            el_array = gateway.new_array(Area, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(Area, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def convert_list_to_double_array(gateway, arg):
        el_array = gateway.new_array(gateway.jvm.Double, len(arg))
        for i in range(len(arg)):
            el_array[i] = float(arg[i])
        return el_array

    @staticmethod
    def convert_list_to_string_array(gateway, arg):
        el_array = gateway.new_array(gateway.jvm.String, len(arg))
        for i in range(len(arg)):
            el_array[i] = arg[i]
        return el_array

    @staticmethod
    def create_winding_array(gateway, args):
        Winding = gateway.jvm.model.geometry.coil.Winding
        if type(args) is tuple:
            el_array = gateway.new_array(Winding, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(Winding, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def create_pole_array(gateway, args):
        Pole = gateway.jvm.model.geometry.coil.Pole
        if type(args) is tuple:
            el_array = gateway.new_array(Pole, len(args))
            for i in range(len(args)):
                el_array[i] = args[i]
        else:
            el_array = gateway.new_array(Pole, 1)
            el_array[0] = args
        return el_array

    @staticmethod
    def parse_java_array(java_array):
        rows = len(java_array)
        cols = len(java_array[0])

        array = [[0 for x in range(rows)] for y in range(cols)]

        for i in range(rows):
            for j in range(cols):
                array[i][j] = java_array[i][j]
        return array

    @staticmethod
    def create_double_2D_array(gateway, input_array):
        output_array = gateway.new_array(gateway.jvm.Double, len(input_array), len(input_array[0]))
        for r in range(len(input_array)):
            for c in range(len(input_array[r])):
                output_array[r][c] = input_array[r][c]
        return output_array

    @staticmethod
    def create_unboxed_double_2D_array(gateway, input_array):
        output_array = gateway.new_array(gateway.jvm.double, len(input_array), len(input_array[0]))
        for r in range(len(input_array)):
            for c in range(len(input_array[r])):
                output_array[r][c] = input_array[r][c]
        return output_array


class FunLibCSVReader:
    def __init__(self):
        pass

    def read_csv_funclib_create_hashmap(self, gs: GatewaySIGMA = None):
        df = pd.read_csv(os.path.join(Path(__file__).parent, 'CFUN_mapping.csv'))
        funlib_map = gs.gateway.jvm.java.util.HashMap()
        for index, row in df.iterrows():
            funlib_map.put(row['SIGMA_name'], row['File_name'])
        return funlib_map
