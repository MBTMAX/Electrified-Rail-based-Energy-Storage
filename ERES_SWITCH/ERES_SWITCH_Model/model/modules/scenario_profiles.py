"""Central scenario profiles for the ERES SWITCH simulations."""

from __future__ import annotations


REGIONS = ("CN", "EU", "IN")
ERES_CASES = ("BR", "HR", "NR")
TECH_SCENARIOS = ("A", "C", "M")
CARBON_CASES = (
    "BASELINE",
    "CE000",
    "CE001",
    "CE002",
    "CE003",
    "CE004",
    "CE005",
    "CE006",
    "CE007",
    "CE008",
    "CE009",
    "CE010",
    "CE011",
    "CE012",
    "CE013",
    "CE014",
    "CE015",
    "CE105",
)

_RESERVE_FRACTIONS = {
    ("CN", "A"): {"CAES": 0.885, "H2": 0.4, "Hydro_Pumped": 0.9},
    ("CN", "C"): {"CAES": 0.9, "H2": 0.4, "Hydro_Pumped": 0.9},
    ("CN", "M"): {"CAES": 0.92, "H2": 0.35, "Hydro_Pumped": 0.9},
    ("EU", "A"): {
        "CAES": 0.885,
        "H2": 0.4,
        "Hydro Pumped Storage_EP": 0.9,
    },
    ("EU", "C"): {
        "CAES": 0.9,
        "H2": 0.4,
        "Hydro Pumped Storage_EP": 0.9,
    },
    ("EU", "M"): {
        "CAES": 0.92,
        "H2": 0.4,
        "Hydro Pumped Storage_EP": 0.9,
    },
    ("IN", "A"): {"CAES": 0.885, "H2": 0.4, "Pumped Storage_EP": 0.9},
    ("IN", "C"): {"CAES": 0.9, "H2": 0.4, "Pumped Storage_EP": 0.9},
    ("IN", "M"): {"CAES": 0.92, "H2": 0.4, "Pumped Storage_EP": 0.9},
}


def _build_profiles():
    profiles = {}
    for region in REGIONS:
        for eres_case in ERES_CASES:
            for tech_scenario in TECH_SCENARIOS:
                profile_name = f"{region}_{eres_case}_{tech_scenario}"
                profiles[profile_name] = {
                    "region": region,
                    "eres_case": eres_case,
                    "tech_scenario": tech_scenario,
                    "spinning_reserve_fractions": dict(
                        _RESERVE_FRACTIONS[
                            (region, tech_scenario)
                        ]
                    ),
                }
    return profiles


SCENARIO_PROFILES = _build_profiles()


def define_arguments(argparser):
    argparser.add_argument(
        "--scenario-profile",
        choices=sorted(SCENARIO_PROFILES),
        default=None,
        help=(
            "Scenario configuration profile: region (CN/EU/IN), "
            "ERES case (BR/HR/NR), and technology scenario (A/C/M)."
        ),
    )
    argparser.add_argument(
        "--carbon-case",
        choices=CARBON_CASES,
        default=None,
        help="Carbon-policy case selected from the global input bundle.",
    )


def get_scenario_profile(model):
    profile_name = model.options.scenario_profile
    if profile_name is None:
        raise ValueError(
            "Missing required --scenario-profile. Choose one of: "
            + ", ".join(sorted(SCENARIO_PROFILES))
        )
    return SCENARIO_PROFILES[profile_name]
