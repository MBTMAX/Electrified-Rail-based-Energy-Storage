"""Technology-specific spinning-reserve limits for the ERES scenarios."""

from pyomo.environ import Constraint, Param, Set, UnitInterval, value

from modules.scenario_profiles import get_scenario_profile


def define_components(m):
    fractions = get_scenario_profile(m)["spinning_reserve_fractions"]

    m.SPINNING_RESERVE_FRACTION_TECHS = Set(
        dimen=1,
        initialize=tuple(fractions),
    )
    m.tech_spinning_reserve_fraction = Param(
        m.SPINNING_RESERVE_FRACTION_TECHS,
        initialize=fractions,
        within=UnitInterval,
    )

    def Max_Spinning_Reserve_Fraction_rule(m, g, t):
        tech = m.gen_tech[g]
        if tech not in m.SPINNING_RESERVE_FRACTION_TECHS:
            return Constraint.Skip

        fraction = m.tech_spinning_reserve_fraction[tech]
        if value(fraction) == 1.0:
            return Constraint.Skip

        p = m.tp_period[t]
        return (
            m.CommitGenSpinningReservesUp[g, t]
            <= m.GenCapacity[g, p] * fraction
        )

    m.Max_Spinning_Reserve_Fraction = Constraint(
        m.SPINNING_RESERVE_GEN_TPS,
        rule=Max_Spinning_Reserve_Fraction_rule,
    )
