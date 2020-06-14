
class SyntLocalParam:
    def __init__(self):
        self.can_logger_enable = 0
        self.output_mipi_test_ram = False  # needs to be in every instance (synth, tx and rx)


class SyntSharedParams:
    def __init__(self):
        print("synt shared params")
