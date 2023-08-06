import hashlib

def password(pass_phrase, number=20, cssn="1111"):
    def divide_list(arr, number_of_subarray):
        sublist_size = len(arr) // number_of_subarray
        remainder = len(arr) % number_of_subarray
        subarrays = []
        start = 0
        end = 0
        for i in range(number_of_subarray):
            end = start + sublist_size
            if i < remainder:
                end += 1
            subarrays.append(arr[start:end])
            start = end
        return subarrays

    def shuffle_list(lst, seed_value=1):
        state = seed_value
        
        for i in range(len(lst) - 1, 0, -1):
            state = (state * 214013 + 2531011) % (2 ** 32)
            j = state % (i + 1)
            
            lst[i], lst[j] = lst[j], lst[i]
        
        return lst

    def hex_to_dec(hex_list):
        dec_list = []
        for hex_val in hex_list:
            dec_list.append(int(hex_val, 16))
        return dec_list

    def cutfill(string, number):
        if len(string) > number:
            string = string[:number]
        elif len(string) < number:
            m = number // len(string)
            n = number % len(string)
            string = string * m + string[:n]
        return string

    def get_range(lst, number):
        final_list = []
        supporter = 0
        for i in lst:
            supporter += i
            final_list.append(supporter % number)
        return final_list

    def return_list(num_list, char_list):
        final_list = []
        for num in num_list:
            final_list.append(char_list[num])
        return final_list
    cssn = str(cssn)
    if type(pass_phrase)!= str:
        raise TypeError("Pass phrase must be a string")
    if type(number)!= int:
        raise TypeError("Number must be an integer")
    if len(cssn)!= 4:
        raise ValueError("CSSN must be 4 digits if")
    total_ones = cssn.count('1')
    final_password_list = []
    char_list = []
    identifier = pass_phrase + str(number) + cssn
    hashed_value = cutfill(hashlib.sha256(identifier.encode()).hexdigest(), number)
    divided_list = divide_list(list(hashed_value), total_ones)
    
    if cssn[0] == '1':
        char_list.append(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    if cssn[1] == '1':
        char_list.append(list("abcdefghijklmnopqrstuvwxyz"))
    if cssn[2] == '1':
        char_list.append(list("0123456789"))
    if cssn[3] == '1':
        char_list.append(list("!@#$%^&*()_+-=[]{};:,./<>?"))
    
    for i in range(total_ones):
        num_lists = get_range(hex_to_dec(divided_list[i]), len(char_list[i]))
        for j in return_list(num_lists, char_list[i]):
            final_password_list.append(j)
    return "".join(shuffle_list(final_password_list,number))
