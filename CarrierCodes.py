class CarrierCodes:
    def __init__(self, raw_codes):
        self.raw_codes = raw_codes
        
        if not self.is_valid_input():
            print("Invalid input ❌. Expected a dictionary.")
            self.raw_codes = {}

    def is_valid_input(self):
        return isinstance(self.raw_codes, dict)

    def organize(self):
        organized_codes = {}

        for carrier, codes in self.raw_codes.items():
            if isinstance(codes, str):
                codes_array = [code.strip() for code in codes.split(",")]
                organized_codes[carrier] = codes_array
            else:
                print(f"Invalid codes for carrier {carrier} ❌")
                organized_codes[carrier] = []

        return organized_codes

    def display(self):
        import json
        print(json.dumps(self.organize(), indent=4))


raw_codes = {
    "MCI": "0910, 0911, 0912, 0913, 0914, 0915, 0916, 0917, 0918, 0919, 0990, 0991, 0992, 0993, 0994, 0903",
    "IRANCEEL": "0930, 0933, 0935, 0936, 0937, 0938, 0939, 0900, 0901, 0902, 0903, 0904, 0905, 0941",
    "RIGHTEL": "0920, 0921, 0922"
}

carrier_codes = CarrierCodes(raw_codes)
carrier_codes.display()
