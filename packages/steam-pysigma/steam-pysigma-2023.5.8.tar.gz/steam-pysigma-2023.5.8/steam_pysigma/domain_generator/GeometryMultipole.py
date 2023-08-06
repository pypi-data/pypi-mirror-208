import os.path
from pathlib import Path

from steam_pysigma.parsers.ParserRoxie import arcCenter
import steam_pysigma.pysigma as ps


class GeometryMultipole:
    """
    Class creates SIGMA domain objects
    IMPROVMENTS:
    No dependency on config sigma
    """

    def __init__(self, g, input_roxie_data, input_model_data, input_conductor_params, settings_dict, flag_build=True,
                 verbose=False):

        self.model_data = input_model_data
        self.roxie_data = input_roxie_data
        self.input_conductor_params = input_conductor_params
        self.bh_curve_database = Path.joinpath(Path(__file__).parent,
                                               input_model_data.sources.bh_curve_source).resolve()
        print(self.bh_curve_database)
        self.settings_dict: dict = settings_dict
        self.verbose = verbose
        if (not self.model_data or not self.roxie_data) and flag_build:
            raise Exception('Cannot build model without providing DataModelMagnet and RoxieData')
        elif flag_build:
            self.g = g
            self.a = ps.ArraysSIGMA
            self.cfg = self.g.ConfigSigma()
            self.cfg.setComsolVersion("53a")
            self.max_r: float = 0.1
            self.conductor_name = str
            self.cableParameters = {'cable': {}, 'strand': {}, 'Jc_fit': {}}  # dM.Conductor #self.cablesParameters
            # self.wedge_elements =
            # self.model =
            self.coil = []
            self.elements = {}
            self.coil_areas = []
            self.wedge_areas = []


    def build_magnet(self):
        """
        This function builds a magnet and creates the different domains.

        :return: None
        """
        if self.verbose: print(f"SIGMA started generating {self.model_data.GeneralParameters.magnet_name}")
        self.air_ff_domain()
        self.air_domain()
        self.coil_domain()
        self.iron_yoke_domain()
        self.wedge_domain()
        return self.get_all_domains()
        # self.bh_curve()

    def coil_domain(self):
        """
        Function creates winding blocks domain
        :return: None
        """
        poles = ()
        for coil_nr, coil in self.roxie_data.coil.coils.items():
            for pole_nr, pole in coil.poles.items():
                windings = ()
                for layer_nr, layer in pole.layers.items():
                    for winding_key, winding in layer.windings.items():
                        self.conductor_name = winding.conductor_name
                        # self.cableParameters = self.roxie_data.conductor.conductor[winding.conductor_name].parameters
                        self.cable_domain(conductor=winding.conductor_name)  # Overwritten
                        areas = ()
                        currents = ()
                        for block_key, block in winding.blocks.items():
                            currents += (block.current_sign,)
                            # kp0 = self.g.Point.ofCartesian(coil.bore_center.x, coil.bore_center.y)
                            bore = coil.bore_center
                            if (
                                    block.block_corners.iH.y > 0.0 and block.block_corners.oH.y > 0.0 and block.block_corners.iLA.y > 0.0 and block.block_corners.oLA.y > 0.0):  # ?
                                inner, outer = arcCenter(bore, block.block_corners.iH, block.block_corners.oH
                                                         , block.block_corners.iLA, block.block_corners.oLA,
                                                         diff_radius=None)
                            else:
                                inner, outer = arcCenter(bore, block.block_corners.iLA, block.block_corners.oLA,
                                                         block.block_corners.iH,
                                                         block.block_corners.oH, diff_radius=None)
                            arg = [self.g.Point.ofCartesian(block.block_corners.iH.x, block.block_corners.iH.y),
                                   self.g.Point.ofCartesian(block.block_corners.iLA.x, block.block_corners.iLA.y),
                                   self.g.Point.ofCartesian(block.block_corners.oLA.x, block.block_corners.oLA.y),
                                   self.g.Point.ofCartesian(block.block_corners.oH.x, block.block_corners.oH.y)]
                            kp0_inner = self.g.Point.ofCartesian(inner[0], inner[1])
                            kp0_outer = self.g.Point.ofCartesian(outer[0], outer[1])
                            areas += (self.g.Area.ofHyperLines(
                                self.a.create_hyper_line_array(self.g.gateway,
                                                               (self.g.Arc.ofEndPointsCenter(arg[1], arg[0], kp0_inner),
                                                                self.g.Line.ofEndPoints(arg[1], arg[3]),
                                                                self.g.Arc.ofEndPointsCenter(arg[2], arg[3], kp0_outer),
                                                                self.g.Line.ofEndPoints(arg[0], arg[2])))),)
                        # self.coil_areas += [areas[0], areas[1]]
                        windings += (self.g.Winding.ofAreas(self.a.create_area_array(self.g.gateway, areas),
                                                            self.a.create_int_array(self.g.gateway, currents),
                                                            winding.conductors_number, winding.conductors_number,
                                                            self.g.cable),)  # Parse block_index and halfturn index

                poles += (self.g.Pole.ofWindings(self.a.create_winding_array(self.g.gateway, windings)),)

        self.coil = self.g.Coil.ofPoles(self.a.create_pole_array(self.g.gateway, poles))

    def cable_domain(self, conductor: str = None):
        """
        Function sets cable characteristics and conductor properties.
        :return: None
        """
        self.g.cable = self.g.Cable()
        self.g.cable.setLabel(conductor)
        self.g.cable.setTop(self.model_data.general_parameters.T_initial)
        i = 0
        # while conductor != self.input_conductor_params.Model_Data_GS.conductors[conductor]:
        # i += 1
        for entry in self.input_conductor_params.Model_Data_GS.conductors[conductor]:
            if entry[0] == 'cable' or entry[0] == 'strand' or entry[0] == 'Jc_fit':
                for key in entry[1]:
                    self.cableParameters[entry[0]][key[0]] = key[1] if key[1] else 0.
        self.g.cable.setwInsulNarrow(self.cableParameters['cable']['th_insulation_along_height'])
        self.g.cable.setwInsulWide(self.cableParameters['cable']['th_insulation_along_width'])
        self.g.cable.setRc(self.cableParameters['cable']['Rc'])
        self.g.cable.setRa(self.cableParameters['cable']['Ra'])
        self.g.cable.setwBare(self.cableParameters['cable']['bare_cable_width'])
        self.g.cable.sethInBare(self.cableParameters['cable']['bare_cable_height_low'])
        self.g.cable.sethOutBare(self.cableParameters['cable']['bare_cable_height_high'])
        self.g.cable.setNoOfStrands(self.cableParameters['cable']['n_strands'])
        self.g.cable.setNoOfStrandsPerLayer(self.cableParameters['cable']['n_strands_per_layers'])
        self.g.cable.setNoOfLayers(self.cableParameters['cable']['n_strand_layers'])
        self.g.cable.setlTpStrand(self.cableParameters['cable']['strand_twist_pitch'])
        self.g.cable.setwCore(self.cableParameters['cable']['width_core'])
        self.g.cable.sethCore(self.cableParameters['cable']['height_core'])
        self.g.cable.setThetaTpStrand(self.cableParameters['cable']['strand_twist_pitch_angle'])
        self.g.cable.setFracFillInnerVoids(self.cableParameters['cable']['f_inner_voids'])
        self.g.cable.setFractFillOuterVoids(self.cableParameters['cable']['f_outer_voids'])

        self.g.cable.setdFilament(self.cableParameters['strand']['filament_diameter'])
        self.g.cable.setDstrand(self.cableParameters['strand']['diameter'])
        self.g.cable.setfRhoEff(self.cableParameters['strand']['f_Rho_effective'])
        self.g.cable.setlTp(self.cableParameters['strand']['fil_twist_pitch'])
        self.g.cable.setRRR(self.cableParameters['strand']['RRR'])
        self.g.cable.setTupRRR(self.cableParameters['strand']['T_ref_RRR_high'])
        self.g.cable.setFracHe(0.)
        self.g.cable.setFracCu(self.cableParameters['strand']['Cu_noCu_in_strand'] /
                               (1 + self.cableParameters['strand']['Cu_noCu_in_strand']))
        self.g.cable.setFracSc(1 / (1 + self.cableParameters['strand']['Cu_noCu_in_strand']))
        if self.cableParameters['Jc_fit']['type'][:4] == 'CUDI':
            self.g.cable.setC1(self.cableParameters['Jc_fit']['C1_' + self.cableParameters['Jc_fit']['type']])
            self.g.cable.setC2(self.cableParameters['Jc_fit']['C2_' + self.cableParameters['Jc_fit']['type']])
        else:
            self.g.cable.setC1(0.)
            self.g.cable.setC2(0.)

        self.g.cable.setCriticalSurfaceFit(self.g.Cable.CriticalSurfaceFitEnum.Ic_NbTi_GSI)
        self.g.cable.setInsulationMaterial(self.g.MatDatabase.MAT_KAPTON)
        self.g.cable.setMaterialInnerVoids(self.g.MatDatabase.MAT_VOID)
        self.g.cable.setMaterialOuterVoids(self.g.MatDatabase.MAT_VOID)
        self.g.cable.setMaterialCore(self.g.MatDatabase.MAT_VOID)
        self.g.cable.setResitivityCopperFit(self.g.Cable.ResitivityCopperFitEnum.rho_Cu_CUDI)

    def wedge_domain(self):
        """
        Function creates inter-block wedges domain
        :return: None
        """
        wedges = self.roxie_data.wedges

        elements = []
        for i in wedges:
            kp0_inner = self.g.Point.ofCartesian(wedges[i].corrected_center.inner.x, wedges[i].corrected_center.inner.y)
            kp0_outer = self.g.Point.ofCartesian(wedges[i].corrected_center.outer.x, wedges[i].corrected_center.outer.y)
            arg = [self.g.Point.ofCartesian(wedges[i].corners.iH.x, wedges[i].corners.iH.y),
                   self.g.Point.ofCartesian(wedges[i].corners.iLA.x, wedges[i].corners.iLA.y),
                   self.g.Point.ofCartesian(wedges[i].corners.oH.x, wedges[i].corners.oH.y),
                   self.g.Point.ofCartesian(wedges[i].corners.oLA.x, wedges[i].corners.oLA.y)]

            area = self.g.Area.ofHyperLines(self.a.create_hyper_line_array(
                self.g.gateway, (self.g.Arc.ofEndPointsCenter(arg[0], arg[1], kp0_inner),
                                 self.g.Line.ofEndPoints(arg[1], arg[3]),
                                 self.g.Arc.ofEndPointsCenter(arg[3], arg[2], kp0_outer),
                                 self.g.Line.ofEndPoints(arg[0], arg[2]))))
            self.wedge_areas += [area]

            elements.append(self.g.Element(f"Wedge_El{i}", area))

        self.wedge_elements = self.a.create_element_array(self.g.gateway, tuple(elements))

    def mirrorXY(self, area):
        """
        This function mirrors a SIGMA area object in x, y and xy. Returns all possible mirroring options.
        :param area:
        :return: area, ar2, ar2.mirrorX(), area.mirrorX()
        """
        ar2 = area.mirrorY()
        return area, ar2, ar2.mirrorX(), area.mirrorX()

    def air_ff_domain(self):
        """
        Function creates air far field domain
        :return: None
        """

        iron = self.roxie_data.iron

        kpc = self.g.Point.ofCartesian(0.0, 0.0)
        for i in iron.key_points:
            max_i = max(iron.key_points[i].x, iron.key_points[i].y)
            if max_i > self.max_r:
                self.max_r = max_i

        kp1 = self.g.Point.ofCartesian(self.max_r * 2 * 0.95, 0.0)
        kp2 = self.g.Point.ofCartesian(0.0, self.max_r * 2 * 0.95)
        kp1_out = self.g.Point.ofCartesian(self.max_r * 2, 0.0)
        kp2_out = self.g.Point.ofCartesian(0.0, self.max_r * 2)
        ln1 = self.g.Line.ofEndPoints(kpc, kp1_out)
        ln2 = self.g.Arc.ofEndPointsCenter(kp1_out, kp2_out, kpc)
        ln3 = self.g.Line.ofEndPoints(kp2_out, kp2)
        ln4 = self.g.Arc.ofEndPointsCenter(kp2, kp1, kpc)

        hyper_areas = self.mirrorXY(self.g.Area.ofHyperLines(
            self.a.create_hyper_line_array(self.g.gateway, tuple([ln1, ln2, ln3, ln4]))))

        arg = []  # elements
        for i, ar in enumerate(hyper_areas):
            arg.append(self.g.Element(f"AFF_El{i}", ar))

        self.air_far_field = self.a.create_element_array(self.g.gateway, tuple(arg))

    def air_domain(self):
        """
        Function creates air domain
        :return: None
        """
        kpc = self.g.Point.ofCartesian(0.0, 0.0)

        self.air = self.a.create_element_array(self.g.gateway, self.g.Element('Air', self.g.Area.ofHyperLines(
            self.a.create_hyper_line_array(self.g.gateway,
                                           self.g.Circumference.ofCenterRadius(kpc, self.max_r * 2 * 0.95)))))

    def iron_yoke_domain(self):
        """
        Function creates iron yoke domain
        :return: None
        """
        iron = self.roxie_data.iron

        keyPointsCOMSOL = {}
        hyperLinesCOMSOL = {}
        hyperAreasCOMSOL = {}

        for i in iron.key_points:
            keyPointsCOMSOL[i] = self.g.Point.ofCartesian(iron.key_points[i].x, iron.key_points[i].y)

        for i in iron.hyper_lines:
            if iron.hyper_lines[i].type == 'line':
                hyperLinesCOMSOL[i] = self.g.Line.ofEndPoints(keyPointsCOMSOL[iron.hyper_lines[i].kp1],
                                                              keyPointsCOMSOL[iron.hyper_lines[i].kp2])

            elif iron.hyper_lines[i].type == 'arc':
                hyperLinesCOMSOL[i] = self.g.Arc.ofThreePoints(keyPointsCOMSOL[iron.hyper_lines[i].kp1],
                                                               keyPointsCOMSOL[iron.hyper_lines[i].kp3],
                                                               keyPointsCOMSOL[iron.hyper_lines[i].kp2])

            elif iron.hyper_lines[i].type == 'ellipticArc':
                hyperLinesCOMSOL[i] = self.g.EllipticArc.ofEndPointsAxes(keyPointsCOMSOL[iron.hyper_lines[i].kp1],
                                                                         keyPointsCOMSOL[iron.hyper_lines[i].kp2],
                                                                         iron.hyper_lines[i].arg1,
                                                                         iron.hyper_lines[i].arg2)

            elif iron.hyper_lines[i].type == 'circle':
                hyperLinesCOMSOL[i] = self.g.Circumference.ofDiameterEndPoints(keyPointsCOMSOL[iron.hyper_lines[i].kp1],
                                                                               keyPointsCOMSOL[iron.hyper_lines[i].kp2])
            else:
                raise ValueError('Hyper line {} not supported'.format(iron.hyper_lines[i].type))

        for i in iron.hyper_areas:
            arg = [hyperLinesCOMSOL[j] for j in iron.hyper_areas[i].lines]  # lines for areas
            hyperAreasCOMSOL[i] = self.mirrorXY(self.g.Area.ofHyperLines(
                self.a.create_hyper_line_array(self.g.gateway, tuple(arg))))

        for i in hyperAreasCOMSOL:
            arg = []  # elements
            for j, ar in enumerate(hyperAreasCOMSOL[i]):
                arg.append(self.g.Element(f"IY{iron.hyper_areas[i].material[2:]}_{i}_El{j}", ar))

            self.elements[i] = self.a.create_element_array(self.g.gateway, tuple(arg))

    def get_all_domains(self):
        """
        This function saves a Java file to be used in COMSOL simulation software.

        :return: None
        """
        domains = [self.g.AirFarFieldDomain("AFF", self.g.MatDatabase.MAT_AIR, self.air_far_field)]
        domains += [self.g.AirDomain("AIR", self.g.MatDatabase.MAT_AIR, self.air)]

        orderedElements = list(self.elements)
        # change order of generated domains to override correctly

        for hyper_hole_key, hyper_hole in self.roxie_data.iron.hyper_holes.items():
            index = [orderedElements.index(hyper_hole.areas[0]),
                     orderedElements.index(hyper_hole.areas[1])]
            if index[0] < index[1]:
                orderedElements.insert(index[1], orderedElements.pop(index[0]))

        # MAT_AIR, MAT_COIL, MAT_COPPER, MAT_KAPTON, MAT_GLASSFIBER, MAT_INSULATION_TEST, MAT_STEEL, MAT_IRON1,
        # MAT_IRON2, MAT_VOID, MAT_NULL, MAT_COIL_TEST, MAT_G10
        self.iron_yoke = [
            self.g.IronDomain(self.cfg, i, str(self.bh_curve_database),
                              self.roxie_data.iron.hyper_areas[i].material, self.elements[i])
            for i in orderedElements]  # domains
        #print(self.iron_yoke)
        domains += self.iron_yoke
        domains.append(self.g.CoilDomain("CO", self.g.MatDatabase.MAT_COIL, self.coil))
        domains.append(self.g.WedgeDomain("W", self.g.MatDatabase.MAT_COPPER, self.wedge_elements))
        return domains
