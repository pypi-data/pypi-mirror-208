from emmet.api.routes.materials.robocrys.query_operators import RoboTextSearchQuery
from monty.tempfile import ScratchDir
from monty.serialization import loadfn, dumpfn


def test_robocrys_search_query():
    op = RoboTextSearchQuery()

    pipeline = [
        {
            "$search": {
                "index": "description",
                "regex": {
                    "query": ["cubic", "octahedra"],
                    "path": "description",
                    "allowAnalyzedField": True,
                },
            }
        },
        {
            "$facet": {
                "total_doc": [{"$count": "count"}],
                "results": [
                    {
                        "$project": {
                            "_id": 0,
                            "task_id": 1,
                            "material_id": 1,
                            "description": 1,
                            "condensed_structure": 1,
                            "last_updates": 1,
                            "search_score": {"$meta": "searchScore"},
                        }
                    }
                ],
            }
        },
        {"$unwind": "$results"},
        {"$unwind": "$total_doc"},
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": ["$results", {"total_doc": "$total_doc.count"}]
                }
            }
        },
        {"$sort": {"search_score": -1}},
        {"$skip": 0},
        {"$limit": 10},
    ]

    assert op.query(keywords="cubic, octahedra", _skip=0, _limit=10) == {
        "pipeline": pipeline
    }

    with ScratchDir("."):
        dumpfn(op, "temp.json")
        new_op = loadfn("temp.json")
        query = {"pipeline": pipeline}
        assert new_op.query(keywords="cubic, octahedra", _skip=0, _limit=10) == query

    assert op.post_process([{"total_doc": 10}], query) == [{"total_doc": 10}]
    assert op.meta() == {"total_doc": 10}
