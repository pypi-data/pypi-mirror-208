from __future__ import annotations
from enum import Enum

from pydantic import BaseModel, ValidationError, Field, validator, root_validator, parse_obj_as
from pydantic.fields import Validator
import typing as t
from typing_extensions import Annotated
from numpy import mod


def optional_discriminators(unions: t.List[str]):
    def dec(model: t.Type[BaseModel]):
        for k in unions:
            field = model.__fields__[k]
            discriminator_lookup = {v.type_: k for k, v in field.sub_fields_mapping.items()}

            def handle_missing_discriminator(cls, values):
                if isinstance(values, dict) and field.discriminator_key not in values:
                    parsed = parse_obj_as(t.Union[tuple(f.type_ for f in field.sub_fields)], values)
                    values[field.discriminator_key] = discriminator_lookup[type(parsed)]
                return values

            field.class_validators[f"handle_missing_{field.discriminator_key}"] = Validator(
                handle_missing_discriminator, pre=True
            )
            field.populate_validators()
        return model

    return dec


class SolverConfig(BaseModel):
    initial_time_limit: float = 8.0
    secondary_time_limit: float = 8.0  # not used
    initial_mip_gap_tolerance: float = 0.0
    secondary_mip_gap_tolerance: float = 0.02  # not used
    initial_verbose: bool = False
    secondary_verbose: bool = True  # not used
    hybrid_infeasible_tol: float = 0
    solver_specific: t.Dict[str, t.Any] = {}

    @validator("initial_time_limit", "secondary_time_limit")
    def validate_time_limits(cls, v):
        assert 1e-3 < v < 1e3, f"time_limit must be between 0.001 and 1000 seconds, got {v:.4f} seconds."
        return v

    @validator("initial_mip_gap_tolerance", "secondary_mip_gap_tolerance")
    def validate_mip_gaps(cls, v):
        assert 0 <= v < 1, f"mip_gap must be between 0 and 1, got {v}."
        return v


class StorageType(str, Enum):
    ac = "ac"
    dc = "dc"


class SingleAxisTracking(BaseModel):
    tracking_type: t.Optional[t.Literal["SAT"]] = "SAT"
    rotation_limit: float = 45.0
    backtrack: bool = True


class FixedTilt(BaseModel):
    tracking_type: t.Optional[t.Literal["FT"]] = "FT"
    tilt: float


class ScalarUtilization(BaseModel):
    dimension_type: t.Optional[t.Literal["scalar"]] = "scalar"
    actual: float
    lower: float
    upper: float

    @root_validator(skip_on_failure=True)
    def between_0_and_1(cls, values):
        for v in "actual", "lower", "upper":
            assert 0 <= values[v] <= 1, "must be between 0 and 1"
        return values


def _check_lengths(strs_lists: t.Dict[str, list]):
    str1 = next(iter(strs_lists.keys()))
    len1 = len(next(iter(strs_lists.values())))
    for k, v in strs_lists.items():
        assert len(v) == len1, f"{str1} and {k} must be the same length"


class TimeSeriesUtilization(BaseModel):
    dimension_type: t.Optional[t.Literal["time_series"]] = "time_series"
    actual: t.List[float]
    lower: t.List[float]
    upper: t.List[float]

    @root_validator(skip_on_failure=True)
    def between_0_and_1(cls, values):
        for v in "actual", "lower", "upper":
            assert all(0 <= vi <= 1 for vi in values[v]), "must be between 0 and 1"
        return values

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        _check_lengths({"actual": values["actual"], "lower": values["lower"], "upper": values["upper"]})
        return values

    def __len__(self) -> int:
        return len(self.actual)


@optional_discriminators(["utilization"])
class ReserveMarket(BaseModel):
    price: t.List[float]
    offer_cap: float
    utilization: t.Union[ScalarUtilization, TimeSeriesUtilization] = Field(..., discriminator="dimension_type")
    duration_requirement: float = Field(0.0, description="market requirement for offer duration (hours)")
    obligation: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        if isinstance(values["utilization"], TimeSeriesUtilization):
            _check_lengths({"price": values["price"], "utilization": values["utilization"]})
        if values["obligation"]:
            _check_lengths({"price": values["price"], "obligation": values["obligation"]})
        return values

    def __len__(self) -> int:
        return len(self.price)


class ReserveMarkets(BaseModel):
    up: t.Optional[t.Dict[str, ReserveMarket]]
    down: t.Optional[t.Dict[str, ReserveMarket]]

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        length = None
        for attrib in "up", "down":
            for v in (values[attrib] or dict()).values():
                if length is None:
                    length = len(v)
                else:
                    assert len(v) == length, "all reserve markets must contain data of the same length"
        return values

    def __len__(self) -> int:
        for v in (self.up or dict()).values():
            return len(v)


class DARTPrices(BaseModel):
    """Mirrors Pandera schema used by the library, but allows for columns of different length, so that users can
    pass, e.g., 5M RTM prices and 1H DAM prices"""

    rtm: t.List[float]
    dam: t.List[float]
    rtorpa: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def check_rtorpa_len(cls, values):
        if values["rtorpa"]:
            assert len(values["rtorpa"]) == len(values["rtm"]), "RTORPA must have same lenght as RTM"
        return values


def _check_time_interval(sub_hourly, hourly, time_interval_mins, subhourly_str, hourly_str):
    rt_intervals_per_hour, err = divmod(len(sub_hourly), len(hourly))
    assert err == 0, f"length of {hourly_str} must divide length of {subhourly_str}"
    assert (
        60 / rt_intervals_per_hour == time_interval_mins
    ), f"lengths of {subhourly_str} and {hourly_str} must reflect time_interval_mins"


class PriceScenarios(BaseModel):
    prices: t.List[t.List[float]]
    weights: t.List[float]

    @root_validator(skip_on_failure=True)
    def check_weight_length(cls, values):
        assert len(values["weights"]) == len(values["prices"]), "length of weights must equal length of prices"
        return values

    @validator("prices")
    def check_price_lengths(cls, v):
        # assert all prices have the same lengths
        l0 = len(v[0])
        assert all(len(v1) == l0 for v1 in v), "all prices must have the same length"
        return v

    def __len__(self):
        return len(self.prices[0])

    @property
    def shape(self):
        return len(self.prices), len(self.prices[0])


class DARTPriceScenarios(BaseModel):
    dam: PriceScenarios
    rtm: PriceScenarios

    @root_validator(skip_on_failure=True)
    def check_equal_lengths(cls, values):
        assert values["dam"].shape[1] == values["rtm"].shape[1]
        return values

    def __len__(self):
        return self.dam.shape[1]


class MarketBase(BaseModel):
    energy_prices: t.Union[DARTPrices, t.List[float], DARTPriceScenarios]
    reserve_markets: t.Optional[ReserveMarkets]
    time_interval_mins: t.Optional[int] = 60
    load_peak_reduction: t.Optional[LoadPeakReduction]

    @root_validator(skip_on_failure=True)
    def check_time_interval(cls, values):
        if isinstance(values["energy_prices"], DARTPrices):
            _check_time_interval(
                values["energy_prices"].rtm,
                values["energy_prices"].dam,
                values["time_interval_mins"],
                "rtm prices",
                "dam prices",
            )
        return values

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        if values["reserve_markets"]:
            _check_lengths(
                {"dam prices": values["energy_prices"].dam, "reserve market data": values["reserve_markets"]}
            )

        if values["load_peak_reduction"]:
            _check_lengths(
                {"rtm prices": values["energy_prices"].rtm, "peak reduction data": values["load_peak_reduction"]}
            )
        return values


class SolarResourceTimeSeries(BaseModel):
    year: t.List[int]
    month: t.List[int]
    day: t.List[int]
    hour: t.List[int]
    minute: t.List[int]
    tdew: t.List[float]
    df: t.List[float]
    dn: t.List[float]
    gh: t.List[float]
    pres: t.List[float]
    tdry: t.List[float]
    wdir: t.List[float]
    wspd: t.List[float]
    alb: t.Optional[t.List[float]]
    snow: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def check_lengths(cls, values):
        assert mod(len(next(iter(values.values()))), 8760) == 0, "solar resource time series data must represent 1 year"
        try:
            _check_lengths({k: v for k, v in values.items() if v is not None})
        except AssertionError:
            raise AssertionError("solar resource time series data must have consistent lengths")
        return values

    def __len__(self) -> int:
        return len(self.year)


class SolarResource(BaseModel):
    latitude: float
    longitude: float
    time_zone_offset: float
    elevation: float
    data: SolarResourceTimeSeries
    monthly_albedo: t.Optional[t.List[float]]

    def __len__(self) -> int:
        return len(self.data)


class PSMRegion(str, Enum):
    NorthAmerica = "North America"
    AsiaPacific = "Asia/Pacific"


class SolarResourceLocation(BaseModel):
    latitude: float
    longitude: float
    region: PSMRegion = PSMRegion.NorthAmerica

    class Config:
        extra = "forbid"


class FileComponent(BaseModel):
    path: str


class PVModuleCEC(BaseModel):
    bifacial: bool
    a_c: float
    n_s: float
    i_sc_ref: float
    v_oc_ref: float
    i_mp_ref: float
    v_mp_ref: float
    alpha_sc: float
    beta_oc: float
    t_noct: float
    a_ref: float
    i_l_ref: float
    i_o_ref: float
    r_s: float
    r_sh_ref: float
    adjust: float
    gamma_r: float
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float


class MermoudModuleTech(str, Enum):
    SiMono = "mtSiMono"
    SiPoly = "mtSiPoly"
    CdTe = "mtCdTe"
    CIS = "mtCIS"
    uCSi_aSiH = "mtuCSi_aSiH"


class PVModuleMermoudLejeune(BaseModel):
    bifacial: bool
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float
    tech: MermoudModuleTech
    iam_c_cs_iam_value: t.Optional[t.List[float]]
    iam_c_cs_inc_angle: t.Optional[t.List[float]]
    i_mp_ref: float
    i_sc_ref: float
    length: float
    n_diodes: int
    n_parallel: int
    n_series: int
    r_s: float
    r_sh_0: float
    r_sh_exp: float
    r_sh_ref: float
    s_ref: float
    t_c_fa_alpha: float
    t_ref: float
    v_mp_ref: float
    v_oc_ref: float
    width: float
    alpha_sc: float
    beta_oc: float
    mu_n: float
    n_0: float
    custom_d2_mu_tau: t.Optional[float]


class BaseInverter(BaseModel):
    mppt_low: float
    mppt_high: float
    paco: float
    vdco: float
    pnt: float
    includes_xfmr: bool = False


class Inverter(BaseInverter):
    pso: float
    pdco: float
    c0: float
    c1: float
    c2: float
    c3: float
    vdcmax: float
    tdc: t.List[t.List[float]] = Field(default_factory=lambda: [[1.0, 52.8, -0.021]])


class ONDTemperatureDerateCurve(BaseModel):
    ambient_temp: t.List[float]
    max_ac_power: t.List[float]


class ONDEfficiencyCurve(BaseModel):
    dc_power: t.List[float]
    ac_power: t.List[float]


class ONDInverter(BaseInverter):
    temp_derate_curve: ONDTemperatureDerateCurve
    nominal_voltages: t.List[float]
    power_curves: t.List[ONDEfficiencyCurve]
    dc_turn_on: float
    aux_loss: t.Optional[float]
    aux_loss_threshold: t.Optional[float]

    @root_validator(skip_on_failure=True)
    def check_sufficient_power_curves_voltages(cls, values):
        assert (
            len(values["power_curves"]) == len(values["nominal_voltages"]) == 3
        ), "3 power curves and corresponding voltages required for OND model"
        return values

    @root_validator(skip_on_failure=True)
    def check_aux_loss_etc(cls, values):
        if (values.get("aux_loss") is None) != (values.get("aux_loss_threshold") is None):
            raise AssertionError("either both or neither of aux_loss and aux_loss_threshold must be provided")
        return values


InverterTypes = t.Union[Inverter, ONDInverter, str, FileComponent]
PVModuleTypes = t.Union[PVModuleCEC, PVModuleMermoudLejeune, str, FileComponent]


class Layout(BaseModel):
    orientation: t.Optional[str]
    vertical: t.Optional[int]
    horizontal: t.Optional[int]
    aspect_ratio: t.Optional[float]

    @root_validator(skip_on_failure=True)
    def all_or_none(cls, values):
        missing = [v is None for k, v in values.items()]
        assert all(missing) or not any(missing), "Either all or no attributes must be assigned in Layout"
        return values


class Transformer(BaseModel):
    rating: t.Optional[float]
    load_loss: float
    no_load_loss: float


class ACLosses(BaseModel):
    ac_wiring: float = 0.01
    transmission: float = 0.0
    # Feeds into nrel_sam.AdjustmentFactors rather than nrel_sam.Losses
    poi_adjustment: float = 0.0  # TODO: deprecate this?
    transformer_load: t.Optional[float]  # deprecate
    transformer_no_load: t.Optional[float]  # deprecate
    hv_transformer: t.Optional[Transformer]
    mv_transformer: t.Optional[Transformer]

    @root_validator(skip_on_failure=True)
    def check_repeated_hv_transformer(cls, values):
        assert (values["transformer_load"] is None and values["transformer_no_load"] is None) or values[
            "hv_transformer"
        ] is None, "Cannot provide hv_transformer if transformer_load or transformer_no_load are provided"
        return values


class DCLosses(BaseModel):
    dc_optimizer: float = 0.0
    enable_snow_model: bool = False
    dc_wiring: float = 0.02
    soiling: t.List[float] = Field(default_factory=lambda: 12 * [0.0])
    diodes_connections: float = 0.005
    mismatch: float = 0.01
    nameplate: float = 0.0
    rear_irradiance: float = 0.0
    mppt_error: float = 0.0  # TODO: remove once mppt_error deprecated, equivalent to tracking_error
    tracking_error: float = 0.0

    # Feeds into nrel_sam.AdjustmentFactors rather than nrel_sam.Losses
    lid: float = 0.0
    dc_array_adjustment: float = 0.0

    @root_validator(skip_on_failure=True)
    def check_tracker_losses(cls, values):  # TODO: remove once mppt_error deprecated, equivalent to tracking_error
        assert (
            values["mppt_error"] * values["tracking_error"] == 0.0
        ), "Only one of mppt_error and tracking_error may be nonzero"
        return values


class Losses(ACLosses, DCLosses):
    class Config:
        extra = "forbid"


class DCProductionProfile(BaseModel):
    power: t.List[float]
    voltage: t.List[float]
    ambient_temp: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        _check_lengths({"power": values["power"], "voltage": values["voltage"]})
        if values["ambient_temp"]:
            _check_lengths({"power": values["power"], "ambient_temp": values["ambient_temp"]})
        return values

    def __len__(self) -> int:
        return len(self.power)


class ACProductionProfile(BaseModel):
    power: t.List[float]
    ambient_temp: t.Optional[t.List[float]]

    # if ACProductionProfile is allowed to have extra fields in the payload, then a DCProductionProfile payload will be
    # coerced into an ACProductionProfile object if something is wrong with voltage
    class Config:
        extra = "forbid"

    @root_validator(skip_on_failure=True)
    def check_length(cls, values):
        if values["ambient_temp"]:
            _check_lengths({"power": values["power"], "ambient_temp": values["ambient_temp"]})
        return values

    def __len__(self) -> int:
        return len(self.power)


ProductionProfile = t.Union[DCProductionProfile, ACProductionProfile]


class BaseSystemDesign(BaseModel):
    dc_capacity: float
    ac_capacity: float
    poi_limit: float


@optional_discriminators(["tracking"])
class PVSystemDesign(BaseSystemDesign):
    modules_per_string: t.Optional[int]
    strings_in_parallel: t.Optional[int]
    tracking: t.Union[FixedTilt, SingleAxisTracking] = Field(..., discriminator="tracking_type")
    azimuth: float = 180.0
    gcr: float


class TermUnits(str, Enum):
    hours = "hours"
    days = "days"
    years = "years"


class ProjectTermMixin(BaseModel):
    project_term: int = 1
    project_term_units: TermUnits = "years"


class BaseGenerationModel(ProjectTermMixin):
    project_type: t.Optional[t.Literal["generation"]] = "generation"
    time_interval_mins: int = 60


def scale_project_term_to_hours(project_term: int, project_term_units: TermUnits) -> int:
    if project_term_units == "hours":
        return project_term
    elif project_term_units == "days":
        return 24 * project_term
    else:  # years
        return 8760 * project_term


def _check_time_interval_project_term(
    signal_len, signal_str, project_term, time_interval_mins, project_term_units: TermUnits
):
    """
    For more on why we treat project_term as an int and validate like we do check out this PR comment:
    https://github.com/Tyba-Energy/generation/pull/186#discussion_r1054578658. The broader PR has even more context
    should it be needed
    """
    signal_hours = int(signal_len * (time_interval_mins / 60))
    project_term_hours = scale_project_term_to_hours(project_term, project_term_units)
    assert (
        project_term_hours == signal_hours
    ), f"project_term, project_term_units, time_interval_mins, and length of {signal_str} must be consistent"


class ExternalGenerationModel(BaseGenerationModel):
    losses: t.Union[ACLosses, Losses]
    production_override: ProductionProfile
    system_design: BaseSystemDesign

    @root_validator(skip_on_failure=True)
    def check_time_interval_project_term(cls, values):
        _check_time_interval_project_term(
            len(values["production_override"]),
            "production_override",
            values["project_term"],
            values["time_interval_mins"],
            values["project_term_units"],
        )
        return values

    def __len__(self) -> int:
        return len(self.production_override)


class ACExternalGenerationModel(ExternalGenerationModel):
    generation_type: t.Optional[t.Literal["ExternalAC"]] = "ExternalAC"
    losses: ACLosses = ACLosses()
    production_override: ACProductionProfile


class DCExternalGenerationModel(ExternalGenerationModel):
    generation_type: t.Optional[t.Literal["ExternalDC"]] = "ExternalDC"
    losses: Losses = Losses()
    production_override: DCProductionProfile
    inverter: InverterTypes


class ArrayDegradationMode(str, Enum):
    linear = "linear"
    compounding = "compounding"


def _pv_gen_len(sol_res, pt):
    if isinstance(sol_res, SolarResource):
        return len(sol_res) * pt
    else:
        return 8760 * pt


class PVGenerationModel(BaseGenerationModel):
    generation_type: t.Optional[t.Literal["PV"]] = "PV"
    solar_resource: t.Union[SolarResource, t.Tuple[float, float], SolarResourceLocation]
    inverter: InverterTypes
    pv_module: PVModuleTypes
    layout: Layout = Layout()
    losses: Losses = Losses()
    system_design: PVSystemDesign
    array_degradation_rate: float = 0.005
    array_degradation_mode: ArrayDegradationMode = ArrayDegradationMode.linear

    def __len__(self) -> int:
        return _pv_gen_len(self.solar_resource, self.project_term)

    @root_validator(skip_on_failure=True)
    def check_time_interval_project_term(cls, values):
        _check_time_interval_project_term(
            _pv_gen_len(values["solar_resource"], values["project_term"]),
            "solar_resource",
            values["project_term"],
            values["time_interval_mins"],
            values["project_term_units"],
        )
        return values

    @validator("project_term_units")
    def check_project_term_units(cls, v):
        assert v == "years", "Currently only project_term_units of 'years' is supported for PVGenerationModel objects"
        return v


GenerationModel = Annotated[
    t.Union[PVGenerationModel, DCExternalGenerationModel, ACExternalGenerationModel],
    Field(discriminator="generation_type"),
]


class TableCapDegradationModel(BaseModel):
    annual_capacity_derates: t.List[float]


class TableEffDegradationModel(BaseModel):
    annual_efficiency_derates: t.List[float]


class BatteryHVACParams(BaseModel):
    container_temperature: float
    cop: float
    u_ambient: float
    discharge_efficiency_container: float
    charge_efficiency_container: float
    aux_xfmr_efficiency: float
    container_surface_area: float = 20.0
    design_energy_per_container: float = 750.0


class BatteryParams(BaseModel):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    degradation_rate: t.Optional[float]
    degradation_annual_cycles: float = 261  # cycle / work day
    hvac: t.Optional[BatteryHVACParams]
    capacity_degradation_model: t.Optional[TableCapDegradationModel]
    efficiency_degradation_model: t.Optional[TableEffDegradationModel]
    term: t.Optional[float]

    @root_validator(skip_on_failure=True)
    def check_cap_degradation_models(cls, values):
        assert not (
            values["degradation_rate"] is None and values["capacity_degradation_model"] is None
        ), "Either degradation_rate or capacity_degradation_model must be specified"
        assert (
            values["degradation_rate"] is None or values["capacity_degradation_model"] is None
        ), "Only one of degradation_rate and capacity_degradation_model may be specified"
        return values

    @root_validator(skip_on_failure=True)
    def check_degrad_table_length(cls, values):
        term = values["term"] or 0  # validate against term if term is provided
        for dm in "capacity", "efficiency":
            if values[f"{dm}_degradation_model"]:
                assert (
                    len(getattr(values[f"{dm}_degradation_model"], f"annual_{dm}_derates")) - 1 >= term
                ), f"annual_{dm}_derates must be long enough to cover battery term"
        return values


class EnergyStrategy(str, Enum):
    da = "DA"
    rt = "RT"
    dart = "DART"


class StorageSolverOptions(BaseModel):
    cycling_cost_adder: float = 0.0
    annual_cycle_limit: float = None
    disable_intra_interval_variation: bool = False
    window: int = None
    step: int = None
    flexible_solar: bool = False
    symmetric_reg: bool = False
    energy_strategy: t.Optional[EnergyStrategy]
    dart: t.Optional[bool]
    uncertain_soe: bool = True
    dam_annual_cycle_limit: float = None
    no_virtual_trades: bool = False
    initial_soe: float = 0.0
    duration_requirement_on_discharge: bool = True  # True for ERCOT
    solver: t.Optional[str] = None
    solver_config: SolverConfig = SolverConfig()

    @root_validator(skip_on_failure=True)
    def check_dam_annual_cycle_limit(cls, values):
        if values["dam_annual_cycle_limit"] is not None and not (values["dart"] or values["energy_strategy"] == "DART"):
            raise AssertionError("dart must be `true` if dam_annual_cycle_limit is set")
        return values

    @validator("solver")
    def check_solver_name(cls, v):
        valid_solvers = ["HiGHS", "GLPK", "HiGHS-GLPK", None]
        assert v in valid_solvers, f"solver must be one of {valid_solvers}"
        return v

    @root_validator(skip_on_failure=True)
    def check_solver_config(cls, values):
        if values["solver_config"].solver_specific and (values["solver"] not in {"HiGHS", "GLPK"}):
            raise ValueError("solver_specific options may only be passed when using HiGHS or GLPK solver")
        return values

    @root_validator(skip_on_failure=True)
    def support_deprecated_dart(cls, values):
        assert not (values["dart"] is not None and values["energy_strategy"] is not None), (
            "Only one of `dart` or `energy_strategy` may be provided. `dart` is deprecated; use `energy_strategy`"
            " instead."
        )
        if values["energy_strategy"] is None:
            values["energy_strategy"] = EnergyStrategy.dart if values["dart"] else EnergyStrategy.da
            values["dart"] = None
        return values


class MultiStorageInputs(StorageSolverOptions):
    batteries: t.List[BatteryParams]

    @validator("batteries")
    def check_battery_terms(cls, v):
        if len(v) > 1:  # don't worry about terms if there's only one battery
            for battery in v:
                assert battery.term, "if multiple batteries are provided, terms must also be provided"
        return v


class StorageCoupling(str, Enum):
    ac = "ac"
    dc = "dc"
    hv_ac = "hv_ac"


def _get_price_str_and_price(values):
    if isinstance(values["energy_prices"], (DARTPrices, DARTPriceScenarios)):
        return "rtm prices", values["energy_prices"].rtm
    return "energy_prices", values["energy_prices"]


class PeakWindow(BaseModel):
    mask: t.List[bool]
    price: float


class LoadPeakReduction(BaseModel):
    load: t.List[float]
    max_load: t.List[float]  # TODO: should be optional -- https://app.asana.com/0/1178990154879730/1203603348130562/f
    seasonal_peak_windows: t.List[PeakWindow] = []
    daily_peak_windows: t.List[PeakWindow] = []

    @root_validator(skip_on_failure=True)
    def check_lengths(cls, values):
        windows = [*values["seasonal_peak_windows"], *values["daily_peak_windows"]]
        assert (
            windows
        ), "One or both of seasonal_peak_windows and daily_peak_windows must be provided when using load_peak_reduction"
        length = len(values["load"])
        assert len(values["max_load"]) == length, "load and max_load must have same length"
        for window in windows:
            assert len(window.mask) == length, "peak masks must have same length as load"
        return values

    def __len__(self) -> int:
        return len(self.load)


class ImportExportLimitMixin(BaseModel):
    import_limit: t.Optional[t.List[float]]
    export_limit: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def validate_limits(cls, values):
        if values["import_limit"] is not None:
            assert all([v <= 0 for v in values["import_limit"]]), "import_limit must be <= 0"
        if values["export_limit"] is not None:
            assert all([v >= 0 for v in values["export_limit"]]), "export_limit must be >= 0"
        return values

    @root_validator(skip_on_failure=True)
    def check_import_export_lengths(cls, values):
        for limit in "import_limit", "export_limit":
            if values[limit]:
                price_str, price = _get_price_str_and_price(values)
                _check_lengths({limit: values[limit], price_str: price})
        return values


def _check_degrad_table_length(values: dict):
    if len(values["storage_inputs"].batteries) == 1:
        battery = values["storage_inputs"].batteries[0]
        pt = (
            scale_project_term_to_hours(
                values.get("project_term") or values["pv_inputs"].project_term,
                values.get("project_term_units") or values["pv_inputs"].project_term_units,
            )
            / 8760
        )
        for dm in "capacity", "efficiency":
            if dm_ob := getattr(battery, f"{dm}_degradation_model"):
                tbl_yrs = len(getattr(dm_ob, f"annual_{dm}_derates")) - 1
                assert tbl_yrs >= pt, f"annual_{dm}_derates must be long enough to cover project/battery term"
    return values


def _check_symmetric_reg_inputs(values: dict):
    if values["storage_inputs"].symmetric_reg:
        assert values.get(
            "reserve_markets"
        ), "when storage_inputs.symmetric_reg is True, reserve_markets must be provided"
        assert ("reg_up" in (values["reserve_markets"].up or dict())) and (
            "reg_down" in (values["reserve_markets"].down or dict())
        ), "when storage_inputs.symmetric_reg is True, both reg_up and reg_down reg markets must be provided"

    return values


@optional_discriminators(["pv_inputs"])
class PVStorageModel(ImportExportLimitMixin, MarketBase):
    project_type: t.Optional[t.Literal["hybrid"]] = "hybrid"
    storage_inputs: MultiStorageInputs
    storage_coupling: StorageCoupling
    pv_inputs: GenerationModel
    enable_grid_charge_year: t.Optional[float]

    @property
    def project_term(self) -> int:
        """symmetric retrieval of project_term for convenience"""
        return self.pv_inputs.project_term

    @property
    def project_term_units(self) -> TermUnits:
        return self.pv_inputs.project_term_units

    @root_validator(skip_on_failure=True)
    def check_time_intervals(cls, values):
        assert (
            values["time_interval_mins"] == values["pv_inputs"].time_interval_mins
        ), "pv and price time_interval_mins must be equal"
        return values

    @root_validator(skip_on_failure=True)
    def check_pv_length(cls, values):
        price_str, price = _get_price_str_and_price(values)
        _check_lengths({price_str: price, "pv_inputs": values["pv_inputs"]})
        return values

    @root_validator(skip_on_failure=True)
    def check_battery_terms(cls, values):
        if len(values["storage_inputs"].batteries) > 1:
            total_batt_yrs = sum(bat.term for bat in values["storage_inputs"].batteries)
            assert (
                scale_project_term_to_hours(values["pv_inputs"].project_term, values["pv_inputs"].project_term_units)
                >= total_batt_yrs * 8760
            ), "project_term must be greater than or equal to the total battery terms"
        return values

    @root_validator(skip_on_failure=True)
    def check_degrad_table_length(cls, values):
        return _check_degrad_table_length(values)

    @root_validator(skip_on_failure=True)
    def check_sym_reg_inputs(cls, values):
        return _check_symmetric_reg_inputs(values)


class StandaloneStorageModel(ProjectTermMixin, ImportExportLimitMixin, MarketBase):
    project_type: t.Optional[t.Literal["storage"]] = "storage"
    storage_inputs: MultiStorageInputs
    ambient_temp: t.Optional[t.List[float]]

    @root_validator(skip_on_failure=True)
    def check_ambient_temp_length(cls, values):
        if values["ambient_temp"]:
            price_str, price = _get_price_str_and_price(values)
            _check_lengths({price_str: price, "ambient_temp": values["ambient_temp"]})
        return values

    @root_validator(skip_on_failure=True)
    def check_time_interval_project_term(cls, values):
        price_str, price = _get_price_str_and_price(values)
        _check_time_interval_project_term(
            len(price), price_str, values["project_term"], values["time_interval_mins"], values["project_term_units"]
        )
        return values

    @root_validator(skip_on_failure=True)
    def check_battery_and_project_terms(cls, values):
        # only validate battery terms if a battery term is passed or multiple batteries are passed
        if len(values["storage_inputs"].batteries) > 1 or values["storage_inputs"].batteries[0].term is not None:
            total_batt_yrs = sum(bat.term for bat in values["storage_inputs"].batteries)
            project_term_hours = scale_project_term_to_hours(values["project_term"], values["project_term_units"])
            total_battery_term_hours = int(total_batt_yrs * 8760)
            assert (
                project_term_hours == total_battery_term_hours
            ), "project_term must be consistent with the total battery terms"
            price_str, price = _get_price_str_and_price(values)
            price_hours = int(len(price) * (values["time_interval_mins"] / 60))
            assert (
                price_hours >= total_battery_term_hours
            ), f"length of {price_str} must be greater than total battery terms"
        return values

    @root_validator(skip_on_failure=True)
    def check_degrad_table_length(cls, values):
        return _check_degrad_table_length(values)

    @root_validator(skip_on_failure=True)
    def check_sym_reg_inputs(cls, values):
        return _check_symmetric_reg_inputs(values)


def get_pv_model(**data: t.Any) -> GenerationModel:
    try:
        m = PVGenerationModel(**data)
    except ValidationError:
        try:
            m = DCExternalGenerationModel(**data)
        except ValidationError:
            m = ACExternalGenerationModel(**data)
    return m


def get_pv_storage_model(**data: t.Any) -> PVStorageModel:
    return PVStorageModel(**data)


def get_standalone_storage_model(model: dict) -> StandaloneStorageModel:
    return StandaloneStorageModel(**model)


JobModel = Annotated[
    t.Union[StandaloneStorageModel, PVStorageModel, GenerationModel], Field(discriminator="project_type")
]


@optional_discriminators(["model"])
class AsyncModelBase(BaseModel):
    id: str
    model: JobModel
    results_path: t.Optional[str]


@optional_discriminators(["model"])
class AsyncPVModel(AsyncModelBase):
    id: str
    model: GenerationModel


class AsyncPVStorageModel(AsyncModelBase):
    id: str
    model: PVStorageModel


class AsyncStandaloneStorageModel(AsyncModelBase):
    id: str
    model: StandaloneStorageModel
