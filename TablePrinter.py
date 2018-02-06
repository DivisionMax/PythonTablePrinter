import argparse


# Set-up the data stores
def print_vouchers(vouchers):
    # use the line_items and voucher objects
    if output_file:
        columns = int(headers.get('columns'))
        # seed the loop
        next_vouchers = get_items_to_print(columns, vouchers)
        while len(next_vouchers) > 0:
            # items are vertical
            for line in line_items:
                # iterate through each voucher and print the field value
                for i in range(len(next_vouchers)):
                    voucher = next_vouchers[i]
                    field = voucher.get(line)
                    if line == 'empty':
                        field = ' '
                    # column left padding
                    output_file.write(' ' * int(headers.get('left_margin')))
                    # create set widths
                    # write the data
                    output_file.write(field)
                    field_with_spacing = ' ' * (int(headers.get('column_width')) - len(field))
                    output_file.write(field_with_spacing)
                    # space the columns
                    column_spacing = ' ' * int(headers.get('column_spacing'))
                    output_file.write(column_spacing)
                output_file.write('\n')

            # space the rows
            row_spacing = '\n' * int(headers.get('row_spacing'))
            # get new items
            next_vouchers = get_items_to_print(columns, vouchers)
            if len(next_vouchers) > 0:
                output_file.write(row_spacing)
            else:
                output_file.close()
                break


def aggregate_voucher(voucher):
    name = voucher.get('description')
    if name in voucher_averages:
        count = voucher_averages.get(name)
        count += 1
        voucher_averages[name] = count
    else:
        voucher_averages[name] = 1


def validate_summaries(calc_averages, input_summaries):
    if input_summaries and calc_averages:
        if len(input_summaries) == len(calc_averages) and len(input_summaries) > 0:
            for summary in input_summaries:
                if summary in calc_averages:
                    if calc_averages.get(summary) == \
                            int(input_summaries[summary]['quantity']):
                        pass
                    else:
                        return False
                else:
                    return False
        else:
            return False
    else:
        return False
    return True


def get_items_to_print(columns, items):
    if len(items) == 0:
        response = []
    elif columns > len(items):
        response = [items.pop(0) for i in range(len(items))]
    else:
        response = [items.pop(0) for i in range(columns)]
    return response


def create_voucher(headers, voucher_data):
    # if the lengths are not equal, format will be incorrect
    voucher_data = [data.rstrip('\r\n') for data in voucher_data]
    return dict(zip(headers, voucher_data))


def main():
    are_vouchers = False
    line = input_file.readline().rstrip('\r\n')
    while line:
        if are_vouchers:
            if headers.get('voucher_fields'):
                voucher = create_voucher(headers.get('voucher_fields'), line.split(','))
                aggregate_voucher(voucher)
                vouchers.append(voucher)
        else:
            line_splt = line.split(':')
            if line_splt[0] == 'line_item':
                # Dynamically build the formatter
                line_items.append(line_splt[1])
            elif line_splt[0] == 'voucher_summary':
                # Build the voucher summary items
                voucher_summary = line_splt[1].split(',')
                voucher_summary_item = {
                    'description': voucher_summary[0],
                    'quantity': int(voucher_summary[1]),
                    'total_cost': float(voucher_summary[2])
                    }
                voucher_summaries[voucher_summary[0]] = voucher_summary_item
            elif line_splt[0] == 'voucher_fields':
                are_vouchers = True
                headers['voucher_fields'] = line_splt[1].split(',')
            else:
                headers[line_splt[0]] = line_splt[1]
        line = input_file.readline().rstrip('\r\n')
    if input_file:
        input_file.close()
    print('Voucher input is valid: {}'.format(validate_summaries(voucher_averages, voucher_summaries)))
    print_vouchers(vouchers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Accept an input file containing formatting descriptors and '
                                                 'a list of vouchers to output in the given format')
    parser.add_argument('input', type=str,
                        help='An input file containing the format descriptor and vouchers')
    args = vars(parser.parse_args())

    output_file = args.get('input')
    last_stop = args.get('input').rfind(".")
    output_file = args.get('input')[:last_stop] + '_result.txt'

    headers = {}
    vouchers = []  # [{}, {}..]
    line_items = []
    voucher_summaries = {}  # { '': {}, ..}
    voucher_averages = {}  # { '': <count>, ..}
    input_file = open(args.get('input'), 'r')
    output_file = open(output_file, 'w')

    main()
