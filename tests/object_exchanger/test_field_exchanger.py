from physics_driver import ObjectDriver, DictContainer

import c3po
from c3po.field.Field import ObjectExchanger
from c3po import DirectMatching, LocalDataManager, FixedPointCoupler


def test():
    driver_a = ObjectDriver(DictContainer({"value": 1.}))

    manager = LocalDataManager()

    exchanger_b_to_manager = ObjectExchanger(
        method=DirectMatching(),
        objectsToGet=[(driver_a, "value")],
        objectsToSet=[(manager, "value")],
    )

    exchanger_manager_to_a = ObjectExchanger(
        method=DirectMatching(),
        objectsToGet=[(manager, "value")],
        objectsToSet=[(driver_a, "value")],
    )

    fixed_point_coupler = FixedPointCoupler([driver_a], [exchanger_b_to_manager, exchanger_manager_to_a], [manager])
    fixed_point_coupler.setConvergenceParameters(1E-6, 1000)
    fixed_point_coupler.setDampingFactor(.5)
    fixed_point_coupler.init()
    fixed_point_coupler.solve()
    fixed_point_coupler.term()

    assert abs(driver_a.value.value["value"] - 4 / 3) < 1e-4, f"Expected {4/3}, found {driver_a.value.value['value']}"


if __name__ == "__main__":
    test()
