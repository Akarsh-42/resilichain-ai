from .models import ConstraintSet, Disruption, NodeType, Route, ScenarioState, SupplyNode


def port_closure_scenario() -> ScenarioState:
    """A deterministic demo with two successive disruptions and a feasible recovery."""
    return ScenarioState(
        scenario_id="port-closure-001",
        title="East Port Closure + Carrier Breakdown",
        objective="Restore 80 units of SKU-AX9 to Central City Store within 24 hours.",
        destination_id="store-central",
        constraints=ConstraintSet(
            sku="SKU-AX9",
            required_units=80,
            deadline_hours=24,
            maximum_cost=2500,
            maximum_carbon_kg=50,
        ),
        nodes=[
            SupplyNode(
                id="wh-east",
                name="East Port Warehouse",
                node_type=NodeType.WAREHOUSE,
                inventory={"SKU-AX9": 140},
                latitude=22.5726,
                longitude=88.3639,
            ),
            SupplyNode(
                id="wh-west",
                name="West Regional Warehouse",
                node_type=NodeType.WAREHOUSE,
                inventory={"SKU-AX9": 120},
                latitude=19.0760,
                longitude=72.8777,
            ),
            SupplyNode(
                id="wh-south",
                name="South Express Hub",
                node_type=NodeType.WAREHOUSE,
                inventory={"SKU-AX9": 100},
                latitude=13.0827,
                longitude=80.2707,
            ),
            SupplyNode(
                id="store-central",
                name="Central City Store",
                node_type=NodeType.STORE,
                inventory={"SKU-AX9": 20},
                latitude=20.2961,
                longitude=85.8245,
            ),
        ],
        routes=[
            Route(
                id="east-road",
                source_id="wh-east",
                destination_id="store-central",
                mode="road",
                capacity_units=100,
                cost=1400,
                delivery_hours=18,
                carbon_kg=28,
                available=False,
            ),
            Route(
                id="west-road",
                source_id="wh-west",
                destination_id="store-central",
                mode="road",
                capacity_units=100,
                cost=1750,
                delivery_hours=22,
                carbon_kg=32,
            ),
            Route(
                id="south-express",
                source_id="wh-south",
                destination_id="store-central",
                mode="road-rail",
                capacity_units=90,
                cost=2200,
                delivery_hours=23,
                carbon_kg=40,
            ),
            Route(
                id="emergency-air",
                source_id="wh-south",
                destination_id="store-central",
                mode="air",
                capacity_units=100,
                cost=3800,
                delivery_hours=8,
                carbon_kg=95,
            ),
        ],
        disruptions=[
            Disruption(
                id="d-port",
                kind="port_closure",
                target_id="east-road",
                description="Flooding closed the east-port road corridor.",
            )
        ],
        fail_once_route_ids=["west-road"],
    )

