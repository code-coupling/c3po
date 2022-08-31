# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import pytest

import c3po
from tests.plaques_coupling.PlaquePhysicsDriver import PlaquePhysicsDriver

taille = 1
nbrNoeuds = 20
# Température de référence pour nbrNoeuds = 20 et calculé avec un FixedPointCoupler et une précision de 1E-15
temperature_ref = np.array([[17.10868064, 12.66076104, 10.98374883, 10.32288016, 10.07162101,
         9.99653718,  9.99924414, 10.03554411, 10.08502992, 10.13855277,
        10.19266059, 10.24703125, 10.30333874, 10.36492977, 10.43713292,
        10.52836579, 10.65275892, 10.83645523, 11.13429396, 11.6796121 ,
        12.85105241, 11.66684347, 11.10795252, 10.79490133, 10.59344239,
        10.44770449, 10.33034255, 10.2258024 , 10.12396821, 10.01748632,
         9.90061443,  9.76889531,  9.61953576,  9.45278739,  9.27528196,
         9.10785625,  9.00491078,  9.10654209,  9.79332188, 12.19328646],
       [24.48652925, 21.25718412, 19.65680959, 18.94128636, 18.67209566,
        18.62028217, 18.66989499, 18.76291667, 18.87105723, 18.98157716,
        19.09013768, 19.19722819, 19.30652093, 19.42440155, 19.56042279,
        19.72880002, 19.95150247, 20.264147  , 20.72664544, 21.43896287,
        22.54193769, 21.4142217 , 20.67558769, 20.18356834, 19.8364231 ,
        19.57222448, 19.35300214, 19.15399226, 18.95763463, 18.75036966,
        18.52103691, 18.26034177, 17.96131661, 17.62113028, 17.24522432,
        16.85592039, 16.50990233, 16.3326234 , 16.57837882, 17.68603444],
       [28.32020306, 26.94905506, 26.16394879, 25.83023179, 25.77134858,
        25.85862199, 26.01328671, 26.19156405, 26.3713871 , 26.5435426 ,
        26.70636593, 26.86280461, 27.01900886, 27.18396882, 27.3699957 ,
        27.5940587 , 27.88014929, 28.26284703, 28.79163301, 29.53278216,
        30.55811867, 29.49754649, 28.7188821 , 28.14795679, 27.71594013,
        27.37044262, 27.07347718, 26.79698962, 26.51912464, 26.22168139,
        25.88858864, 25.50523649, 25.05866628, 24.53883409, 23.94140921,
        23.27277117, 22.55758456, 21.84678618, 21.21308941, 20.6862566 ],
       [30.61355378, 30.81162841, 30.97055988, 31.19285912, 31.47255604,
        31.77828224, 32.08285691, 32.36972504, 32.6317496 , 32.86848063,
        33.08384854, 33.2846876 , 33.48003501, 33.68107656, 33.90165009,
        34.15926766, 34.47660892, 34.88326512, 35.41697457, 36.12248478,
        37.04523545, 36.0786718 , 35.32646267, 34.74021171, 34.27194703,
        33.88024994, 33.53119931, 33.19692811, 32.85365095, 32.47991877,
        32.05531914, 31.55966651, 30.97270838, 30.27438959, 29.44566205,
        28.46950596, 27.33077084, 26.01062715, 24.46518559, 22.56821423],
       [32.1142161 , 33.50747268, 34.50980499, 35.29676059, 35.94984758,
        36.50507556, 36.98008151, 37.38651791, 37.73479214, 38.03549458,
        38.29966201, 38.53879992, 38.76501155, 38.99134204, 39.2323545 ,
        39.50490813, 39.82903929, 40.22870043, 40.73185781, 41.36920611,
        42.17113523, 41.3188772 , 40.62782525, 40.06413684, 39.59334695,
        39.18317165, 38.80455637, 38.4313209 , 38.03913458, 37.60431451,
        37.1026872 , 36.50860612, 35.79413848, 34.92835814, 33.87652049,
        32.59851289, 31.04516226, 29.14953836, 26.80863724, 23.85135583],
       [33.14620062, 35.42429814, 37.11025743, 38.3937477 , 39.39602573,
        40.19367867, 40.83688849, 41.36084395, 41.79215973, 42.15233729,
        42.45967404, 42.73043203, 42.97968782, 43.22206428, 43.47242453,
        43.7465301 , 44.06159106, 44.43654466, 44.89180617, 45.44823945,
        46.12541157, 45.39334666, 44.77827897, 44.25680933, 43.80387962,
        43.3942544 , 43.00327504, 42.6068075 , 42.18062587, 41.699481  ,
        41.13601436, 40.45958875, 39.63503382, 38.6212216 , 37.36925174,
        35.81978811, 33.8987184 , 31.50992505, 28.52412259, 24.7649351 ],
       [33.87099596, 36.79473443, 39.00683895, 40.69323818, 41.99171393,
        43.00171919, 43.79505598, 44.42446577, 44.92972132, 45.3417296 ,
        45.68528222, 45.9809537 , 46.24647799, 46.49779999, 46.74990318,
        47.01744398, 47.31516284, 47.65798805, 48.06071581, 48.5371805 ,
        49.0989636 , 48.47940795, 47.94117494, 47.46857881, 47.04327943,
        46.64528327, 46.25346616, 45.84555415, 45.3976375 , 44.88332803,
        44.272645  , 43.53067048, 42.61597044, 41.4787294 , 40.05848708,
        38.28129299, 36.05604658, 33.26990099, 29.78319161, 25.42587593],
       [34.37866576, 37.76409631, 40.36463219, 42.35886574, 43.89079672,
        45.07236295, 45.98902554, 46.70572513, 47.27203702, 47.72623871,
        48.09838899, 48.41262706, 48.68888994, 48.94419855, 49.19360861,
        49.45087274, 49.72881707, 50.0394019 , 50.39342109, 50.79980978,
        51.2645699 , 50.74051554, 50.27067816, 49.84477228, 49.44914398,
        49.06753603, 48.68144818, 48.27006801, 47.80979158, 47.27337496,
        46.62875343, 45.83754965, 44.85327757, 43.61924532, 42.06617476,
        40.10960673, 37.64728395, 34.55696045, 30.69555068, 25.90117001],
       [34.7232578 , 38.42573668, 41.29819076, 43.51273762, 45.21534675,
        46.52461686, 47.53427655, 48.31723359, 48.92982698, 49.4156337 ,
        49.80861539, 50.13560723, 50.41823437, 50.67435425, 50.91910535,
        51.16561394, 51.42538157, 51.70835383, 52.02266131, 52.37402795,
        52.76485154, 52.31426261, 51.89889411, 51.51196285, 51.14289721,
        50.77793357, 50.40035725, 49.99036789, 49.52456313, 48.97504735,
        48.30817637, 47.48295123, 46.44908544, 45.14480292, 43.49449523,
        41.40649272, 38.77140108, 35.46171359, 31.33365791, 26.23226016],
       [34.93800112, 38.83941806, 41.8845434 , 44.24102782, 46.05520422,
        47.44900452, 48.5207676 , 49.34812042, 49.99158848, 50.49814366,
        50.9043172 , 51.23876011, 51.52426164, 51.77928473, 52.0190826 ,
        52.25644665, 52.5021164 , 52.7648665 , 53.05127937, 53.36521533,
        53.70699924, 53.30578687, 52.92816444, 52.56938465, 52.22068266,
        51.86975768, 51.50093895, 51.0950017 , 50.62861076, 50.07338168,
        49.39455964, 48.54932942, 47.48479823, 46.13575178, 44.42239031,
        42.24841807, 39.50008155, 36.04697387, 31.74549998, 26.44556523],
       [35.04233065, 39.04094841, 42.17129906, 44.59871605, 46.46933659,
        47.90631322, 49.00992522, 49.85992995, 50.51884238, 51.03531714,
        51.44720704, 51.7841324 , 52.06953687, 52.32226711, 52.55772911,
        52.78866569, 53.02558481, 53.27685501, 53.54848058, 53.84357758,
        54.16158879, 53.78513733, 53.42737105, 53.08444409, 52.74834384,
        52.40733938, 52.04613346, 51.64566424, 51.18252479, 50.62798615,
        49.94662449, 49.0945711 , 48.01744131, 46.64807012, 44.90430669,
        42.68730478, 39.88097321, 36.35344031, 31.9613643 , 26.55741232],
       [35.04516286, 39.04706309, 42.18126562, 44.6128309 , 46.4874134 ,
        47.92769586, 49.03363743, 49.88485765, 50.54388267, 51.05947146,
        51.46962444, 51.80412151, 52.08656673, 52.33597387, 52.56793941,
        52.79544023, 53.02927493, 53.27815284, 53.54843145, 53.84352159,
        54.16301754, 53.78665551, 53.43054623, 53.09076567, 52.75907741,
        52.42346482, 52.068351  , 51.67443242, 51.21809505, 50.67040947,
        49.99571655, 49.14983265, 48.07793937, 46.71229678, 44.97004712,
        42.75156465, 39.94003266, 36.4031053 , 31.99745672, 26.576464  ],
       [34.94609623, 38.8573383 , 41.91444573, 44.28405982, 46.11081673,
        47.51506972, 48.5941357 , 49.42524327, 50.06900028, 50.57274278,
        50.97348263, 51.30036934, 51.57667724, 51.82136398, 52.05024592,
        52.27681762, 52.51271473, 52.76779315, 53.04978884, 53.36355227,
        53.7099334 , 53.30886835, 52.93639426, 52.58746214, 52.2525338 ,
        51.91836262, 51.56838679, 51.18264126, 50.73718028, 50.20304083,
        49.54478545, 48.71866714, 47.67048454, 46.33325979, 44.62499217,
        42.44692139, 39.68295577, 36.20110331, 31.85771754, 26.50487413],
       [34.73502394, 38.45372577, 41.34776111, 43.58672858, 45.31279979,
        46.64134333, 47.66420864, 48.45373335, 49.06658955, 49.5471497 ,
        49.93030815, 50.24379513, 50.51005065, 50.7477251 , 50.97285434,
        51.19972507, 51.44140083, 51.70982681, 52.01539574, 52.36588694,
        52.76485681, 52.3140931 , 51.90796747, 51.5389213 , 51.19470173,
        50.85964593, 50.51537913, 50.14082886, 49.71162618, 49.19900218,
        48.56826548, 47.77692021, 46.77248618, 45.49012822, 43.85030376,
        41.7568001 , 39.09574539, 35.73638086, 31.53444108, 26.33866679],
       [34.38984326, 37.79743185, 40.43243036, 42.4672187 , 44.03789399,
        45.25053818, 46.18776461, 46.91409165, 47.48009506, 47.92562156,
        48.28232782, 48.57573156, 48.82690056, 49.05386471, 49.27280214,
        49.49900753, 49.74758351, 50.03369497, 50.37210827, 50.77570142,
        51.25290931, 50.72766766, 50.27246036, 49.87512579, 49.51861627,
        49.18324378, 48.84782505, 48.48974012, 48.08419895, 47.60297851,
        47.01278387, 46.2733039 , 45.33499974, 44.13668483, 42.60302942,
        40.64225454, 38.14446911, 34.98132927, 31.00788643, 26.06747742],
       [33.87078605, 36.8218309 , 39.08856081, 40.84107037, 42.20112174,
        43.25842194, 44.08132096, 44.72318375, 45.22629111, 45.62447263,
        45.94509153, 46.21067476, 46.44033249, 46.65105018, 46.85890767,
        47.08024374, 47.33270514, 47.63594773, 48.01145508, 48.48059817,
        49.06024422, 48.43739324, 47.92181528, 47.49328488, 47.12666996,
        46.79603985, 46.47628928, 46.14294758, 45.77102711, 45.33342437,
        44.7990868 , 44.13099351, 43.28393434, 42.2020706 , 40.81630365,
        39.0415615 , 36.77424988, 33.89032326, 30.24474405, 25.67353032],
       [33.10708373, 35.41837706, 37.19636421, 38.58960028, 39.6882735 ,
        40.5548799 , 41.23750172, 41.77509654, 42.19978624, 42.53818906,
        42.81250249, 43.04154809, 43.24184188, 43.42873292, 43.6176696 ,
        43.82566373, 44.07297806, 44.3848551 , 44.79251467, 45.33141512,
        46.03347202, 45.29430235, 44.71551404, 44.26230708, 43.89598876,
        43.58150914, 43.28892429, 42.99207098, 42.66643456, 42.28695662,
        41.82593356, 41.25094201, 40.52267335, 39.59256096, 38.4000989 ,
        36.86976974, 34.9075295 , 32.39688744, 29.19491197, 25.12934506],
       [31.96331071, 33.40959676, 34.58434515, 35.55845199, 36.35960469,
        37.00982568, 37.53189025, 37.94847234, 38.28070094, 38.54742302,
        38.7651373 , 38.9483766 , 39.11039051, 39.26409031, 39.42332511,
        39.60466808, 39.82999069, 40.130076  , 40.5488852 , 41.14535231,
        41.98180156, 41.11572562, 40.48742236, 40.03226822, 39.68874697,
        39.40983592, 39.16098948, 38.91560551, 38.65107811, 38.34579515,
        37.97679191, 37.51772554, 36.93690109, 36.19512883, 35.2431962 ,
        34.01868044, 32.44169383, 30.40894229, 27.78532018, 24.39281515],
       [30.1449399 , 30.50094463, 31.02002765, 31.56412946, 32.06064149,
        32.48454313, 32.83418872, 33.11758656, 33.3458654 , 33.53045578,
        33.68206862, 33.81055212, 33.9252278 , 34.03558695, 34.15242577,
        34.28972135, 34.46791604, 34.71991924, 35.10194115, 35.70991195,
        36.68249662, 35.68915621, 35.0588895 , 34.65142354, 34.36901941,
        34.15332099, 33.9687799 , 33.79163159, 33.60365268, 33.38856157,
        33.12971805, 32.80839525, 32.40221754, 31.88348994, 31.21715363,
        30.3579895 , 29.24639105, 27.80137543, 25.90821342, 23.39599897],
       [26.90208099, 26.21976142, 26.22728236, 26.42065692, 26.6439434 ,
        26.84887095, 27.02296144, 27.16611121, 27.28236088, 27.37686921,
        27.45483417, 27.52121544, 27.58084356, 27.63879788, 27.70111582,
        27.77612252, 27.87717615, 28.02906022, 28.28486666, 28.77647065,
        29.88367652, 28.76574832, 28.26263091, 27.99369017, 27.82611644,
        27.70570912, 27.606321  , 27.51287598, 27.41484994, 27.30335743,
        27.16959127, 27.00378157, 26.79431364, 26.52679857, 26.182906  ,
        25.73866892, 25.16166804, 24.40569495, 23.3992148 , 22.01692899]])

class Mat1Mat2Coupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()

def couplage_plaque(coupler_type = 'FixedPoint'):

    myPhysics1 = PlaquePhysicsDriver(taille, taille, nbrNoeuds, nbrNoeuds, mat_type = 'gauche',Tdroite=20., Tgauche=30., Thaut=20., Tbas=0., Text=60., Tinitiale=10., coeffThermique = 1.)
    myPhysics1.initialize()
    myPhysics1.setInputDoubleValue('PRECISION_CIBLE', 1E-12)
    myPhysics1.setInputDoubleValue('PRECISION', 1E-12)

    myPhysics2 = PlaquePhysicsDriver(taille, taille, nbrNoeuds, nbrNoeuds, mat_type = 'droit',Tdroite=20., Tgauche=30., Thaut=20., Tbas=0., Text=60., Tinitiale=-10., coeffThermique=5.)
    myPhysics2.initialize()
    myPhysics2.setInputDoubleValue('PRECISION_CIBLE', 1E-12)
    myPhysics2.setInputDoubleValue('PRECISION', 1E-12)

    Ph1toPhy2Transformer = c3po.DirectMatching()
    Ph2toDataTransformer = c3po.DirectMatching()
    DatatoPh1Transformer = c3po.DirectMatching()

    DataCoupler = c3po.LocalDataManager()

    Ph1toPhy2 = c3po.LocalExchanger(Ph1toPhy2Transformer, [], [], [(myPhysics1, str(i)) for i in range(nbrNoeuds)], [(myPhysics2, str(i)) for i in range(nbrNoeuds)])
    Ph2toData = c3po.LocalExchanger(Ph2toDataTransformer, [], [], [(myPhysics2, str(i)) for i in range(nbrNoeuds)], [(DataCoupler, str(i)) for i in range(nbrNoeuds)])
    DatatoPh1 = c3po.LocalExchanger(DatatoPh1Transformer, [], [], [(DataCoupler, str(i)) for i in range(nbrNoeuds)], [(myPhysics1, str(i)) for i in range(nbrNoeuds)])

    Mat1Mat2Run = Mat1Mat2Coupler([myPhysics1,myPhysics2], [Ph1toPhy2])

    if coupler_type == "FixedPoint" :
        CouplerGS = c3po.FixedPointCoupler([Mat1Mat2Run], [Ph2toData, DatatoPh1], [DataCoupler])
        CouplerGS.setDampingFactor(1)
        CouplerGS.setNormChoice(c3po.NormChoice.norm2)
        CouplerGS.setConvergenceParameters(1E-12, 1000)
        CouplerGS.init()
        # Initialisation frontiere domaine
        Ph2toData.exchange()
        DatatoPh1.exchange()
        CouplerGS.solve()
        CouplerGS.term()
    elif coupler_type == 'CrossedSecant' :
        CouplerCS = c3po.CrossedSecantCoupler([Mat1Mat2Run], [Ph2toData, DatatoPh1], [DataCoupler])
        CouplerCS.setNormChoice(c3po.NormChoice.norm2)
        CouplerCS.setConvergenceParameters(1E-12, 1000)
        CouplerCS.init()
        # Initialisation frontiere domaine
        Ph2toData.exchange()
        DatatoPh1.exchange()
        CouplerCS.solve()
        CouplerCS.term()
    elif coupler_type == 'Anderson' :
        CouplerAnderson = c3po.AndersonCoupler([Mat1Mat2Run], [Ph2toData, DatatoPh1], [DataCoupler])
        CouplerAnderson.setOrder(3)
        CouplerAnderson.setConvergenceParameters(1E-12, 100)
        CouplerAnderson.init()
        # Initialisation frontiere domaine
        Ph2toData.exchange()
        DatatoPh1.exchange()
        CouplerAnderson.solve()
        CouplerAnderson.term()
    elif coupler_type == 'JFNK' :
        CouplerJFNK = c3po.JFNKCoupler([Mat1Mat2Run], [Ph2toData, DatatoPh1], [DataCoupler])
        CouplerJFNK.setKrylovConvergenceParameters(1E-4, 3)
        CouplerJFNK.setConvergenceParameters(1E-12, 100)
        CouplerJFNK.init()
        # Initialisation frontiere domaine
        Ph2toData.exchange()
        DatatoPh1.exchange()
        CouplerJFNK.solve()
        CouplerJFNK.term()
    elif coupler_type == 'AdaptiveResidualBalance' or coupler_type == 'DynamicResidualBalance' :
        # For Residual Balance
        DataCouplerResiduals = c3po.LocalDataManager()
        datatoCouplerTransformer_1 = c3po.DirectMatching()
        datatoCouplerTransformer_2 = c3po.DirectMatching()

        exch_Residual1 = c3po.LocalExchanger( datatoCouplerTransformer_1, [], [], valuesToGet=[(myPhysics1, 'PRECISION_ATTEINTE')], valuesToSet=[(DataCouplerResiduals,'Residual1')] )
        exch_Residual2 = c3po.LocalExchanger( datatoCouplerTransformer_2, [], [], valuesToGet=[(myPhysics2, 'PRECISION_ATTEINTE')], valuesToSet=[(DataCouplerResiduals,'Residual2')] )

        if coupler_type == 'AdaptiveResidualBalance':
            CouplerResidualBalance = c3po.AdaptiveResidualBalanceCoupler(
                {"Solver1" : myPhysics1, "Solver2" : myPhysics2},
                {"1to2" : Ph1toPhy2,
                "2to1" : c3po.LocalExchanger(c3po.DirectMatching(),[],[]), #Cet echangeur est inutile si on passe par un FixedPointCoupler pour faire les iterations.
                    "Residual1" : exch_Residual1,
                    "Residual2" : exch_Residual2},
                [DataCouplerResiduals])
        else :
            CouplerResidualBalance = c3po.DynamicResidualBalanceCoupler(
                {"Solver1" : myPhysics1, "Solver2" : myPhysics2},
                {"1to2" : Ph1toPhy2,
                "2to1" : c3po.LocalExchanger(c3po.DirectMatching(),[],[]), #Cet echangeur est inutile si on passe par un FixedPointCoupler pour faire les iterations.
                    "Residual1" : exch_Residual1,
                    "Residual2" : exch_Residual2},
                [DataCouplerResiduals])
        CouplerResidualBalance.init()
        CouplerResidualBalance.setNormChoice(c3po.NormChoice.norm2)
        if coupler_type == 'AdaptiveResidualBalance': CouplerResidualBalance.setConvRateInit(0.1,0.1)
        CouplerResidualBalance.setConvergenceParameters(1E-12,1E-12,100)

        # On utilise un FixedPointCoupler pour verifier les erreurs multi-physiques.
        myFixedPointCoupler = c3po.FixedPointCoupler([CouplerResidualBalance], [Ph2toData, DatatoPh1], [DataCoupler])

        myFixedPointCoupler.init()
        myFixedPointCoupler.setUseIterate(True)
        myFixedPointCoupler.setConvergenceParameters(1E-12, 100)
        myFixedPointCoupler.setNormChoice(c3po.NormChoice.norm2)
        myFixedPointCoupler.setStationaryMode(True)
        myFixedPointCoupler.initTimeStep(0.)

        # Initialisation frontiere domaine
        Ph2toData.exchange()
        DatatoPh1.exchange()

        # Calculs des etats initiaux perturbés
        myPhysics1.iterate() # Implique le calcul d'une itération/d'un pas de temps
        Ph1toPhy2.exchange()
        myPhysics2.iterate() # Implique le calcul d'une itération/d'un pas de temps
        Ph2toData.exchange()
        DatatoPh1.exchange()

        # Lancement du calcul : on lance le point fixe qui appelle le solve du Adaptive Residual Balance
        myFixedPointCoupler.solve()

    # Récupération de la nappe de température des deux plaques
    temperature = np.zeros((nbrNoeuds,nbrNoeuds+nbrNoeuds))
    for i in range(nbrNoeuds):
        for j in range(nbrNoeuds):
            temperature[j,i]=myPhysics1.temperature_[j+i*nbrNoeuds]
            temperature[j,nbrNoeuds+i]=myPhysics2.temperature_[j+i*nbrNoeuds]

    # Vérification de la nappe de température obtenue
    try:
        for i in range(nbrNoeuds):
            for j in range(nbrNoeuds):
                pytest.approx(temperature[i][j], abs=1.E-3) == temperature_ref[i][j]

        print("Test for coupler {} passed".format(coupler_type))
    except:
        raise

def test_run_all():
    couplage_plaque(coupler_type = 'FixedPoint')
    couplage_plaque(coupler_type = 'Anderson')
    couplage_plaque(coupler_type = 'CrossedSecant')
    couplage_plaque(coupler_type = 'JFNK')
    couplage_plaque(coupler_type = 'AdaptiveResidualBalance')
    couplage_plaque(coupler_type = 'DynamicResidualBalance')

if __name__ == "__main__":
    test_run_all()