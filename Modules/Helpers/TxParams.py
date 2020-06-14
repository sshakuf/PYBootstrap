

class TxLocalParams:
    def __init__(self):
        self.output_mipi_test_ram = False  # needs to be in every instance (synth, tx and rx)


class TxSharedParams:
    def __init__(self):
        print("shared tx params")