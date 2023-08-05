def parse_str_to_list(s: str, only_float_list: bool = False):
    '''
        this function turns:
            - strings in the format '[1.3, 23.5, 12.4]' to a list of floats [1.3, 23.5, 12.4]
            - strings in the format '[hallo, hallo2, hallo3]' to a list of strings [hallo, hallo2, hallo3]
            - strings in another format stay the same string
        :param s: input string from csv
        :param only_float_list: if this flag is true an Exception will be raised when not parsable into a float list
        :return: parsed python datatype needed in model_data
    '''
    if s.startswith('[') and s.endswith(']'):
        try:
            # Try to split the string and convert each element to a float
            return [float(x) for x in s[1:-1].split(',')]
        except ValueError:
            if not only_float_list:
                try:
                    # If that fails, try to split the string and convert each element to a string
                    return [str(x).strip() for x in s[1:-1].split(',')]
                except ValueError:
                    # If that also fails, raise exception
                    raise Exception(
                        f'The entry ({s}) in the csv file cant be read. Vector with different datatypes used.')
            raise Exception(f'The entry ({s}) in the csv file cant be parsed into a float list.')
    else:
        # if no list: use normal string
        if only_float_list:
            raise Exception(f'The entry ({s}) in the csv file cant be parsed into a float list.')
        return s