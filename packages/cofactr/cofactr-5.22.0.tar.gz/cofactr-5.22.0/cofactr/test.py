from cofactr.graph import GraphAPI

graph = GraphAPI(client_id="cofactr", api_key="8oDplyDx27eJCMNy")

canonical_product_ids = graph.get_canonical_product_ids(ids=["XX07JKELZ3JG"])

print(canonical_product_ids)

# graph = GraphAPI(protocol="http", host="127.0.0.1:8050")

# res = graph.create_product(
#     data=PartInV0(
#         owner_id="joseph",
#         mpn="test",
#     )
# )

# import pdb

# pdb.set_trace()

# res = graph.get_offers(product_id="XX9YD048JZIV", owner_id="joseph")

# res = graph.create_product(
#     data={
#         "owner_id": "local-a2079fac-30f5-4392-ada4-e4b103a89822",
#         "custom_id": "boodbug",
#         "mpn": "Boodlebug",
#         "alt_mpns": [],
#         "mfr": {"custom_label": "Dooglebop Inc"},
#         "classification": {"custom_label": "Doodle Remote"},
#         "description": "A very boodley part",
#         "msl": None,
#         "package": None,
#         "terminations": None,
#         "termination_type": None,
#     }
# )

# res = graph.autocomplete_classifications(

# )
