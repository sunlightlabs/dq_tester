

def add_test_result(program, test_name, test_object):
    if program.has_key('tests'):
        if program['tests'].has_key(test_name):
            program['tests'][test_name].append(test_object)
        else:
            program['tests'][test_name] = [test_object]
    else:
        program["tests"] = { test_name: [test_object] }

    return program
