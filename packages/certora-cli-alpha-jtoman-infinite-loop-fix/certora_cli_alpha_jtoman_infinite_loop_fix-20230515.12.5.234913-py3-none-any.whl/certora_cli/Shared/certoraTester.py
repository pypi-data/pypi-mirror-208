from typing import Any, Dict, List, Optional, Tuple, Set
from tabulate import tabulate

errors = ""
warnings = ""
table = []  # type: List[List[str]]
violations_headers = ["Test name", "Rule", "Function", "Result", "Expected"]


def addError(errors: str, testName: str, rule: str, ruleResult: str,
             expectedResult: str = "",
             funcName: str = "") -> str:
    errors += "Violation in " + testName + ": " + rule
    if funcName != "":
        errors += ", " + funcName
    errors += " result is " + ruleResult + "."
    if expectedResult != "":
        errors += "Should be " + expectedResult
    errors += "\n"
    return errors


def print_table(headers: List[str]) -> None:
    print(tabulate(table, headers, tablefmt="psql"))


def findExpected(funcName: str, resultsList: Dict[str, List[str]]) -> str:
    expectedResult = "\033[33mundefined\033[0m"
    for result in resultsList.keys():
        if funcName in resultsList[result]:
            expectedResult = result
            break
    return expectedResult


def appendViolation(table: List[List[str]], testName: str, actualResult: str,
                    expectedResult: str,
                    ruleName: str = "", funcName: str = "") -> None:
    tableRow = []
    tableRow.append(testName)
    tableRow.append(ruleName)
    tableRow.append(funcName)
    tableRow.append(actualResult)
    tableRow.append(expectedResult)

    table.append(tableRow)


# compare jar results with expected
# @param rulesResults is a dictionary that includes all the rule names and
# their results from the jar output
# @param expectedRulesResults is a dictionary that includes all the rule names
# and their results from tester file
# @param assertMessages is a dictionary that includes all the rule names and
# their assertion messages
#        from the jar output
# @param expectedAssertionMessages is a dictionary that includes all the rule
# names and their assertion messages
#        from tester file
# @param test is a boolean indicator of current test (test==false <=> at least
# one error occurred)
def compareResultsWithExpected(
        test_name: str,
        rules_results: Dict[str, Any],
        expected_rules_results: Dict[str, Any],
        assert_messages: Dict[str, Any],
        expected_assertion_messages: Optional[Dict[str, Any]],
        test: bool = True
) -> bool:
    global errors
    global warnings

    violations: Set[Tuple] = set()

    if rules_results != expected_rules_results:
        # compare results in expected
        compare_results(rules_results, expected_rules_results, violations,
                        test_name)
        # check for rules that were expected but didn't got results
        find_not_existing_rules(expected_rules_results, rules_results,
                                violations, test_name)
    # if assertMessages field is defined (in tester)
    if expected_assertion_messages:
        test = compare_assert_messages(test_name, expected_assertion_messages,
                                       assert_messages, errors)
    for t in violations:
        appendViolation(table, *t)

    test = len(violations) == 0

    return test


def extract_nested_rules_status(nested_rule: Dict[str, List[str]]) -> str:
    if len(nested_rule['UNKNOWN']) > 0:
        return 'UNKNOWN'
    if len(nested_rule['TIMEOUT']) > 0:
        return 'TIMEOUT'
    if len(nested_rule['FAIL']) > 0:
        return 'FAIL'
    if len(nested_rule['SANITY_FAIL']) > 0:
        return 'SANITY_FAIL'
    return 'SUCCESS'


def find_not_existing_rules(expected_rules_results: Dict[str, Any],
                            rules_results: Dict[str, Any],
                            violations: Set[Tuple], test_name: str) -> None:
    rules_not_found = set(expected_rules_results) - set(rules_results)
    for r in rules_not_found:
        res = expected_rules_results[r]
        violations.add((test_name, "Rule not found in results.", res if
                        isinstance(res, str) else
                        extract_nested_rules_status(res), r))


def compare_results(results: Dict[str, Any], expected: Dict[str, Any],
                    violations: Set[Tuple], test_name: str) -> None:
    for rule, rule_result in results.items():
        if rule in expected.keys():
            expected_rule_result = expected[rule]
            if isinstance(rule_result, str):
                if isinstance(expected_rule_result, str):
                    # and the rule is flat in the expected as well
                    if rule_result != expected_rule_result:
                        # errors = addError(errors, testName, rule, ruleResult,
                        #  expectedRuleResult)
                        violations.add((test_name, rule_result,
                                        expected_rule_result, rule, ""))
                else:  # the rule is nested in the expected
                    nested_rule_res = extract_nested_rules_status(
                        expected_rule_result)
                    if rule_result != nested_rule_res:
                        # errors = addError(errors, testName, rule, ruleResult,
                        #  expectedRuleResult)
                        violations.add((test_name, rule_result,
                                        nested_rule_res, rule, ""))

            else:
                # nested rule ( ruleName: {result1: [functions list], result2:
                # [functions list] ... } )
                if isinstance(expected_rule_result, str):
                    # but the rule is not nested in the expected
                    nested_rule_res = extract_nested_rules_status(rule_result)
                    if nested_rule_res != expected_rule_result:
                        # errors = addError(errors, testName, rule, ruleResult,
                        #  expectedRuleResult)
                        violations.add((test_name, nested_rule_res,
                                        expected_rule_result, rule, ""))

                else:  # both rules are nested
                    for result, func_list in rule_result.items():
                        func_list.sort()
                        expected_rule_result[result].sort()

                        # compare functions lists (current results with
                        # expected)
                        if func_list != expected_rule_result[result]:
                            for func_name in func_list:
                                # if function appears in current results but
                                # does not appear in the expected ones
                                if func_name not in expected_rule_result[
                                        result]:
                                    # errors = addError(errors, testName, rule,
                                    #  result, "", funcName)
                                    # found results for an unexpected rule
                                    expected_result = findExpected(
                                        func_name, expected_rule_result)
                                    violations.add((test_name, result,
                                                    expected_result, rule,
                                                    func_name))
        else:
            result = (rule_result if isinstance(rule_result, str)
                      else "Object{" + ", ".join(rule_result.keys()) + "}")
            violations.add((test_name, result, "\033[33mundefined\033[0m",
                            rule, ""))
            # errors += testName + ", " + rule + " is not listed in 'rules'.
            #  Expected rules: " + \
            # ','.join(expectedRulesResults.keys()) + "\n"


def compare_assert_messages(test_name: str,
                            expected_assertion_messages: Dict[str, Any],
                            assert_messages: Dict[str, Any],
                            errors: str) -> bool:
    test = True
    for rule in expected_assertion_messages.keys():
        if rule not in assert_messages:
            # current rule is missing from 'assertMessages' section in current
            # results
            test = False
            errors += test_name + ", rule \"" + rule + \
                "\" does not appear in the output." + \
                "Please, remove unnecessary rules.\n"
        elif expected_assertion_messages[rule] != assert_messages[rule]:
            # assertion messages are different from each other
            test = False
            errors += test_name + ", rule \"" + rule + \
                "\": wrong assertion message. Got: \"" + \
                assert_messages[rule] + "\". Expected: \"" + \
                expected_assertion_messages[rule] + "\".\n"
    return test


def get_errors() -> str:
    return errors


def has_violations() -> bool:
    if table:
        return True
    else:
        return False


def get_violations() -> None:
    if table:
        print("Found violations:")
        print_table(violations_headers)
