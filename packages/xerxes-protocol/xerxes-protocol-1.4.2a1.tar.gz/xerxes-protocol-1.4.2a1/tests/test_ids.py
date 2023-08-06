import pytest
import xerxes_protocol.ids as ids


class TestDevid:
    def test_type_1(self):
        id = ids.DevId(0xFF)
        assert bytes(id) == b"\xFF"
    
    
    def test_type_2(self):
        with pytest.raises(TypeError):
            id = ids.DevId(3.5)
    
    
    def test_type_3(self):
        id = ids.DevId(b"\xFF")
        assert bytes(id) == b"\xFF"
            
            
    def test_large(self):
        with pytest.raises(AssertionError):
            id = ids.DevId(256)
    
    
    def test_negative(self):
        with pytest.raises(AssertionError):
            id = ids.DevId(-1)
    
            
class TestMsgid:
    def test_type_1(self):
        id = ids.MsgId(0x01FF)
        assert bytes(id) == b"\xFF\x01"
    
    
    def test_type_2(self):
        with pytest.raises(TypeError):
            id = ids.DevId(3.5)
            
    
    def test_type_3(self):
        id = ids.MsgId(0x01FF)
        assert int(id) == 0x01FF
            
            
    def test_length_1(self):
        with pytest.raises(AssertionError):
            id = ids.DevId(0x10000)
            
        
    def test_length_2(self):
        with pytest.raises(AssertionError):
            id = ids.DevId(-1)
        
        
    def test_ack_ok(self):
        pid = ids.MsgId.ACK_OK
        assert bytes(pid) == b"\x02\x00"
