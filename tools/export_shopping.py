"""Refresh the site's purchase data from a MAC-benchmark checkout."""
import argparse
import json
import sys
from pathlib import Path


def recorded_run(episode, score):
    """Replay the sealed run and capture the responses whose digests the kernel logged."""
    from macbench.domains.shopping.tasks import bare_kernel
    from macbench.kernel.engine import verified_final_state

    sealed = episode.kernel.seal()
    responses = {}

    def recording_kernel():
        kernel = bare_kernel(episode.task)
        call = kernel.call

        def capture(seat, request, origin="seat", wake_with=()):
            start = len(kernel.log)
            result = call(seat, request, origin=origin, wake_with=wake_with)
            # A seat's wait may have logged several controller calls before its own call.
            entry = next(e for e in kernel.log[start:] if e["type"] == "call" and e["by"] == origin)
            responses[entry["i"]] = result.result if result.ok else result.error.model_dump(mode="json")
            return result

        kernel.call = capture
        return kernel

    final = verified_final_state(recording_kernel, sealed)
    assert score.valid and final is not None, episode.task.task_id
    events = sealed["events"]
    assert set(responses) == {e["i"] for e in events if e["type"] == "call"}, episode.task.task_id
    service = final["service"]
    market = {"demand": iter(service["demand_log"]), "restock": iter(service["restock_log"])}
    order_fields = ("order_id", "merchant_name", "paid_cents", "promised_delivery_date")
    orders = [{k: order[k] for k in order_fields} for order in service["orders"].values()]
    return {
        "head": sealed["head"], "events": events, "responses": responses, "score": score.as_dict(), "orders": orders,
        "market": {e["i"]: next(market[e["kind"]]) for e in events if e["type"] == "event" and e["kind"] in market},
    }


def opening_offers(task, merchants):
    from macbench.domains.shopping import persona

    catalogue = task.scenario().catalog
    items = persona.items_of(task.shopper.facts, lambda variant_id: catalogue.variant(variant_id).product_id)
    offers = []
    for item in items:
        product = catalogue.product(item.product_id)
        for variant_id in item.acceptable():
            variant = catalogue.variant(variant_id)
            for merchant in merchants:
                listing = catalogue.listing(item.product_id, merchant)
                offers.append({
                    "variant_id": variant_id, "product": product.name, "value": variant.value,
                    "substitute": variant_id != item.variant_id, "merchant": merchant,
                    "stock": catalogue.stock_of(variant_id, merchant), "price_cents": listing.list_price_cents,
                    "delivery_days": listing.delivery_days,
                })
    return offers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path)
    benchmark = parser.parse_args().benchmark.resolve()
    sys.path.insert(0, str(benchmark / "src"))

    from macbench.domains.shopping import catalog, examples, foils, generator, interface, reference, tasks

    dev = benchmark / "tasks" / "shopping" / "dev"
    manifest = json.loads((dev / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["interface"] == interface.VERSION, "shopping manifest and interface versions differ"

    records = []
    runs = {}
    for row in manifest["tasks"]:
        task_id = row["task_id"]
        fixture = json.loads((dev / f"{task_id}.json").read_text(encoding="utf-8"))
        task = tasks.from_dict(fixture)
        assert task.kind == "purchase" and generator.digest(task) == row["digest"], task_id
        episode, score = tasks.run(task, reference.play)
        careless_episode, careless = tasks.run(task, foils.play(row["careless_agent"]["name"]), score)
        assert (score.success, score.total_loss_cents) == (row["reference"]["success"], row["reference"]["loss_cents"]), task_id
        assert all(score.process[key] == row["reference"][key]
                   for key in ("calls", "world_minutes", "refused_by_code", "proposals_rejected")), task_id
        assert (careless.success, careless.regret_cents, careless.failed()) == (
            row["careless_agent"]["success"], row["careless_agent"]["regret_cents"], row["careless_agent"]["failed"]), task_id

        runs[task_id] = {"reference": recorded_run(episode, score), "careless": recorded_run(careless_episode, careless)}
        fields = ("task_id", "family", "title", "source", "variant", "observation_minutes",
                  "reference", "leaving_succeeds", "careless_agent", "slower_reference", "digest", "world_now")
        records.append({
            **{key: row[key] for key in fields}, "brief": task.brief, "tests": task.tests,
            "facts": task.shopper.facts, "delay_minutes": task.shopper.delay_minutes,
            "opening_offers": opening_offers(task, catalog.MERCHANTS), "events": fixture["events"],
            "merchant_policies": fixture["merchant_policies"],
            "cards": {"Shopping agent": tasks.agent_card(task, episode), "Shopper": tasks.shopper_card(task, episode)},
        })

    inventory = catalog.load()
    spec = interface.INTERFACE.export(set())
    action_fields = ("group", "name", "roles", "time_cost_s", "wait_field", "errors")
    checkout = ("price_cart", "reserve_cart", "create_proposal", "grant_authorization", "place_order")
    data = {
        "interface": spec["version"],
        "catalogue": {"products": len(inventory.products), "listings": len(inventory.listings),
                      "variants": len(inventory.variants), "categories": len({p.category for p in inventory.products.values()}),
                      "merchants": catalog.MERCHANTS},
        "tasks": records,
        "actions": [{key: action[key] for key in action_fields} for action in spec["actions"]],
        "examples": {name: {key: examples.EXAMPLES[name][key] for key in ("request", "response")} for name in checkout},
    }
    out = Path(__file__).resolve().parents[1] / "data"
    (out / "shopping.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    run_rows = [f"  {json.dumps(task_id)}: {json.dumps(pair, ensure_ascii=False, separators=(',', ':'))}"
                for task_id, pair in runs.items()]
    (out / "shopping_runs.json").write_text("{\n" + ",\n".join(run_rows) + "\n}\n", encoding="utf-8")
    print(f"{len(records)} purchase tasks, {sum(len(pair) for pair in runs.values())} replay-verified runs, {len(data['actions'])} actions")


if __name__ == "__main__":
    main()
