

def add_test_result(program, test_name, test_object, unique_key=None, unique_value=None):
    test_object['name'] = test_name
    if program.has_key('tests'):
        if program['tests'].has_key(test_object['result']):
            if not unique_key or not unique_value:
                program['tests'][test_object['result']].append(test_object)
            else:
                #remove possible duplicate
                for result_type in program['tests']:
                    for t in program['tests'][result_type]:
                        if t['name'] == test_name and t.has_key(unique_key) and t[unique_key] == unique_value:
                            program['tests'][result_type].remove(t)
                            program['tests'][test_object['result']].append(test_object)
                            return program
           
                program['tests'][test_object['result']].append(test_object)
        else:
            program['tests'][test_object['result']] = [test_object]
    else:
        program["tests"] = { test_object['result']: [test_object] }

    return program
