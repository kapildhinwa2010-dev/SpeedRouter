import pytest
import torch
from speedrouter import SpeedRouter, create_speedrouter

class TestSpeedRouter:
    def test_init(self):
        m = SpeedRouter(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = SpeedRouter(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_speedrouter()
        assert isinstance(m, SpeedRouter)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
