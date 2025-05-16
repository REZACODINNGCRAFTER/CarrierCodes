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

    def get_all_codes(self):
        all_codes = []
        for codes in self.organize().values():
            all_codes.extend(codes)
        return all_codes

    def get_codes_by_carrier(self, carrier_name):
        return self.organize().get(carrier_name.upper(), [])

    def find_carrier_by_code(self, search_code):
        for carrier, codes in self.organize().items():
            if search_code in codes:
                return carrier
        return None

    def count_codes_per_carrier(self):
        return {carrier: len(codes) for carrier, codes in self.organize().items()}

    def has_duplicate_codes(self):
        all_codes = self.get_all_codes()
        return len(all_codes) != len(set(all_codes))

    def get_duplicate_codes(self):
        from collections import Counter
        all_codes = self.get_all_codes()
        return [code for code, count in Counter(all_codes).items() if count > 1]

    def get_unique_codes(self):
        from collections import Counter
        all_codes = self.get_all_codes()
        return [code for code, count in Counter(all_codes).items() if count == 1]

    def carriers_with_no_codes(self):
        return [carrier for carrier, codes in self.organize().items() if not codes]

    def is_code_valid(self, code):
        return code in self.get_all_codes()


raw_codes = {
    "MCI": "0910, 0911, 0912, 0913, 0914, 0915, 0916, 0917, 0918, 0919, 0990, 0991, 0992, 0993, 0994, 0903",
    "IRANCEEL": "0930, 0933, 0935, 0936, 0937, 0938, 0939, 0900, 0901, 0902, 0903, 0904, 0905, 0941",
    "RIGHTEL": "0920, 0921, 0922"
}

carrier_codes = CarrierCodes(raw_codes)
carrier_codes.display()

print("\nAll codes:", carrier_codes.get_all_codes())
print("\nCodes for IRANCEEL:", carrier_codes.get_codes_by_carrier("IRANCEEL"))
print("\nCarrier for code '0903':", carrier_codes.find_carrier_by_code("0903"))
print("\nCount of codes per carrier:", carrier_codes.count_codes_per_carrier())
print("\nContains duplicate codes:", carrier_codes.has_duplicate_codes())
print("\nDuplicate codes:", carrier_codes.get_duplicate_codes())
print("\nUnique codes:", carrier_codes.get_unique_codes())
print("\nCarriers with no codes:", carrier_codes.carriers_with_no_codes())
print("\nIs code '0910' valid?:", carrier_codes.is_code_valid("0910"))
print("Is code '0999' valid?:", carrier_codes.is_code_valid("0999"))
