import vecs
import numpy as np
import random
import pytest

def test_upsert(client: vecs.Client) -> None:
    n_records = 100
    dim = 384

    movies = client.create_collection(name = 'ping', dimension=dim)

    # collection initially empty
    assert len(movies) == 0


    records = [
        (
            f"vec{ix}",
             vec,
             {
                 "genre": random.choice(["action", "rom-com", "drama"]),
                 "year": int(50*random.random()) + 1970
             }
        )
        for ix, vec in enumerate(np.random.random((n_records, dim)))
    ]

    # insert works
    movies.upsert(records)
    assert len(movies) == n_records

    # upserting overwrites
    new_record =  ("vec0", np.zeros(384), {})
    movies.upsert(
        [new_record]
    )
    db_record = movies["vec0"]
    db_record[0] == new_record[0]
    db_record[1] == new_record[1]
    db_record[2] == new_record[2]


def test_fetch(client: vecs.Client) -> None:
    n_records = 100
    dim = 384

    movies = client.create_collection(name = 'ping', dimension=dim)

    records = [
        (
            f"vec{ix}",
             vec,
             {
                 "genre": random.choice(["action", "rom-com", "drama"]),
                 "year": int(50*random.random()) + 1970
             }
        )
        for ix, vec in enumerate(np.random.random((n_records, dim)))
    ]

    # insert works
    movies.upsert(records)

    # test basic usage
    fetch_ids = ["vec0", "vec15", "vec99"]
    res = movies.fetch(ids=fetch_ids)
    assert len(res) == 3
    ids = set([x[0] for x in res])
    assert all([x in ids for x in fetch_ids])

    # test one of the keys does not exist not an error
    fetch_ids = ["vec0", "vec15", "does not exist"]
    res = movies.fetch(ids=fetch_ids)
    assert len(res) == 2

    # bad input
    with pytest.raises(vecs.exc.ArgError):
        movies.fetch(ids='should_be_a_list')
    

def test_delete(client: vecs.Client) -> None:
    n_records = 100
    dim = 384

    movies = client.create_collection(name = 'ping', dimension=dim)

    records = [
        (
            f"vec{ix}",
             vec,
             {
                 "genre": random.choice(["action", "rom-com", "drama"]),
                 "year": int(50*random.random()) + 1970
             }
        )
        for ix, vec in enumerate(np.random.random((n_records, dim)))
    ]

    # insert works
    movies.upsert(records)

    delete_ids = ["vec0", "vec15", "vec99"]
    movies.delete(ids=delete_ids)
    assert len(movies) == n_records - len(delete_ids)

    # bad input
    with pytest.raises(vecs.exc.ArgError):
        movies.delete(ids='should_be_a_list')

def test_repr(client: vecs.Client) -> None:
    movies = client.create_collection(name = 'movies', dimension=99)
    assert repr(movies) == 'vecs.Collection(name="movies", dimension=99)'
   

def test_getitem(client: vecs.Client) -> None:
    movies = client.create_collection(name = 'movies', dimension=3)
    movies.upsert(vectors=[("1", [1,2,3], {})])

    assert movies["1"] is not None
    assert len(movies["1"]) == 3
    
    with pytest.raises(KeyError):
        assert movies["2"] is not None


    with pytest.raises(vecs.exc.ArgError):
        movies[["only strings work not lists"]]


def test_query(client: vecs.Client) -> None:
    n_records = 100
    dim = 64 

    bar = client.create_collection(name = 'bar', dimension=dim)

    records = [
    (
        f"vec{ix}",
         vec,
         {
             "genre": random.choice(["action", "rom-com", "drama"]),
             "year": int(50*random.random()) + 1970
         }
    )
    for ix, vec in enumerate(np.random.random((n_records, dim)))
    ]

    bar.upsert(records)

    query_id, query_vec, query_meta = bar["vec5"]

    top_k = 7

    res = bar.query(
        query_vector = query_vec,
        top_k = top_k,
        filters = None,
        measure = 'cosine_distance',
        include_value = False,
        include_metadata = False
    )
    
    # correct number of results
    assert len(res) == top_k
    # most similar to self
    assert res[0] == 'vec5'

    with pytest.raises(vecs.exc.ArgError):
        res = bar.query(
            query_vector = query_vec,
            top_k = 101,
        )
    

    with pytest.raises(vecs.exc.ArgError):
        res = bar.query(
            query_vector = query_vec,
            top_k = top_k,
            measure='invalid'
        )

    # include_value
    res = bar.query(
        query_vector = query_vec,
        top_k = top_k,
        filters = None,
        measure = 'cosine_distance',
        include_value = True,
    )
    assert len(res[0]) == 2
    assert res[0][0] == 'vec5'
    assert pytest.approx(res[0][1]) == 0

    # include_metadata
    res = bar.query(
        query_vector = query_vec,
        top_k = top_k,
        filters = None,
        measure = 'cosine_distance',
        include_metadata = True,
    )
    assert len(res[0]) == 2
    assert res[0][0] == 'vec5'
    assert res[0][1] == query_meta
    

def test_query_filters(client: vecs.Client) -> None:
    n_records = 100
    dim = 4 

    bar = client.create_collection(name = 'bar', dimension=dim)

    records = [
        (f"0", [0, 0, 0, 0], {"year": 1990}),
        (f"1", [1, 0, 0, 0], {"year": 1995}),
        (f"2", [1, 1, 0, 0], {"year": 2005}),
        (f"3", [1, 1, 1, 0], {"year": 2001}),
        (f"4", [1, 1, 1, 1], {"year": 1985}),
        (f"5", [2, 1, 1, 1], {"year": 1863}),
        (f"6", [2, 2, 1, 1], {"year": 2021}),
        (f"7", [2, 2, 2, 1], {"year": 2019}),
        (f"8", [2, 2, 2, 2], {"year": 2003}),
        (f"9", [3, 2, 2, 2], {"year": 1997}),
    ]


    bar.upsert(records)

    query_rec = records[0]

    res = bar.query(
        query_vector = query_rec[1],
        top_k = 3,
        filters = {"year": {"$lt": 1990}},
        measure = 'cosine_distance',
        include_value = False,
        include_metadata = False
    )

    assert res

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            filters = ["wrong type"],
            measure = 'cosine_distance',
        )

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            # multiple keys
            filters = {"key1": {"$eq": "v"}, "key2": {"$eq": "v"}},
            measure = 'cosine_distance',
        )

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            # bad key
            filters = {1: {"$eq": "v"}},
            measure = 'cosine_distance',
        )

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            # and requires a list
            filters = {
                "$and": {"year": {"$eq": 1997}}
            },
            measure = 'cosine_distance',
        )

    # AND 
    assert len(bar.query(
        query_vector = query_rec[1],
        top_k = 3,
        # and requires a list
        filters = {
            "$and": [
                {"year": {"$eq": 1997}},
                {"year": {"$eq": 1997}},
            ]
        },
        measure = 'cosine_distance',
    )) == 1

    # OR 
    assert len(bar.query(
        query_vector = query_rec[1],
        top_k = 3,
        # and requires a list
        filters = {
            "$or": [
                {"year": {"$eq": 1997}},
                {"year": {"$eq": 1997}},
            ]
        },
        measure = 'cosine_distance',
    )) == 1

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            # bad value, too many conditions
            filters = {"year": {"$eq": 1997, "$neq": 1998}},
            measure = 'cosine_distance',
        )

    with pytest.raises(vecs.exc.FilterError):
        bar.query(
            query_vector = query_rec[1],
            top_k = 3,
            # bad value, unknown operator
            filters = {"year": {"$no_op": 1997}},
            measure = 'cosine_distance',
        )

    # neq 
    assert len(bar.query(
        query_vector = query_rec[1],
        top_k = 3,
        # and requires a list
        filters = {
            "year": {"$neq": 2000}
        },
        measure = 'cosine_distance',
    )) == 3
    
 
def test_access_index(client: vecs.Client) -> None:
    dim = 4 
    bar = client.create_collection(name = 'bar', dimension=dim)
    assert bar.index is None
   
 

def test_create_index(client: vecs.Client) -> None:
    dim = 4 
    bar = client.create_collection(name = 'bar', dimension=dim)

    bar.create_index(metadata_config={"indexed": ["foo"]})

    assert bar.index is not None

    with pytest.raises(vecs.exc.ArgError):
        bar.create_index(replace=False)

    with pytest.raises(vecs.exc.ArgError):
        bar.create_index(method="does not exist")

    with pytest.raises(NotImplementedError):
        bar.create_index(measure="does not exist")
     
    with pytest.raises(vecs.exc.ArgError):
        bar.create_index(method="does not exist")
     
    with pytest.raises(vecs.exc.ArgError):
        bar.create_index(metadata_config={"indexed": "wrong type"})

    with pytest.raises(vecs.exc.ArgError):
        bar.create_index(metadata_config={"indexed": [9]})














































