import copy
import dill
import re


class ParserException(Exception):
    pass


class Parser:
    def __init__(self, lexer=None, rules=None):
        self.lexer = None
        self.rules = {}

        if rules:
            self.add_rules(rules)

        if lexer:
            self.lexer = copy.copy(lexer)

    def add_rules(self, rules):
        pass

    def build(self):
        pass

    def save(self, filename="parser.p"):
        with open(filename, "wb") as file:
            dill.dump(self, file)

    def parse(self):
        pass

# ======================================================================================================================
# Rule formatting
# ======================================================================================================================


def format_rules(rules):
    """
    :param rules: rules are given in the following format
        rules = {
            'token': [
                ('keyword1 keyword2 keyword3', function),
                ('keyword4 keyword5', other_function)
            ]
            'other_token': [
                ...
            ],
            ...
        }
    :return: The return format is similar but strings of keywords have been replaced by lists of keywords and special
        symbols (such as ?) have been parsed to add corresponding rules
    """
    formatted_rules = {}

    for token, token_rules in rules.items():

        formatted_rules[token] = []
        for rule in token_rules:
            formatted_rules[token].extend(parse_rule(rule))

    return formatted_rules


def append_many(lists, element, at_sub_pos=None):
    for ls in lists:
        if at_sub_pos is not None:
            ls[at_sub_pos].append(element)
        else:
            ls.append(element)


def parse_rule(rule):
    """
    Parse a rule (pattern, function) by turning the pattern into a list of token and adjusts the function when the
    pattern has optional token (? operator)
    :param rule: A rule is a tuple with a pattern as string and a function
    :return:
    """

    pattern, fn = rule
    token_list = pattern.split()

    parsed_rule = [([], [])]

    for pos, token in enumerate(token_list):
        if not is_token_valid(token):
            raise ParserException('Parser only accepts token composed of letters, numbers and underscores')

        if token[-1] == "?":
            token = token[:-1]

            split_rule = copy.deepcopy(parsed_rule)
            append_many(split_rule, pos, at_sub_pos=1)
            append_many(parsed_rule, token, at_sub_pos=0)

            parsed_rule += split_rule

        else:
            append_many(parsed_rule, token, at_sub_pos=0)

    return [(pattern_as_list, spread_arguments_with_none(optional_pos, fn)) for pattern_as_list, optional_pos in
            parsed_rule]


def is_token_valid(token): return True if re.compile(r'^\w+\??$').match(token) else False


def spread_arguments_with_none(sorted_none_pos, fn):
    """
    :param sorted_none_pos: A list of position of argument which must be None
    :param fn: Any function
    :return: A new function that takes len(sorted_none_pos) more argument than fn, but which arguments at positions
             in sorted_none_pos are expected to be None
    """
    return (lambda *args: fn(*insert_none_at_positions(sorted_none_pos, args))) if sorted_none_pos else fn


def insert_none_at_positions(sorted_pos_list, list):
    """
    :param sorted_pos_list: The positions where None must be inserted, this list must be sorted
    :param list: The list of length >= max(sorted_pos_list) + len(sorted_pos_list)
    :return: A list but where None has been inserted at the given position provided
    """
    new_list = []
    pop_list_index = new_list_index = old_list_index = 0

    len_sorted_pos_list = len(sorted_pos_list)

    while pop_list_index < len_sorted_pos_list:
        next_element_pos = sorted_pos_list[pop_list_index]
        pop_list_index += 1

        while new_list_index != next_element_pos:
            new_list.append(list[old_list_index])
            old_list_index += 1
            new_list_index += 1

        new_list.append(None)
        new_list_index += 1

    return new_list + [arg for arg in list[old_list_index:]]
