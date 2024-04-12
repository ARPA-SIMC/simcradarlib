from simcradarlib.io_utils.structure_class import StructVariable
import numpy as np

"""
Sostituisce la tabella /autofs/radar/radar/file_x_idl/tabelle/variabili.txt
e contiene classi figlie di StructVariable, implementata in
simcradarlib.io_utils.structure_class che implementano le variabili radar.
(Per ora non sono implementate Z_50, Z_70 )
"""


class VarPr(StructVariable):
    def __init__(self):
        super().__init__(
            name="pr",
            long_name="Radar precipitation flux",
            standard_name="precipitation_flux",
            units="kg m-2 s-1",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table=None,
        )


class VarZ60(StructVariable):
    def __init__(self):
        super().__init__(
            name="Z_60",
            long_name="Radar reflectivity factor",
            standard_name=None,
            units="dBZ",
            min_val=-19.69,
            max_val=60.0,
            missing=np.float32(-20.0),
            undetect=np.float32(-19.69),
            color_table="RGB_Z.txt",
        )


class VarCumPrr(StructVariable):
    def __init__(self):
        super().__init__(
            name="cum_pr",
            long_name="Radar Precipitation amount",
            standard_name="precipitation_amount",
            units="kg m-2",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table=None,
        )


class VarZdr(StructVariable):
    def __init__(self):
        super().__init__(
            name="ZDR",
            long_name="Radar Differential Reflectivity",
            standard_name=None,
            units="dB",
            min_val=-6.0,
            max_val=10.0,
            missing=np.float32(-16.0),
            undetect=np.float32(-16.0),
            color_table="RGB_ZDR.txt",
        )


class VarVn16(StructVariable):
    def __init__(self):
        super().__init__(
            name="VN16",
            long_name="Doppler Radar Velocity",
            standard_name=None,
            units="m s-1",
            min_val=-16.5,
            max_val=16.5,
            missing=np.float32(-16.5),
            undetect=np.float32(-16.5),
            color_table="RGB_V.txt",
        )


class VarVn49(StructVariable):
    def __init__(self):
        super().__init__(
            name="VN49",
            long_name="Doppler Radar Velocity",
            standard_name=None,
            units="m s-1",
            min_val=-49.5,
            max_val=49.5,
            missing=np.float32(-49.5),
            undetect=np.float32(-49.5),
            color_table="RGB_V.txt",
        )


class VarSv(StructVariable):
    def __init__(self):
        super().__init__(
            name="sV",
            long_name="Doppler Radar Velocity Spectrum Width",
            standard_name=None,
            units="m s-1",
            min_val=0.0,
            max_val=10.0,
            missing=np.float32(0.0),
            undetect=np.float32(0.0),
            color_table="RGB_SV.txt",
        )


class VarQc(StructVariable):
    def __init__(self):
        super().__init__(
            name="qc",
            long_name="Quality",
            standard_name="quality",
            units="percent",
            min_val=0.0,
            max_val=1.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table=None,
        )


class VarPrmm(StructVariable):
    def __init__(self):
        super().__init__(
            name="pr_mm",
            long_name="Radar precipitation flux",
            standard_name="precipitation_flux",
            units="mm h-1",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table=None,
        )


class VarCumPrmm(StructVariable):
    def __init__(self):
        super().__init__(
            name="cum_pr_mm",
            long_name="Radar precipitation amount",
            standard_name="precipitation_amount",
            units="mm",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table=None,
        )


class VarZ(StructVariable):
    def __init__(self):
        super().__init__(
            name="Z",
            long_name="Radar reflectivity factor",
            standard_name=None,
            units="dBZ",
            min_val=-64.0,
            max_val=80.0,
            missing=np.float32(-70.0),
            undetect=np.float32(-64.0),
            color_table="RGB_Z.txt",
        )


class VarTh(StructVariable):
    def __init__(self):
        super().__init__(
            name="Z",
            long_name="Uncorrected Radar reflectivity factor",
            standard_name=None,
            units="dBZ",
            min_val=-64.0,
            max_val=80.0,
            missing=np.float32(-70.0),
            undetect=np.float32(-64.0),
            color_table="RGB_Z.txt",
        )


class VarDbzh(StructVariable):
    def __init__(self):
        super().__init__(
            name="DBZH",
            long_name="Radar reflectivity factor",
            standard_name=None,
            units="dBZ",
            min_val=-64.0,
            max_val=80.0,
            missing=np.float32(-70.0),
            undetect=np.float32(-64.0),
            color_table="RGB_Z.txt",
        )


class VarVrad(StructVariable):
    def __init__(self):
        super().__init__(
            name="VRAD",
            long_name="Doppler Radar Velocity",
            standard_name=None,
            units="m s-1",
            min_val=-49.5,
            max_val=49.5,
            missing=np.float32(-49.5),
            undetect=np.float32(-49.5),
            color_table="RGB_V_48_17livelli.txt",
        )


class VarWrad(StructVariable):
    def __init__(self):
        super().__init__(
            name="WRAD",
            long_name="Doppler Radar Velocity Spectrum Width",
            standard_name=None,
            units="m s-1",
            min_val=0.0,
            max_val=10.0,
            missing=np.float32(0.0),
            undetect=np.float32(0.0),
            color_table="RGB_SV.txt",
        )


class VarRhohv(StructVariable):
    def __init__(self):
        super().__init__(
            name="RHOHV",
            long_name="Correlation ZH-ZV",
            standard_name=None,
            units="percent",
            min_val=0.0,
            max_val=1.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table="RGB_RHO.txt",
        )


class VarPhidp(StructVariable):
    def __init__(self):
        super().__init__(
            name="PHIDP",
            long_name="Differential phase",
            standard_name=None,
            units="degree",
            min_val=-180.0,
            max_val=180.0,
            missing=np.float32(-180.0),
            undetect=np.float32(-180.0),
            color_table=None,
        )


class VarHght(StructVariable):
    def __init__(self):
        super().__init__(
            name="HGHT",
            long_name="Height",
            standard_name=None,
            units="km",
            min_val=-6.0,
            max_val=20.0,
            missing=np.float32(-9999.0),
            undetect=np.float32(-9999.0),
            color_table="RGB_GENERAL.txt",
        )


class VarDbzV(StructVariable):
    def __init__(self):
        super().__init__(
            name="DBZV",
            long_name="Radar reflectivity factor",
            standard_name=None,
            units="dBZ",
            min_val=-64.0,
            max_val=80.0,
            missing=np.float32(-70.0),
            undetect=np.float32(-64.0),
            color_table="RGB_Z.txt",
        )


class VarPoh(StructVariable):
    def __init__(self):
        super().__init__(
            name="POH",
            long_name="Probability of Hail",
            standard_name=None,
            units="percent",
            min_val=0.0,
            max_val=1.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table="RGB_GENERAL.txt",
        )


class VarVil(StructVariable):
    def __init__(self):
        super().__init__(
            name="VIL",
            long_name="Vertical integrated liquid Water",
            standard_name=None,
            units="km m-2",
            min_val=0.0,
            max_val=150.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table="RGB_VIL.txt",
        )


class VarClassConv(StructVariable):

    # chiedi units

    def __init__(self):
        super().__init__(
            name="CLASS_CONV",
            long_name="Convective-Stratiform class",
            standard_name=None,
            units="",
            min_val=0.0,
            max_val=1500.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table="RGB_GENERAL.txt",
        )


class VarSnr(StructVariable):

    # undetect è 8dB?

    def __init__(self):
        super().__init__(
            name="SNR",
            long_name="Signal Noise Ratio",
            standard_name=None,
            units="dB",
            min_val=-8.0,
            max_val=8.0,
            missing=np.float32(-8.0),
            undetect=np.float32(8.0),
            color_table="RGB_GENERAL.txt",
        )


class VarClass(StructVariable):

    # missing e undetect ok?

    def __init__(self):
        super().__init__(
            name="CLASS",
            long_name="Hydrometeor Classification",
            standard_name=None,
            units="",
            min_val=0.0,
            max_val=11.0,
            missing=np.float32(12.0),
            undetect=np.float32(9.0),
            color_table="RGB_HYDROCLASS.2.txt",
        )


class VarVilDensity(StructVariable):
    def __init__(self):
        super().__init__(
            name="VILdensity",
            long_name="Hail size",
            standard_name=None,
            units="cm",
            min_val=0.0,
            max_val=10.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table="RGB_VILdensity.txt",
        )


class VarRate(StructVariable):
    def __init__(self):
        super().__init__(
            name="RATE",
            long_name="Rain Rate",
            standard_name="precipitation_flux",
            units="mm h-1",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table="RGB_SRI.txt",
        )


class VarAcrr(StructVariable):
    def __init__(self):
        super().__init__(
            name="ACRR",
            long_name="Accumulated precipitation",
            standard_name="precipitation_amount",
            units="mm",
            min_val=0.0,
            max_val=10000.0,
            missing=np.float32(-1.0),
            undetect=np.float32(0.0),
            color_table="RGB_CUMULATE.txt",
        )


class VarClassId(StructVariable):
    def __init__(self):
        super().__init__(
            name="ClassID",
            long_name="Fuzzy logic class",
            standard_name=None,
            units="",
            min_val=0.0,
            max_val=4.0,
            missing=np.float32(-1.0),
            undetect=np.float32(-1.0),
            color_table=None,
        )
        self.name = ("ClassID",)
        self.long_name = ("Fuzzy logic class",)
        self.standard_name = (None,)
        self.units = ("",)
        self.min_val = (0.0,)
        self.max_val = (4.0,)
        self.missing = (np.float32(-1.0),)
        self.undetect = (np.float32(-1.0),)
        self.color_table = None
