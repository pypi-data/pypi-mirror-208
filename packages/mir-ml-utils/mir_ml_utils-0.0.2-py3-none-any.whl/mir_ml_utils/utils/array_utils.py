from typing import List, Any


def get_array_chunks_generator(data: List[Any], n: int):
    """Returns chucks of the given array.
    If len(data) % n != 0 then the last chunk
    will get all the remaining data

    Parameters
    ----------
    data: The data to create chunks
    n: The size of the chunk

    Returns
    -------
    A view of the chunk
    """
    # looping till length l
    for i in range(0, len(data), n):
        yield data[i:i + n]


def get_chunks(data: List[Any], n: int) -> List[List[Any]]:
    return list(get_array_chunks_generator(data=data,
                                           n=n))