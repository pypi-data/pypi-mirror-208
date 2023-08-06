from xerxes_protocol.memory import (
    uint64_t,
    uint32_t,
    uint16_t,
    uint8_t,
    float_t,
    double_t,
    MemoryElement,
)


class TestElemType:
    def test_memory_type_defaults(self):
        assert uint64_t._length == 8
        assert uint64_t._format == "Q"
        assert uint64_t._container == int

        assert uint32_t._length == 4
        assert uint32_t._format == "I"
        assert uint32_t._container == int

        assert uint16_t._length == 2
        assert uint16_t._format == "H"
        assert uint16_t._container == int

        assert uint8_t._length == 1
        assert uint8_t._format == "B"
        assert uint8_t._container == int

        assert float_t._length == 4
        assert float_t._format == "f"
        assert float_t._container == float

        assert double_t._length == 8
        assert double_t._format == "d"
        assert double_t._container == float
    

    def test_memory_element(self):
        me = MemoryElement(0, uint64_t, False)
        assert me.elem_addr == 0
        assert me.elem_type == uint64_t
        assert me.write_access is False
        assert me.can_write() is False
