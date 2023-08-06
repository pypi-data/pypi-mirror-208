import vecs
import pytest 

def test_create_collection(client: vecs.Client) -> None:
    client.create_collection(name = 'docs', dimension=384)

    with pytest.raises(vecs.exc.CollectionAlreadyExists):
        client.create_collection(name = 'docs', dimension=384)

def test_get_collection(client: vecs.Client) -> None:

    with pytest.raises(vecs.exc.CollectionNotFound):
        client.get_collection(name = 'foo')

    client.create_collection(name = 'foo', dimension=384)

    foo = client.get_collection(name = 'foo')
    assert foo.name == 'foo'


def test_list_collections(client: vecs.Client) -> None:
    assert len(client.list_collections()) == 0
    client.create_collection(name = 'docs', dimension=384)
    client.create_collection(name = 'books', dimension=1586)
    collections = client.list_collections()
    assert len(collections) == 2

def test_delete_collection(client: vecs.Client) -> None:
    client.create_collection(name = 'books', dimension=1586)
    collections = client.list_collections()
    assert len(collections) == 1
    client.delete_collection('books')
    collections = client.list_collections()
    assert len(collections) == 0

    with pytest.raises(vecs.exc.CollectionNotFound):
        client.delete_collection('books')

