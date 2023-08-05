from collections.abc import Sequence


class FrozenByteList(Sequence):
    def __init__(self, input_bytes, getter=None):
        self._data = input_bytes
        self.getter = getter
        self.element_count = int.from_bytes(input_bytes[:4], 'big')

    @classmethod
    def create(cls, byte_strings: list):
        num_elements = len(byte_strings)
        offsets = [0]
        for byte_string in byte_strings:
            offsets.append(offsets[-1] + len(byte_string))
        serialized_data = bytearray()
        serialized_data += num_elements.to_bytes(4, 'big')
        for offset in offsets:
            serialized_data += offset.to_bytes(4, 'big')
        for byte_string in byte_strings:
            serialized_data += byte_string
        return cls(bytes(serialized_data))

    def __len__(self):
        return self.element_count

    def get_offset(self, i: int):
        return int.from_bytes(
            self._data[4+i*4:4+((i+1)*4)], 'big')

    def __getitem__(self, index: int):
        if index < 0 or index >= self.element_count:
            raise IndexError('Invalid index %d' % index)
        start = self.get_offset(index)
        end = self.get_offset(index+1)
        data_start = self.element_count * 4 + 8
        element = self._data[data_start+start:data_start+end]
        if self.getter is None:
            return element
        return self.getter(element)

    def data(self):
        return self._data


def cached_binary_searcher(arr, cache_depth=8):
    cache = {}

    def binary_search(target):
        left = 0
        right = len(arr) - 1
        depth = 0
        while left <= right:
            mid = (left + right) // 2
            if depth < cache_depth:
                depth += 1
                current = cache.get(mid)
                if current is None:
                    current = arr[mid]
                    cache[mid] = current
            else:
                current = arr[mid]
            if current == target:
                return mid
            elif current < target:
                left = mid + 1
            else:
                right = mid - 1
        return None
    return binary_search
