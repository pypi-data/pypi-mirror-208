import numpy as np
from torchdata.datapipes import functional_datapipe
from torchdata.datapipes.iter import IterDataPipe
from torchdata.datapipes.map import MapDataPipe


@functional_datapipe("rolling")
class RollingWindow(IterDataPipe):
    """
    Usage ex:

    pipes.FileOpener(datapipe, mode='rt')
        .parse_csv(delimiter=',', skip_lines=1)
        .map(parse_price)
        .rolling(window_size=5, step=2)
        .batch(4)
    """
    def __init__(self, source_dp: IterDataPipe, window_size, step=1) -> None:
        super().__init__()
        self.source_dp = source_dp
        self.window_size = window_size
        self.step = step
    
    def __iter__(self):
        it = iter(self.source_dp)
        cur = []
        while True:
            try:
                while len(cur) < self.window_size:
                    cur.append(next(it))
                yield np.array(cur)
                for _ in range(self.step):
                    if cur:
                        cur.pop(0)
                    else:
                        next(it)
            except StopIteration:
                return
